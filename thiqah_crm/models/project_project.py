# -*- coding:utf-8 -*-

from odoo import models, fields


class ProjectProjectCrm(models.Model):
    _inherit = 'project.project'

    lead_id = fields.Many2one(
        'crm.lead'
    )
