# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ImpactUnit(models.Model):
    _name = 'freelance.impact.unit'
    _description = 'Freelance Impacted Unit'

    request_id = fields.Many2one('freelance.request', string='Freelance Request')
    department_id = fields.Many2one('hr.department', string='Department')
    operation = fields.Text(string='Functions will be performed')