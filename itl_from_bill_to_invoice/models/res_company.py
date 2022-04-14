from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    

    def get_invoice_product(self):
        product_comision_id = self.env.ref('itl_from_bill_to_invoice.product_comision')
        if product_comision_id:
            return product_comision_id.id
        else:
            return False

    extra_cost_type = fields.Selection([('fixed','Fixed price'),('percentage','Percentage')], string="Extra cost type", help="The invoice lines of invoice created from bill will add the extra percentage or fixed price.")
    percentage = fields.Float(string="Percentage")
    fixed_price = fields.Float(string="Fixed price")
    invoice_partner_id = fields.Many2one('res.partner', string="Customer fo new invoice")
    invoice_product_id = fields.Many2one('product.product', string="Product for new invoice", default=get_invoice_product)