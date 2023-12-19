# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProjectDeliverable(models.Model):
    _name = 'thiqah.project.deliverable'
    _description = 'Thiqah Project Deliverable'

    # sequence = fields.Char(string='Deliverable Number', required=True,
    #                        readonly=True, default=lambda self: _('New'))
    deliverable_number = fields.Char()

    name = fields.Char()
    progress_percent = fields.Float('Progress Percent')

    due_date = fields.Date('Due Date')
    delivered_date = fields.Date('Delivered Date')

    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ])

    # Relation
    project_id = fields.Many2one('project.project', readonly=True)

    # @api.model
    # def create(self, vals):
    #     """
    #     override the create method to add sequence processing.
    #     """
    #     if vals.get('sequence', _('New')) == _('New'):
    #         vals['sequence'] = self.env['ir.sequence'].next_by_code(
    #             'seq_project_deliverable') or _('New')
    #     res = super(ProjectDeliverable, self).create(vals)
    #     return res
