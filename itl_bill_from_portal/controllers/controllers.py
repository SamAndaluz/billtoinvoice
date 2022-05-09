import base64
from re import A
import zipfile
import io
import json
import logging
import os
from contextlib import ExitStack

from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request, content_disposition
from odoo.tools.translate import _
from odoo.tools import image_process
from odoo.addons.web.controllers.main import Binary
from odoo.addons.documents.controllers.main import ShareRoute

import werkzeug
from werkzeug import urls
from werkzeug.exceptions import NotFound, Forbidden

from odoo import http, _
from odoo.http import request
from odoo.osv import expression
from odoo.tools import consteq, plaintext2html
from odoo.addons.mail.controllers.main import MailController
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError, UserError

logger = logging.getLogger(__name__)


def _check_special_access(res_model, res_id, token='', _hash='', pid=False):
    record = request.env[res_model].browse(res_id).sudo()
    if token:  # Token Case: token is the global one of the document
        token_field = request.env[res_model]._mail_post_token_field
        return (token and record and consteq(record[token_field], token))
    elif _hash and pid:  # Signed Token Case: hash implies token is signed by partner pid
        return consteq(_hash, record._sign_token(pid))
    else:
        raise Forbidden()

def _message_post_helper(res_model, res_id, message, token='', _hash=False, pid=False, nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread. We
        distinguish 2 cases:
            1/ If a token is specified, all logged in users will be able to write a message regardless
            of access rights; if the user is the public user, the message will be posted under the name
            of the partner_id of the object (or the public user if there is no partner_id on the object).

            2/ If a signed token is specified (`hash`) and also a partner_id (`pid`), all post message will
            be done under the name of the partner_id (as it is signed). This should be used to avoid leaking
            token to all users.

        Required parameters
        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        Optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param string hash: signed token by a partner if model uses some token field to bypass access right
                            post messages.
        :param string pid: identifier of the res.partner used to sign the hash
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].browse(res_id)

    # check if user can post with special token/signed token. The "else" will try to post message with the
    # current user access rights (_mail_post_access use case).
    if token or (_hash and pid):
        pid = int(pid) if pid else False
        if _check_special_access(res_model, res_id, token=token, _hash=_hash, pid=pid):
            record = record.sudo()
        else:
            raise Forbidden()

    # deduce author of message
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False

    # Token Case: author is document customer (if not logged) or itself even if user has not the access
    if token:
        if request.env.user._is_public():
            # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
            # TODO : Author must be Public User (to rename to 'Anonymous')
            author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
        else:
            if not author_id:
                raise NotFound()
    # Signed Token Case: author_id is forced
    elif _hash and pid:
        author_id = pid

    email_from = None
    if author_id and 'email_from' not in kw:
        partner = request.env['res.partner'].sudo().browse(author_id)
        email_from = partner.email_formatted if partner.email else None

    message_post_args = dict(
        body=message,
        message_type=kw.pop('message_type', "comment"),
        subtype_xmlid=kw.pop('subtype_xmlid', "mail.mt_comment"),
        author_id=author_id,
        **kw
    )

    # This is necessary as mail.message checks the presence
    # of the key to compute its default email from
    if email_from:
        message_post_args['email_from'] = email_from

    return record.with_context(mail_create_nosubscribe=nosubscribe).message_post(**message_post_args)

class ShareRoute(ShareRoute):

    def _portal_post_filter_params(self):
        return ['token', 'hash', 'pid']


    @http.route(['/vendor/post_files'], type='http', methods=['POST'], auth='public', website=True)
    def portal_post_bill(self, message=None, bill_file=None, from_date=None, to_date=None, spreedsheet_file=None, redirect=None, **kw):
        user_id = request.env['res.users'].sudo().browse(request.env.context.get('uid'))
        partner_id = user_id.partner_id
        url = redirect or (request.httprequest.referrer and request.httprequest.referrer + "#discussion") or '/my'

        if not bill_file:
            raise UserError("You must upload the bill.")
        if not spreedsheet_file:
            raise UserError("You must upload the spreedsheet.")

        if partner_id.child_ids:
            invoice_address_id = partner_id.child_ids.filtered(lambda p: p.type == 'invoice')
            if invoice_address_id:
                partner_id = invoice_address_id[0]

        Bills = request.env['account.move']
        bill_id = Bills.sudo().create({
            'partner_id': partner_id.id,
            'move_type': 'in_invoice',
            'period_from_date': from_date,
            'period_to_date': to_date
        })
        bill_id._onchange_partner_id()

        Attachments = request.env['ir.attachment']
        # Bill file
        bill_name = bill_file.filename
        bill_attachment = bill_file.read()
        bill_attachment_id = Attachments.sudo().create({
            'name':bill_name,
            'datas': base64.b64encode(bill_attachment),
            'res_model': 'mail.compose.message',
            'res_id': 0,
            'company_id': request.env.company.id,
        })
        # Spreedsheet
        spreedsheet_name = spreedsheet_file.filename
        spreedsheet_attachment = spreedsheet_file.read()
        spreedsheet_attachment_id = Attachments.sudo().create({
            'name':spreedsheet_name,
            'datas': base64.b64encode(spreedsheet_attachment),
            'res_model': 'mail.compose.message',
            'res_id': 0,
            'company_id': request.env.company.id,
            'itl_from_portal': True
        })

        attachment_ids = [bill_attachment_id.id, spreedsheet_attachment_id.id]
        if message or attachment_ids:
            res_model = 'account.move'
            res_id = bill_id.id
            # message is received in plaintext and saved in html
            if message:
                message = plaintext2html(message)
            post_values = {
                'res_model': res_model,
                'res_id': res_id,
                'message': message,
                'send_after_commit': False,
                'attachment_ids': False,  # will be added afterward
            }
            post_values.update((fname, kw.get(fname)) for fname in self._portal_post_filter_params())
            message = _message_post_helper(**post_values)

            if attachment_ids:
                # sudo write the attachment to bypass the read access
                # verification in mail message
                record = request.env[res_model].browse(res_id)
                message_values = {'res_id': res_id, 'model': res_model}
                attachments = record._message_post_process_attachments([], attachment_ids, message_values)

                if attachments.get('attachment_ids'):
                    message.sudo().write(attachments)

        return request.redirect(url)
