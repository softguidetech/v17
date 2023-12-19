# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    assignment_advisor_id = fields.Many2one(related='company_id.assignment_advisor_id', readonly=False)
    digital_solution__id = fields.Many2one(related='company_id.digital_solution__id', readonly=False)
