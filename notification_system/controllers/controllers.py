# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.osv.expression import AND

import json


class NotificationSystem(http.Controller):
    """
        Odoo URLs are CSRF-protected by default (when accessed with unsafe
        HTTP methods). See
        https://www.odoo.com/documentation/15.0/developer/reference/addons/http.html#csrf for
        more details.

        * if this endpoint is accessed through Odoo via py-QWeb form, embed a CSRF
        token in the form, Tokens are available via `request.csrf_token()`
        can be provided through a hidden input and must be POST-ed named
        `csrf_token` e.g. in your form add:

            <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>

        * if the form is generated or posted in javascript, the token value is
        available as `csrf_token` on `web.core` and as the `csrf_token`
        value in the default js-qweb execution context

        * if the form is accessed by an external third party (e.g. REST API
        endpoint, payment gateway callback) you will need to disable CSRF
        protection (and implement your own protection if necessary) by
        passing the `csrf=False` parameter to the `route` decorator.
    """

    @http.route('/notification/inbox/messages', auth='user', csrf=False)
    def render_notification(self, **kw):
        """
        """
        domain = [
            ('user_id', '=', int(request.env.user.id)), ('is_open', '=', False)
        ]
        # messages = request.env['notification.system'].sudo().search(
        #     domain, limit=5)

        # and is_open is false ==> this deleted from the query
        request.env.cr.execute("""
                               select message_id,name,description,url_redirect,model_id,model_name,is_open,type
                                from notification_system
                                where user_id = %s
                                order by create_date desc limit 5
                               """, [tuple([int(request.env.user.id)])])
        messages = request.env.cr.fetchall()
        response = {}
        messages_ = []
        notification_counter = 0

        # TODO: (Verification)????browse keep cache alive
        for message in messages:
            # Need to test the model_id depending on the model_name
            # to avoid the null value in the redirect url.
            check_record = 'True' if request.env[str(message[5])].sudo().search([
                ('id', '=', int(message[4]))
            ]) else 'False'

            check_request_rejected =  message[7]
            
            messages_.append(
                {
                    'message_id': message[0],
                    'name': message[1] if check_record == 'True' else message[1]+' (Service Request Deleted)',
                    'message': message[2],
                    'url_redirect': message[3],
                    'is_open': 'True' if message[6] else 'False',
                    'model_id_exists': check_record,
                    'is_request_rejected': check_request_rejected
                }
            )
            if not message[6]:
                notification_counter += 1

        response['response'] = messages_
        response['notification_counter'] = notification_counter
        response['counter'] = len(messages)
        try:
            return json.dumps(response)
        except Exception as exception:
            return str(exception)

    @ http.route('/notification/update/state', auth='user', csrf=False)
    def update_message_state(self, **kw):
        """
        """
        # do the action
        nofication = request.env['notification.system'].sudo().search([
            ('message_id', '=', kw['key'])
        ])
        if nofication:
            nofication.write({
                'is_open': True
            })
