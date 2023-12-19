# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectDeparment(models.Model):
    _name = 'thiqah_project.project_department'
    _inherit = 'hr.department'
    _description = 'Thiqah Project Department'

    email = fields.Char()
    partner_id = fields.Many2one('res.partner')
