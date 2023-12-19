# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ...thiqah_base.models.tools import get_random_string


class ClientProduct(models.Model):
    _name = 'client.product'
    _description = 'Client Product'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')


class ClientRegistration(models.Model):
    _name = 'client.registration'
    _description = 'Clients Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'client_name'

    # Client Info (Company)
    client_name = fields.Char(string='Supplier Name')
    site_name = fields.Char(string='Site Name')
    supplier_oracle_id = fields.Char(string='Supplier Oracle ID')
    # Bank Info
    bank_country = fields.Many2one('res.country', string='Bank Country')
    bank_name = fields.Char( string='Bank')
    branch_name = fields.Char(string='Branch')
    bank_id = fields.Char( string='Bank')
    branch_id = fields.Char(string='Branch')
    account = fields.Char(string='Account')
    account_holder_name = fields.Char(string='Account holder name')
    iban = fields.Char(string='IBAN')
    # Helper fields
    is_bank_added = fields.Boolean(default=False)
    state = fields.Selection([('draft', 'Draft'), ('product_manager', 'Product manager'), ('business_operation', 'Business Operation'), ('approved', 'Approved')], default='draft')
    client_product_id = fields.Many2one('client.product', string="Client Product")
    concerned_user_ids = fields.Many2many( 'res.users', 'creg_concerned_user_rel', 'creg_id', 'user_id')
    legal_representative = fields.Char(string='Legal representative')
    id_number = fields.Char(string='ID Number')
    phone_number = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')


class ClientPayment(models.Model):
    _name = 'client.payment'
    _description = 'Clients Payments'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'workflow.engine']
    _rec_name = "sequence"

    sequence = fields.Char(string='Sequence', default=_('New'))
    client_registration_id = fields.Many2one('client.registration', string="Client Registration")
    client_product_id = fields.Many2one('client.product', string="Client Product")
    client_name = fields.Char(related='client_registration_id.client_name',string='Client Name')
    site_name = fields.Char(related='client_registration_id.site_name',string='Site Name')
    legal_representative = fields.Char(string='Legal representative')
    currency_id = fields.Many2one('res.currency', string="Currency",default=lambda self: self.env.company.currency_id)
    total_amount = fields.Monetary(string='Total Amount')
    mazad_number = fields.Char(string='Mazad Number')
    id_number = fields.Char(string='ID Number')
    phone_number = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    concerned_user_ids = fields.Many2many( 'res.users', 'cpay_concerned_user_rel', 'cpayment_id', 'user_id')
    traceability_actors_ids = fields.Many2many( 'res.users', 'traceability_cpay_user_rel', 'cpayment_id', 'user_id')
    last_step_created_by = fields.Many2one('res.users')
    last_step_created_at = fields.Date('Last Step Create At')
    is_approved = fields.Boolean(default=False)
    invoice_created = fields.Boolean(default=False)
    invoice_validated = fields.Boolean(default=False)

    def get_change_status_url(self):
        self.ensure_one()
        return '/my/client_payment/%s?' % (self.id)
    
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
            workflows = workflows.filtered(lambda r: rec_id.client_product_id and rec_id.client_product_id.id in r.criteria_ids.mapped('criteria_id'))
            return workflows
        else:
             return super(ClientPayment, self)._get_worflow_id()
    
    @api.model
    def create(self, vals):
        """
        override the create method to add sequence processing.
        """
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code(self._name) or 'New'
        # Search the correct workflow
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)])
        workflow_id = self.env['workflow.workflow'].sudo().search([('model_id', '=', model_id.id)]).filtered(lambda r: vals['client_product_id'] in r.criteria_ids.mapped('criteria_id'))
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
        for allowed_user in allowed_users.ids:
            notif_id = self.env['notification.system'].sudo().create({
                'message_id': get_random_string(23),
                'name': _('Client Payment Assignment'),
                'description': _('This client payment request is pending your action: ' + vals['sequence']),
                'user_id': allowed_user,
                'url_redirect': res.get_change_status_url(),
                'model_id': res.id,
                'model_name': res._name
            })
            notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
        if allowed_users:
            res.write({
                'concerned_user_ids': [(6, 0, allowed_users.ids)],
                'traceability_actors_ids': [(6, 0, allowed_users.ids)]
            })
        return res
