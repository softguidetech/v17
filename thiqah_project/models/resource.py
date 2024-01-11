# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ProjectResource(models.Model):
    _inherit = 'resource.resource'
    _name = 'thiqah.project.resource'
    _description = 'Thiqah Project Resource'

    resource_number = fields.Char()
    department_id = fields.Many2one('hr.department')
    other_resource = fields.Char()

    project_id = fields.Many2one('project.project', readonly=True)
