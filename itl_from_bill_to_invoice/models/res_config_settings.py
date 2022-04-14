from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    extra_cost_type = fields.Selection([('fixed','Fixed price'),('percentage','Percentage')], related="company_id.extra_cost_type", string="Extra cost type", help="The invoice lines of invoice created from bill will add the extra percentage or fixed price.", readonly=False)
    percentage = fields.Float(string="Percentage", related="company_id.percentage", readonly=False)
    fixed_price = fields.Float(string="Fixed price", related="company_id.fixed_price", readonly=False)
    invoice_partner_id = fields.Many2one('res.partner', related="company_id.invoice_partner_id", string="Customer fo new invoice", readonly=False)
    invoice_product_id = fields.Many2one('product.product', related="company_id.invoice_product_id", string="Product for new invoice", readonly=False)