from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    extra_cost_type = fields.Selection([('fixed','Fixed price'),('percentage','Percentage')], string="Extra cost type", help="The invoice lines of invoice created from bill will add the extra percentage or fixed price.")
    percentage = fields.Float(string="Percentage")
    fixed_price = fields.Float(string="Fixed price")
    invoice_partner_id = fields.Many2one('res.partner', string="Customer fo new invoice")
    invoice_product_id = fields.Many2one('product.product', string="Product for new invoice")

