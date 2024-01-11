# -*- coding: utf-8 -*-

from odoo import models, fields


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    irequest_user_id = fields.Many2one('res.users', string='Inquiry request Responsible')
