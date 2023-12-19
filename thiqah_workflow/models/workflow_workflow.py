# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError


class Workflow(models.Model):
    _name = 'workflow.workflow'
    _description = 'Odoo Workflow'

    _sql_constraints = [
        ('uniq_name',  'CHECK(1=2)', _("Workflow name must be unique.")),
        ('uniq_model',  'CHECK(1=1)', _("Model must be unique.")),
    ]

    name = fields.Char('Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model')
    state_ids = fields.One2many('workflow.state', 'workflow_id', string='States')
    action_ids = fields.One2many( 'workflow.action', 'workflow_id', string='Actions')
    transition_ids = fields.One2many('workflow.transition', 'workflow_id')
    active = fields.Boolean(string='Active', default=True)
    criteria_ids = fields.One2many('workflow.criteria', 'workflow_id')
    workflow_records = fields.Char()
    is_stateful = fields.Boolean(
        default=False, compute='_compute_is_stateful', store=True)
    relationship_model_ids = fields.Many2many('ir.model', 'worklfow_relationship_model_rel',
                                              'workflow_id', 'model_id', string='Criterias models')
    # compute='_comupte_relationship_models')
    records_ids = fields.Char(compute='_compute_records_criteria')

    # Purpose : HR process.
    # + Instead of a complete module, we add just the field 'for_hr'.
    for_hr = fields.Boolean(
        default=False, help='This field inject the sequence criteria in the default process.')

    def unlink(self):
        for workflow in self:
            if workflow.workflow_records:
                raise UserError(
                    "You cannot delete this workflow.\nThere are records linked to it.")
            for criteria_ in workflow.criteria_ids:
                criteria_.unlink()
        return super().unlink()

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            field_get = self.env[self.model_id.model].fields_get(allfields=[
                'state'])

            selection_items = field_get['state']['selection'] if 'state' in field_get else False

            # (2, id, 0)
            # removes the record of id id from the set, then deletes it (from the database). Can not be used in create().
            # command = [(2, id) for id in self.state_ids.ids]
            command = []
            if selection_items and len(selection_items):
                flow_start = True
                for item in selection_items:
                    # adds a new record created from the provided value dict.
                    command.append(
                        (0, 0,
                         {'technical_name': item[0],
                             'name': item[1], 'flow_start': flow_start}
                         )
                    )
                    if flow_start:
                        flow_start = False

            # onchange method returns pseudo-records which do not exist in the database yet. So, the best way is to use update().
            self.update(
                {'state_ids': command}
            )

            # (5, 0, 0)
            # removes all records from the set, equivalent to using the command 3 on every record explicitly. Can not be used in create().
            command = [(5,)]

            # We will filter based on the mode {primary,extension}
            # Purpose : That it's an interesting feature of the views inheritance that I like to call it view inheritance by prototype.
            # https://www.odoo.com/forum/help-1/field-name-mode-primary-field-can-anyone-explain-the-purpose-of-this-104612

            buttons = []
            for element in self.model_id.view_ids.filtered(lambda view_id: view_id.type == 'form' and view_id.mode == 'primary'):
                arch = etree.XML(element.arch_db)
                buttons = arch.xpath("//form/header/button")

            for element in self.model_id.view_ids.filtered(lambda r: r.type == 'form' and r.mode == 'extension'):
                arch = etree.XML(element.arch_db)
                buttons = arch.xpath("//button")

            # fetching buttons.
            for button in buttons:
                record = (0, 0,
                          {
                              'name': button.get('name'),
                              'type': button.get('type'),
                              'description': button.get('string')
                          })
                if record not in command:
                    command.append(record)

            self.update({'action_ids': command})

    @api.model_create_multi
    def create(self, vals_list):
        """
        Delete the useful criteria.
        """
        result = super(Workflow, self).create(vals_list)

        for criteria_ in self.env['workflow.criteria'].search([]):
            if criteria_.workflow_id.id not in self.search([]).ids:
                criteria_.unlink()
            else:
                criteria_.write({
                    'is_linked': True
                })

        return result

    @api.depends('state_ids')
    def _compute_is_stateful(self):
        for workflow in self:
            if workflow.state_ids:
                workflow.write({'is_stateful': True})
            else:
                workflow.write({'is_stateful': False})

    @api.depends('criteria_ids')
    def _compute_records_criteria(self):
        for workflow in self:
            if workflow.criteria_ids:
                criterias = []
                for criteria in workflow.criteria_ids:
                    criterias.append({
                        'workflow': workflow.name,
                        'technical_name': criteria.technical_name,
                        'criteria': criteria.criteria
                    })
            workflow.records_ids = criterias

    @api.onchange('relationship_model_ids')
    def _onchange_relationship_model_ids(self):
        workflow_criteria_ids = []
        for workflow in self:
            if workflow.relationship_model_ids:
                res = self.env['workflow.criteria']
                for model in workflow.relationship_model_ids:
                    _model = self.env[model.model].sudo()
                    workflow_criteria = self.env['workflow.criteria'].sudo()
                    for rec in _model.search([]):
                        criteria_ids = workflow_criteria.search(
                            [
                                ('criteria_id', '=', rec.id),
                                ('workflow_id', 'in', self.sudo().search([]).ids),
                                ('technical_name', '=', model.model)
                            ], limit=1)
                        if not criteria_ids:
                            res += workflow_criteria.new(
                                {
                                    'model': rec._description,
                                    'criteria': rec.name_get()[0][1],
                                    'technical_name': rec._name,
                                    'criteria_id': rec.id,
                                }
                            )
                workflow.criteria_ids = res
            else:
                workflow.write({'criteria_ids': False})

    # @api.onchange('criteria_ids')
    def _onchange_criteria_ids(self):
        for workflow in self:
            criterias = []
            for criteria in workflow.criteria_ids:
                criterias.append({
                    'workflow': workflow.name,
                    'technical_name': criteria.technical_name,
                    'criteria': criteria.criteria
                })

    # In the case we will reset the states
    def initialize_global_state(self):
        for workflow in self:
            # unlink each state from the current workflow engine and from the concerned model to avoid the side efects.
            for state in workflow.state_ids:
                state.unlink()

            workflow.is_stateful = True

            # Each record of the affected model retains the current state, so we need the reset:
            # if this workflow engine becomes stateless
            if not workflow.state_ids:
                concerned_model = self.env[workflow.model_id.model].sudo().search([
                ])
                if concerned_model:
                    if 'state' in concerned_model._fields:
                        for record in concerned_model:
                            record.write({
                                'state': None
                            })

    def btn_reload_workflow(self):
        from odoo.addons import thiqah_workflow
        return thiqah_workflow.update_workflow_reload(self)

    def flatten_list(self, _2d_list):
        flat_list = []
        # Iterate through the outer list
        for element in _2d_list:
            if type(element) is list:
                # If the element is of type list, iterate through the sublist
                for item in element:
                    flat_list.append(item)
            else:
                flat_list.append(element)
        return flat_list

    def mapping_records_criterias(self):
        for workflow in self:
            if workflow.model_id:
                criterias = []
                for criteria in workflow.criteria_ids:
                    criterias.append({
                        'workflow': workflow.name,
                        'technical_name': criteria.technical_name,
                        'criteria': criteria.criteria
                    })
                # get the field_name(s) from ir.model.fields depedning from the technical_name
                fields_criteria = []
                current_model = self.env[workflow.model_id.model].sudo()
                if criterias:
                    for criteria in criterias:
                        data = self.env['ir.model.fields'].sudo().search([
                            ('model', '=', current_model._name),
                            ('relation', '=', criteria['technical_name']),
                            ('ttype', '=', 'many2one')
                        ], limit=1).name
                        fields_criteria.append(
                            (data, criteria['criteria'])
                        )
                        criteria['field_name'] = data
                fields_criteria = set(fields_criteria)
                fields_criteria = list(fields_criteria)

                # get the data sufficient for the conditions mentioned
                # prepare the domain
                domains = []
                for field_criteria in fields_criteria:
                    if field_criteria[0] and field_criteria[1]:
                        domains.append((field_criteria[0], '=', field_criteria[1]))
                workflow_records = []
                for domain in domains:
                    workflow_records.append(
                        current_model.sudo().search([domain]).ids)
                workflow_records = self.flatten_list(workflow_records)
                workflow.write({'workflow_records':  workflow_records})
            return True
