# -*- coding: utf-8 -*-

from odoo import models, fields


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    business_unit = fields.Selection([('thiqah', 'THIQAH'), ('ahad', 'AHAD')], string='Entity')
