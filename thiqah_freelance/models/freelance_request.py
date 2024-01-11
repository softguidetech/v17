# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from ...thiqah_base.models.tools import get_random_string


class FreelanceRequest(models.Model):
    _name = 'freelance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'workflow.engine']
    _description = 'Freelance Request'
    _rec_name = "sequence"

    sequence = fields.Char(string='Sequence', default=_('New'))
    request_date = fields.Date(string='Request Date', default=fields.Date.today())
    request_duration = fields.Char(string='Request Duration in months')
    expected_total_cost = fields.Integer(string='Expected Total Cost')
    entity_id = fields.Many2one('res.entity', string='Entity')
    entity_code = fields.Char(related='entity_id.code')
    sector = fields.Char(string='Sector')
    department_id = fields.Many2one('hr.department', string='Department')
    section = fields.Char(string='Section')
    request_type = fields.Selection([('new_project', 'New Project'), ('extend_project', 'Extend Project'), ('add_functions_tasks', 'Additional Functions/Tasks')], string='Request Type')
    request_description = fields.Text(string='Description')
    project_name = fields.Char(string='Project Name')
    project_start_date = fields.Date(string='Project Start Date')
    project_end_date = fields.Date(string='Project End Date')
    # Request Justification​
    company_strategy_justif = fields.Text(string='Company Strategy justification')
    sector_goal_justif = fields.Text(string='Sector Goals Justification')
    request_achievement = fields.Text(string='Requset Objective Acheivement')
    # Organizational Implications​ 
    current_manpower_limit = fields.Text(string='Current Manpower Limit')
    current_manpower_weakness = fields.Text(string='Current Manpower Weakness')
    impacted_unit_ids = fields.One2many('freelance.impact.unit', 'request_id', string='Impacted Units')
    # Function Breakdown​
    function = fields.Text(string='Function')
    unit_kpi = fields.Text(string='Unit KPIs')
    deliverable = fields.Text(string='Deliverable')
    # Deliverable out come​
    deliverable_outcome = fields.Text(string='Deliverable Outcome​')

    od_recommendation = fields.Text(string='OD Recommendation')
    od_duration = fields.Integer(string='OD Duration')
    od_cost = fields.Integer(string='OD Expected Cost')
    concerned_user_ids = fields.Many2many( 'res.users', 'frequest_concerned_user_rel', 'frequest_id', 'user_id')
    traceability_actors_ids = fields.Many2many( 'res.users', 'traceability_frequest_user_rel', 'frequest_id', 'user_id')
    last_step_created_by = fields.Many2one('res.users')
    last_step_created_at = fields.Date('Last Step Create At')
    justification_text = fields.Text()
    is_approved = fields.Boolean(default=False)
    freelancer_count = fields.Integer(string='Freelancer Count', compute='_compute_freelancer')
    freelance_application_ids = fields.One2many('freelance.application', 'request_id', string='Freelance Applications')
    #Helpers fields
    is_freelance_fully_added = fields.Boolean(string='Is Freelancer Fully Added?', default=False)
    last_workorder_date = fields.Date()
    expired = fields.Boolean(default=False)

    # Ahad fields
    ahad_client_name = fields.Char()
    ahad_project_name = fields.Char()
    ahad_project_number = fields.Char()

    def _compute_freelancer(self):
        for rec in self:
            rec.freelancer_count = rec.env['freelance.application'].search_count([('request_id', '=', rec.id)])
    
    def action_open_freelancer(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('thiqah_freelance.freelance_application_action')
        action['domain'] = [('request_id', '=', self.id)]
        return action

    def get_change_status_url(self):
        self.ensure_one()
        return '/my/freelance/%s?' % (self.id)
    
    def reject_request(self):
        self.write({'state': 'reject'})

    @api.model
    def create(self, vals):
        """
        override the create method to add sequence processing.
        """
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code(self._name) or 'New'
        # Search the right workflow
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)])
        workflow_id = self.env['workflow.workflow'].sudo().search([('model_id', '=', model_id.id)]).filtered(lambda r: int(vals.get('entity_id', '0')) in r.criteria_ids.mapped('criteria_id'))
        if workflow_id:
            workflow_id = workflow_id[0]
            state_ids = workflow_id.state_ids.filtered(lambda r: r.flow_start == True)
            vals['state'] = state_ids[0].technical_name if state_ids else False
        res = super().create(vals)
        
        #if no workflow found ==> nothing to to
        if not workflow_id:
            return res
        allowed_users = self.env['res.users']
        transition_id = workflow_id.transition_ids.filtered(lambda r: r.sequence == 0)
        for validation in transition_id.transition_validation_ids:
            if validation.type == 'by_user': 
                allowed_users += validation.get_dedicated_users(res)
            else:
                for group in validation.group_ids:
                    allowed_users += group.users
        # If draft state ==> it means that is the same user who created the request
        # ==> No need to send notification 
        if res.state != 'draft':
            for allowed_user in allowed_users.ids:
                notif_id = self.env['notification.system'].sudo().create({
                    'message_id': get_random_string(23),
                    'name': _('Freelance Request Assignment'),
                    'description': _('This freelance request is pending your action: ' + vals['sequence']),
                    'user_id': allowed_user,
                    'url_redirect': res.get_change_status_url(),
                    'model_id': res.id,
                    'model_name': res._name
                })
                notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
            res.send_mail_notification(allowed_users)
        if allowed_users:
            res.write({
                'concerned_user_ids': [(6, 0, allowed_users.ids)],
                'traceability_actors_ids': [(6, 0, allowed_users.ids)]
            })
        return res
    
    # Cron generate_workorder
    def generate_workorder(self):
        workorder_start_date = fields.Date.today() + relativedelta(day=1)
        workorder_end_date = fields.Date.today() + relativedelta(day=31)
        workorder_duration = (workorder_end_date - workorder_start_date).days + 1
        frequest_ids = self.env['freelance.request'].search([('state', '=', 'approved')])
        for frequest in frequest_ids:
            freelance_application_ids = frequest.freelance_application_ids.filtered(lambda r: r.end_date >= workorder_start_date and r.start_date <= workorder_end_date)
            for application in freelance_application_ids:
                start_date = workorder_start_date if application.start_date <= workorder_start_date else application.start_date
                end_date = workorder_end_date if application.end_date >= workorder_end_date else application.end_date
                duration = (end_date - start_date).days + 1
                vals = {
                    'freelancer_id': application.id,
                    'frequest_id': frequest.id,
                    'due_date': workorder_end_date,
                    'date_from': start_date,
                    'date_to': end_date,
                    'duration': duration,
                }
                if duration == workorder_duration:
                    vals['amount'] = application.salary
                else:
                    vals['amount'] = round(((application.salary / 30) * duration), 2) 
                self.env['freelance.workorder'].create(vals)

    @api.model
    def _get_worflow_id(self):
        active_id = self._context.get('params', {}).get('id', False)
        active_model = self._context.get('params', {}).get('model', '')
        if active_id and active_model and active_model == self._name:
            ir_model = self.env['ir.model'].sudo()
            workflow_workflow = self.env['workflow.workflow'].sudo()
            model_id = ir_model.search([('model', '=', self._name)])
            rec_id = self.env[active_model].browse(active_id)
            workflows = workflow_workflow.search([('model_id', '=', model_id.id)])
            workflows = workflows.filtered(lambda r: rec_id.entity_id and rec_id.entity_id.id in r.criteria_ids.mapped('criteria_id'))
            return workflows
        else:
             return super(FreelanceRequest, self)._get_worflow_id()