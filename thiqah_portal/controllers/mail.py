# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

from werkzeug.exceptions import NotFound, Forbidden

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.mail import _check_special_access, PortalChatter
from odoo.tools import plaintext2html, html2plaintext


class ThiqahPortalChatter(PortalChatter):

    @http.route(['/mail/chatter_post'], type='json', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        result = super(ThiqahPortalChatter, self).portal_chatter_post(
            res_model, res_id, message, **kw)

        if res_model == 'thiqah.project.service.request':

            # avoid browse() | cache | cause
            record_id = request.env[res_model].sudo().search([
                ('id', '=', int(res_id))
            ])
            if record_id.need_to_be_approved:
                # any comment will be considered as justification.

                message = request.env['mail.message'].sudo().search([
                    ('id', '=', int(result['default_message_id']))
                ])
                if request.env.user.has_group('thiqah_project.thiqah_hr_group'):
                    message.write({
                        'for_approve_reject': True
                    })

        return result
