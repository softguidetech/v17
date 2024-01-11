# -*- coding: utf-8 -*-
from odoo import http

from odoo.addons.web.controllers import main


class CustomDataSet(main.DataSet):
    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        return self._call_kw(model, method, args, kwargs)
