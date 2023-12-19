# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class WorkflowState(models.Model):
    _name = 'workflow.state'
    _description = 'Odoo Workflow State'

    _sql_constraints = [
        ('uniq_name', 'CHECK(1=1)', _("State name must be unique.")),
    ]

    name = fields.Char('Name', required=True)
    technical_name = fields.Char('Technical name', required=True)
    workflow_id = fields.Many2one('workflow.workflow', string='Workflow')

    flow_start = fields.Boolean(string='Workflow start', default=False)
    flow_end = fields.Boolean(string='Workflow end', default=False)
    is_visible = fields.Boolean('Is Visible')
    is_approved = fields.Boolean('Is Approved')

    out_transition_ids = fields.One2many(
        'workflow.transition', 'state_from', string='Out Transition links')
    in_transition_ids = fields.One2many(
        'workflow.transition', 'state_to', string='In Transition links')

    def name_get(self):
        result = []
        for state in self:
            name = state.name + '(' + state.technical_name + ')'
            result.append((state.id, name))
        return result

    def create(self, vals_list):
        if vals_list and 'technical_name' in vals_list[0]:
            exists = self.search([('name', '=', vals_list[0]['technical_name'])])
            if exists:
                raise ValidationError(
                    "State technical name must be unique.This information is already in use in another workflow.")
            # vals_list[0]['name'] = vals_list[0]['name'].capitalize()
        return super().create(vals_list)
