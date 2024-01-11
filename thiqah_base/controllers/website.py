# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers import main

"""
Monkey Patch(s)
"""


class WebsiteMain(main.Website):

    @http.route(auth='public')
    def index(self, **kw):
        result = super(WebsiteMain, self).index()
        if request.env.user._is_public():
            return request.redirect('/web/login')
        return result

    def _login_redirect(self, uid, redirect=None):
        """ Redirect regular users (employees) to the backend and others to
            the frontend.
        """
        if not redirect and request.params.get('login_success'):
            user_id = request.env.user.id
            redirect = '/my/home_page'
            if redirect:
                # Inject in the Auditlog to trace the login action(s).
                # Just create a new record auditlog.login
                traceability_values = {
                    'user_id': user_id,
                    'redirect_to': redirect,
                    'user_category_id': request.env['res.users'].sudo().browse([int(user_id)]).thiqah_category_id if request.env['res.users'].sudo().browse([int(user_id)]) else 0
                }
                request.env['auditlog.login'].sudo().create(traceability_values)
        return super()._login_redirect(uid, redirect=redirect)
