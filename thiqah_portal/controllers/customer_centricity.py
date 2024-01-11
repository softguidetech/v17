# -*- encoding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from ...thiqah_base.controllers import thiqah_portal


class customerCentricityController(thiqah_portal.ThiqahPortal):

    @http.route('/customer/centricity', type='http', auth='user', website=True)
    def render_ceo_dashboard(self):
        if not self.can_access_route('customer_centricity'):
            return request.redirect('/access/access_denied')
        values = {}
        return request.render('thiqah_portal.customer_centricity')
