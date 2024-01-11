# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, route


class CustomerPortalInherit(CustomerPortal):

    @route(['/my', '/', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        redirect = '/my/home_page'
        return request.redirect(redirect)
