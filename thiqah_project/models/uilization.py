# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class ProjectUtilization(models.Model):
    _name = 'thiqah.project.utilization'
    _description = 'Thiqah Project Utilization'

    # sequence = fields.Char(string='Utilization Number', required=True,
    #                        readonly=True, default=lambda self: _('New'))

    utilization_number = fields.Char()

    planned_hours = fields.Integer('Planned Hours')
    actual_hours = fields.Integer('Actual Hours')
    forecasted_hours = fields.Integer('Forecasted Hours')

    project_id = fields.Many2one('project.project',readonly=True)

    # @api.model
    # def create(self, vals):
    #     """
    #     override the create method to add sequence processing.
    #     """
    #     if vals.get('sequence', _('New')) == _('New'):
    #         vals['sequence'] = self.env['ir.sequence'].next_by_code(
    #             'thiqah_project_utilization') or _('New')
    #     res = super(ProjectUtilization, self).create(vals)
    #     return res
