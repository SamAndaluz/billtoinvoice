from odoo import api, models, fields
from odoo.exceptions import AccessError
from odoo.http import request

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    itl_from_portal = fields.Boolean(string="From Portal")