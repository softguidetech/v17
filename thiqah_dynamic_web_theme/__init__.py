# -*- coding: utf-8 -*-
from . import models
from odoo import api, SUPERUSER_ID


def _uninstall_reset_changes(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['web_editor.assets'].reset_asset(
        '/thiqah_dynamic_web_theme/static/src/scss/colors.scss', 
        'web._assets_primary_variables'
    )