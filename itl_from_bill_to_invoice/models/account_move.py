from email.policy import default
from operator import inv
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def create_customer_invoice(self):
        journal_id = self.with_context(default_type='out_invoice',default_journal_id=False)._get_default_journal()

        vals = {
            'type': 'out_invoice',
            'journal_id': journal_id.id,
            #'l10n_mx_edi_payment_method_id': self.partner_id.itl_payment_method_id.id if self.partner_id.itl_payment_method_id else False,
            #'l10n_mx_edi_usage': self.partner_id.itl_usage,
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id if self.partner_id.property_payment_term_id else False,
            'invoice_line_ids': [],
            'line_ids': []
        }
        invoice_id = self.copy(default=vals)
        
        products = []
        for line in self.invoice_line_ids:
            vals = {'product_id': line.product_id.id, 'quantity': line.quantity, 'price_unit': abs(line.price_unit), 'tax_ids': []}
            products.append((0, 0, vals))
        
        invoice_id.invoice_line_ids = products
        price_unit = 0
        partner_id = False

        if not invoice_id.partner_id.extra_cost_type and not self.company_id.extra_cost_type:
            raise ValidationError("There is not extra cost type selected in partner nor settings. Please select one.")

        if not invoice_id.partner_id.invoice_partner_id and not self.company_id.invoice_partner_id:
            raise ValidationError("There is not customer for new invoice selected in partner nor settings. Please select one.")

        if not invoice_id.partner_id.invoice_product_id and not self.company_id.invoice_product_id:
            raise ValidationError("There is not product for new invoice selected in partner nor settings. Please select one.")

        if invoice_id.partner_id.extra_cost_type:
            partner_id = invoice_id.partner_id.invoice_partner_id
            product_comision_id = invoice_id.partner_id.invoice_product_id.id
            if invoice_id.partner_id.extra_cost_type == 'fixed':
                price_unit = invoice_id.partner_id.fixed_price
            else:
                if invoice_id.partner_id.percentage == 0:
                    raise ValidationError("The percentage value must be greater than 0.")
                price_unit = self.amount_untaxed  * invoice_id.partner_id.percentage/100
        else:
            partner_id = self.company_id.invoice_partner_id
            product_comision_id = self.company_id.invoice_product_id.id
            if self.company_id.extra_cost_type == 'fixed':
                price_unit = self.company_id.fixed_price
            else:
                if self.company_id.percentage == 0:
                    raise ValidationError("The percentage value must be greater than 0.")
                price_unit = self.amount_untaxed  * self.company_id.percentage/100

        invoice_id.invoice_line_ids = [(0, 0, {'product_id': product_comision_id, 'quantity': 1, 'price_unit': price_unit})]
        invoice_id.partner_id = partner_id

        action = {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice_id.id,
        }

        return action