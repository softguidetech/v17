# -*- coding: utf-8 -*-

from odoo import fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_oauth_microsoft_enabled = fields.Boolean(
        'Allow users to sign in with Microsoft', default=True)
    auth_oauth_microsoft_client_id = fields.Char(
        'Client ID'
    )
