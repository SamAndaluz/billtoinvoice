# -*- coding: utf-8 -*-
# from odoo import http


# class ItlFromBillToInvoice(http.Controller):
#     @http.route('/itl_from_bill_to_invoice/itl_from_bill_to_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_from_bill_to_invoice/itl_from_bill_to_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_from_bill_to_invoice.listing', {
#             'root': '/itl_from_bill_to_invoice/itl_from_bill_to_invoice',
#             'objects': http.request.env['itl_from_bill_to_invoice.itl_from_bill_to_invoice'].search([]),
#         })

#     @http.route('/itl_from_bill_to_invoice/itl_from_bill_to_invoice/objects/<model("itl_from_bill_to_invoice.itl_from_bill_to_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_from_bill_to_invoice.object', {
#             'object': obj
#         })
