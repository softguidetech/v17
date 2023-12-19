# -*- coding: utf-8 -*-

from odoo import models


class AahdCrmSource(models.Model):
    _name = 'thiqah.aahd.source'
    _inherit = 'utm.source'
    _description = 'Thiqah Aahd Source'

    """there is no need to re develop this model . Just a little inheritance from the utm.source"""

