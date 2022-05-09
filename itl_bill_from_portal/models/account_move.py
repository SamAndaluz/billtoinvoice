from ast import literal_eval

from odoo import models, fields, api, exceptions


class AccountMove(models.Model):
    _inherit = 'account.move'


    period_from_date = fields.Date(string="From Date")
    period_to_date = fields.Date(string="To Date")