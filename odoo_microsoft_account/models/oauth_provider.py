# -*- coding: utf-8 -*-

import urllib
import simplejson
from odoo.http import request
from odoo import fields, models
import requests
import logging
_logger = logging.getLogger(__name__)

class AuthOauthProvider(models.Model):
    """Class defining the configuration values of an OAuth2 provider"""

    _inherit = 'auth.oauth.provider'

    secret_key = fields.Char('Secret Key')

    def oauth_token(
            self, type_grant, oauth_provider_rec, code=None,
            refresh_token=None, context=None):
        data = dict(
            grant_type=type_grant,
            redirect_uri=request.env['ir.config_parameter'].sudo().get_param(
                'web.base.url') + '/auth_oauth/microsoft/signin',
            client_id=oauth_provider_rec.client_id,
            client_secret=oauth_provider_rec.secret_key,
        )
        headers = {"content-type": "application/x-www-form-urlencoded"}
        if code:
            data.update({'code': code})
        elif refresh_token:
            data.update({'refresh_token': refresh_token})
        req = requests.post(oauth_provider_rec.validation_endpoint, data=data, headers=headers)
        content = req.json() 
        return content
    