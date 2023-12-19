# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    can_see_utilization_report = fields.Boolean(string='Can See Utilization Report', default=False)
    name = fields.Char(index=True, translate=True)

