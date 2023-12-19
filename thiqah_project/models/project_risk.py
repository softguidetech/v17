# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ProjectRisk(models.Model):
    _name = 'thiqah.project.risk'
    _description = 'Thiqah Project Risk'

    risk_number = fields.Char()
    name = fields.Char()
    description = fields.Text('Description')
    owner = fields.Char('Owner')
    corrective_action = fields.Text('Corrective action / Mitigation')
    level_impact = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ])
    risk_status = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ])

    risk_type_id = fields.Many2one('thiqah.project.risk.type')
    project_id = fields.Many2one('project.project',readonly=True)
