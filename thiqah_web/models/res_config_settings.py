

import re
import json
import logging

from lxml import etree

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    binary_max_size = fields.Integer(
        string='File Size Limit',
        required=True,
        default=20, config_parameter='web.max_file_upload_size',
        help="""Maximum allowed file size in megabytes""")

    supported_types = fields.Char(
        string='Supported Types',
        required=True,
        default='*', config_parameter='web.binary_supported_types'
    )

    # ----------------------------------------------------------
    # Functions
    # ----------------------------------------------------------

#     def set_values(self):
#         res = super(ResConfigSettings, self).set_values()
#         param = self.env['ir.config_parameter'].with_user(self.env.ref('base.user_admin'))
#         param.set_param('thiqah_web.binary_max_size', self.binary_max_size)
#         param.set_param('thiqah_web.binary_supported_types', self.supported_types)
#         return res
#
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSettings, self).get_values()
#         params = self.env['ir.config_parameter'].with_user(self.env.ref('base.user_admin'))
#         res.update(binary_max_size=int(params.get_param('thiqah_web.binary_max_size', 25)),binary_supported_types=params.get_param('thiqah_web.binary_supported_types', '*'))
#         return res
