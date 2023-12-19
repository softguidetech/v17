# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
from ...thiqah_base.models.tools import get_random_string

#If you edit these selection please edit also this file: thiqah_inquiry/data/inquiry_request_sla_data.xml
REQUEST_TYPE = [('inquiry', _('Inquiry')), ('complaint', _('Complaint')), ('other', _('Other'))]
URGENCY = [('heigh', _('Heigh')), ('medium', _('Medium')), ('low', _('Low'))]

class InquiryRequest(models.Model):
    _name = 'inquiry.request'
    _description = 'Inquiry Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'workflow.engine']
    _rec_name = "sequence"

    sequence = fields.Char(string='Sequence', default=_('New'))
    partner_portfolio = fields.Many2one('category.portfolio', string='Partner Portfolio')
    partner_id = fields.Many2one('res.partner', domain=([('is_customer', '=', True)]), string='Partner')
    department_id = fields.Many2one('hr.department', string='Department')
    section = fields.Char(string='Section')
    request_type = fields.Selection(REQUEST_TYPE, string='Request Type')
    urgency = fields.Selection(URGENCY, string='Urgency')
    due_date = fields.Date(string='Due Date')
    description = fields.Text(string='Description')
    user_id = fields.Many2one('res.users', string='Assigned to')
    # Workfow fields
    concerned_user_ids = fields.Many2many( 'res.users', 'irequest_concerned_user_rel', 'irequest_id', 'user_id')
    traceability_actors_ids = fields.Many2many( 'res.users', 'traceability_irequest_user_rel', 'irequest_id', 'user_id')
    last_step_created_by = fields.Many2one('res.users')
    last_step_created_at = fields.Date('Last Step Create At')
    is_approved = fields.Boolean(default=False)
    close_date = fields.Datetime(string='Close Date')
    # SLA Fields
    sla_id = fields.Many2one('inquiry.request.sla', string='SLA')
    sla_due_date = fields.Datetime(string='SLA Due Date')

    # Override this to inject the permission of the use in the forms.
    def _register_hook(self):
        result = super()._register_hook()
        ir_model = self.env['ir.model'].sudo()
        inquiry_request_model = ir_model.search([('model', '=', self._name)])
        if not inquiry_request_model.website_form_access:
            inquiry_request_model.write({'website_form_access': True })
            return True
        return result
    
    @api.model
    def _get_worflow_id(self):
        active_id = self._context.get('params', {}).get('id', False)
        active_model = self._context.get('params', {}).get('model', '')
        if active_id and active_model and active_model == self._name:
            ir_model = self.env['ir.model'].sudo()
            workflow_workflow = self.env['workflow.workflow'].sudo()
            model_id = ir_model.search([('model', '=', self._name)])
            workflows = workflow_workflow.search([('model_id', '=', model_id.id)])
            return workflows
        else:
             return super(InquiryRequest, self)._get_worflow_id()
    
    def get_change_status_url(self):
        self.ensure_one()
        return '/my/inquiries/%s?' % (self.id)
    
    def get_due_date(self, start_date, days):
        due_date = start_date
        for i in range(days):
            due_date = due_date + timedelta(days=1)
            if due_date.weekday() == 4:
                due_date = due_date + timedelta(days=2)
            if due_date.weekday() == 5:
                due_date = due_date + timedelta(days=1)
        return due_date
    
    @api.model
    def create(self, vals):
        """
        override the create method to add sequence processing.
        """
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code(self._name) or 'New'
        if vals.get('request_type') and vals.get('urgency'):
            sla_id = self.env['inquiry.request.sla'].search([('request_type', '=', vals['request_type']), ('urgency', '=', vals['urgency'])], limit=1)
            if sla_id:
                vals['sla_id'] = sla_id.id
                vals['sla_due_date'] = self.get_due_date(fields.Datetime.now(), sla_id.sla_days)
        # Search the correct workflow
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)])
        workflow_id = self.env['workflow.workflow'].sudo().search([('model_id', '=', model_id.id)], limit=1)
        if workflow_id:
            workflow_id = workflow_id[0]
            state_ids = workflow_id.state_ids.filtered(lambda r: r.flow_start == True)
            vals['state'] = state_ids[0].technical_name if state_ids else False
        res = super(InquiryRequest, self).create(vals)
        
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
        for allowed_user in allowed_users.ids:
            notif_id = self.env['notification.system'].sudo().create({
                'message_id': get_random_string(23),
                'name': _('Inquiry Request Assignment'),
                'description': _('This inquiry request is pending your action: ' + vals['sequence']),
                'user_id': allowed_user,
                'url_redirect': res.get_change_status_url(),
                'model_id': res.id,
                'model_name': res._name
            })
            notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
        if allowed_users:
            res.send_mail_notification(allowed_users)
            res.write({
                'concerned_user_ids': [(6, 0, allowed_users.ids)],
                'traceability_actors_ids': [(6, 0, allowed_users.ids)]
            })
        return res