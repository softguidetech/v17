# -*- coding: utf-8 -*-
from odoo import models, fields


class WorkflowCriterias(models.Model):
    _name = 'workflow.criteria'
    _description = 'Workflow Criteria'

    model = fields.Char('Model Name')
    criteria = fields.Char('Criteria')
    criteria_id = fields.Integer(help='Model ID')
    technical_name = fields.Char('Technical Name')

    workflow_id = fields.Many2one(
        'workflow.workflow', string='Workflow')

    is_linked = fields.Boolean(default=False)

    department_id = fields.Many2one(
        'hr.department', help='List contains all departments.', compute='_compute_department_id')

    def _compute_department_id(self):
        for record in self:
            criteria_id = record.criteria_id
            if criteria_id:
                # get the catalog
                # even internal , we use sudo()
                # also we use search not browse(risk of cache)
                catalog_id = self.env['thiqah_project.service_catalog'].sudo().search([
                    ('id', '=', int(criteria_id))
                ])
                record.department_id = catalog_id.department_id
            else:
                record.department_id = False