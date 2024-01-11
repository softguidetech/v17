# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class IrModelInherit(models.Model):
    _inherit = 'ir.model'

    workflow_id = fields.Many2one('workflow.workflow')
