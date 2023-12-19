# -*- coding: utf-8 -*-
# from odoo import http


# class ExternalCommunication(http.Controller):
#     @http.route('/external_communication/external_communication', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/external_communication/external_communication/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('external_communication.listing', {
#             'root': '/external_communication/external_communication',
#             'objects': http.request.env['external_communication.external_communication'].search([]),
#         })

#     @http.route('/external_communication/external_communication/objects/<model("external_communication.external_communication"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('external_communication.object', {
#             'object': obj
#         })
