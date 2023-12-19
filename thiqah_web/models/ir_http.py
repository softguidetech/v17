# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, http, models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        info = super().session_info()
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        max_file_upload_size = int(IrConfigSudo.get_param('web.max_file_upload_size'))
        binary_supported_types = IrConfigSudo.get_param('web.binary_supported_types')
        
        info['max_file_upload_size']=max_file_upload_size*1024*1024
        info['binary_supported_types']=binary_supported_types or '*'
        return info