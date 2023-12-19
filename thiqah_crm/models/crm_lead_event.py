

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict


class CRMLeadEvent(models.Model):
    _name = "crm.lead.event"
    _description = "CRM Lead Event"
    _inherit = ['portal.mixin', 'mail.thread.cc',
                'mail.activity.mixin', 'rating.mixin']

    active = fields.Boolean('Active', default=True)

    name = fields.Char(string='Title', tracking=True,
                       required=True, index=True)

    description = fields.Html(string='Description')

    display_lead_id = fields.Many2one('crm.lead', index=True)

    parent_id = fields.Many2one(
        'crm.lead.event', string='Parent Event', index=True)

    lead_id = fields.Many2one('crm.lead', string='Lead',
                              compute='_compute_lead_id', recursive=True, store=True, readonly=False,
                              index=True, tracking=True, check_company=True, change_default=True)

    date_start = fields.Date()
    date = fields.Date()

    color = fields.Integer(string='Color Index')

    def action_view_kanban_event(self):
        return

    @api.model
    def _default_company_id(self):
        return self.env.company

    company_id = fields.Many2one(
        'res.company', string='Company', compute='_compute_company_id', store=True, readonly=False,
        required=True, copy=True, default=_default_company_id)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Starred", tracking=True)

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Status',
        copy=False, default='normal', required=True)

    @api.depends('parent_id.lead_id', 'display_lead_id')
    def _compute_project_id(self):
        for event in self:
            if event.parent_id:
                event.lead_id = event.display_lead_id or event.parent_id.lead_id

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # for vals in vals_list:
    #     #     lead_id = vals.get('lead_id') or self.env.context.get(
    #     #         'default_lead_id')
    #     #     if lead_id:
    #     #         vals['display_lead_id'] = lead_id

    #     events = super(CRMLeadEvent, self).create(vals_list)

    #     return events

    def action_view_leads(self):
        action = self.env.ref('thiqah_crm.act_crm_lead_all_event') \
            .sudo().read()[0]

        return action

    label_leads = fields.Char(string='Lead', default='Leads',
                              help="Label used for the leads of the event.", translate=True)

    def _compute_lead_count(self):
        lead_data = self.env['crm.lead'].read_group(
            [('event_id', 'in', self.ids), ('type', '=', 'lead')],
            ['event_id', 'display_event_id:count'], ['event_id'])

        result_wo_subevent = defaultdict(int)
        for data in lead_data:
            result_wo_subevent[data['event_id'][0]
                               ] += data['display_event_id']
        for event in self:
            event.lead_count = result_wo_subevent[event.id]

    lead_count = fields.Integer(
        compute='_compute_lead_count', string="Lead Count")
