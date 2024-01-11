# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, date
from ...thiqah_base.models.tools import get_random_string

CONDITION_CODE_TEMP = """# Available locals:
#  - time, date, datetime, timedelta: Python libraries.
#  - env: Odoo Environement.
#  - model: Model of the record on which the action is triggered.
#  - obj: Record on which the action is triggered if there is one, otherwise None.
#  - user, Current user object.
#  - workflow: Workflow engine.
#  - syslog : syslog(message), function to log debug information to Odoo logging file or console.
#  - warning: warning(message), Warning Exception to use with raise."""


class WorkflowTransition(models.Model):
    _name = 'workflow.transition'
    _description = 'Workflow Transition'
    _order = "sequence, name, id"

    name = fields.Char(
        string='Name', help="Enter friendly link name that describe the process.")
    condition_code = fields.Text(
        string='Condition Code', default=CONDITION_CODE_TEMP, help="Enter condition to pass thru this link.")

    # display_name = fields.Char(string='Name')
    name = fields.Char('Technical Name')
    sequence = fields.Integer(default=0)
    action_id = fields.Many2one('workflow.action', required=True, string='Action', ondelete='cascade')
    state_from = fields.Many2one(related='action_id.state_id', string='State from',domain="[('workflow_id','=',workflow_id)]")
    state_to = fields.Many2one(related='action_id.state_to', string='State to', domain="[('workflow_id','=',workflow_id)]")
    workflow_id = fields.Many2one('workflow.workflow', string='Workflow')
    model_name = fields.Char(related='workflow_id.model_id.model')
    # For transition validation
    transition_validation_ids = fields.One2many('workflow.transition.validation', 'transition_id')
    # used to check if this transition resets the workflow
    is_return_transition = fields.Boolean( help="Set to True if this transition return to another transition.")
    return_to_transition_id = fields.Many2one('workflow.transition', string='Return To transition')
    code = fields.Text( help="pyhton expression that returns True or False to determine whether the transition is valid or not.")
    code_condition = fields.Char(help="generated condition by the widget.")
    
    @api.onchange('is_return_transition')
    def _onchange_is_return_transition(self):
        if not self.is_return_transition:
            self.return_to_transition_id = False

    def get_workflow(self):
        return self.workflow_id

    def _get_next_transition(self, state_to):
        if not self.is_return_transition:
            return self.env[self._name].search([ ('state_from', '=', state_to.id), ('is_return_transition', '!=', True)])
        else:
            return self.return_to_transition_id

    @api.constrains('state_from', 'state_to')
    def check_nodes(self):
        for transition in self:
            if transition.state_from == transition.state_to:
                raise ValidationError(
                    _("Sorry, source & destination nodes can't be the same."))

    @api.onchange('state_from', 'state_to')
    def onchange_field(self):
        for transition in self:
            if transition.state_from and transition.state_to:
                transition.name = "%s -> %s" % (
                    transition.state_from.name, transition.state_to.name)

    def _check_transition(self):
        # get the active model from the context.
        context = self.env.context.copy() or {}
        active_model = context.get('active_model', False)
        active_record = context.get('active_id', False)
        user_name = self.env['res.users'].sudo().browse([context.get('uid', False)]).name
        # in case when the action is trigger from the portal.
        if not active_model:
            active_model = context.get('active_model_portal', False)
        return active_model, active_record, user_name

    def _check_validation(self, record_id=False):
        """ Check transition validation """
        for transition in self:
            for validation in transition.transition_validation_ids:
                context = self.env.context.copy() or {}
                user = context.get('user_portal_id', self.env.user)
                allowed_user_ids = self.env['res.users']
                if record_id:
                    if validation.type == 'by_user': 
                        allowed_user_ids += validation.get_dedicated_users(record_id)
                    else:
                        for group in validation.group_ids:
                            allowed_user_ids += group.users
                if user.id not in allowed_user_ids.ids:
                    raise AccessError(_("Sorry, you are not allowed to do this action."))

    def get_from_to(self, transition):
        return ' from ' + str(transition.state_from.name).lower() + ' to ' + str(transition.state_to.name).lower()

    # TODO : NEED opitmization as soon as possible ! due to the abnormal frequent changes !
    def fix_access_denied_issue(self):
        ir_model = self.env['ir.model']
        # Find the "ir.model" model
        model = ir_model.sudo().search([('model', '=', 'ir.model')], limit=1)
        if model:
            # Retrieve the ACL rules for the model
            acl_rules = model[0].access_ids
            # Find the user group associated with UID 14
            user_group = self.env['res.groups'].sudo().search([('users', 'in', self.env.user.id)], limit=1)
            if user_group:
                # Check if the read permission is already assigned to the user group
                read_permission = acl_rules.filtered(lambda r: r.perm_read and r.group_id == user_group)
                if not read_permission:
                    new_acl_rule = self.env['ir.model.access'].sudo().create({
                    'name': 'Read Access for User Group',
                    'model_id': model[0].id,
                    'group_id': user_group[0].id,
                    'perm_read': True,
                    })

    def notify_helper(self, record_id, next_transition, allowed_users_next_transition):
        # action_portal_notification| Inject into notification System
        # Helper
        # Email && Portal (Notifications)
        message = _('You are among those concerned for the next action in ') + \
            str(record_id.name_get()[0][1])+'.'

        if next_transition.state_to.is_approved:
            message = _('This request ' + str(record_id.name_get()[0][1]) + ' need to be approved.')
        for allowed_user_next_transition in allowed_users_next_transition:
            notif_id = self.env['notification.system'].sudo().create({
                'message_id': get_random_string(23),
                'name': _('Service Request Assignment'),
                'description': message,
                'user_id': allowed_user_next_transition.id,
                'url_redirect': record_id.get_change_status_url(),
                'model_name': record_id._name,
                'model_id': record_id.id
            })
            notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
            record_id.send_mail_notification(allowed_user_next_transition)
            #############################
            # Requiring actions
            #############################
            # TODO: Move it to a mixin please!
            #  (!) process depending on the sequence and the current user.
            requiring_users_concerned = [user_concerned.id for user_concerned in allowed_users_next_transition]
            domain = [('related_code', '=', record_id.sequence), ('user_ids', 'in', self.transition_validation_ids.user_ids.ids)]
            requiring_action = self.env['thiqah.portal.requiring.action'].sudo()
            action_exists = requiring_action.search( domain, limit=1)
            if len(action_exists) > 0:
                values = {
                    'service_status': next_transition.state_from.name,
                    'user_ids': [(6, 0, requiring_users_concerned)],
                    'current_step': record_id.current_step,
                    'last_step': record_id.last_step,
                    'last_step_created_by': record_id.last_step_created_by.id,
                    'last_step_created_at': record_id.last_step_created_at,
                    'users_ids': [(6, 0, requiring_users_concerned)]
                }
                action_exists.write(values)

    def get_transition_allowed_users(self, record_id):
        dedicated_user_ids = self.env['res.users']
        for validation in self.transition_validation_ids:
            if validation.type == 'by_user':
                dedicated_user_ids += validation.get_dedicated_users(record_id)
            else:
                for group in validation.group_ids:
                    dedicated_user_ids += group.users
        return dedicated_user_ids
        
    def trigger_transition(self, active_record_id=None, active_model_name=None):
        """
        active_record_id,active_model_name : coming from orm.create.
        """
        self.fix_access_denied_issue()
        active_model, active_record, user_name = self._check_transition()
        if active_record_id and active_model_name:
            active_record = active_record_id
            active_model = active_model_name

        context = self.env.context.copy() or {}
        user_portal = context.get('user_portal_id', False)
        current_user = self.env['res.users'].sudo().browse([int(user_portal)]).id
        try:
            model_object = self.env[active_model].sudo()
            record_id = model_object.browse([int(active_record)])
        except Exception:
            record_id = False
        self._check_validation(record_id)

        if record_id:
            for transition in self:
                next_transition = transition._get_next_transition(transition.state_to)
                # do_action && internal notification
                if record_id.state == transition.state_from.technical_name:
                    record_id.state = transition.state_to.technical_name
                    # Independently fill the traceability_actors_ids
                    traceability_actors_ids = record_id.traceability_actors_ids.ids
                    current_actor = self.env['res.users'].sudo().browse( [int(user_portal)]).id if user_portal else self.env.user.id
                    # traceability_actors_ids = traceability_actors_ids.append(self.env['res.users'].sudo().browse([int(user_portal)]).id if user_portal else self.env.user.id)
                    traceability_actors_ids.append(current_actor)
                    # delete duplciate(due to initial injection in the create event)
                    traceability_actors_ids = list(set(traceability_actors_ids))
                    record_id.sudo().write({'traceability_actors_ids': [(6, 0, traceability_actors_ids)],})
                #If Next Transition
                if record_id._name == 'thiqah.project.service.request' and next_transition:
                    allowed_users_next_transition = next_transition.get_transition_allowed_users(record_id)
                    record_id.write({
                            'current_step': next_transition.action_id.name.upper(),
                            'last_step': transition.action_id.name.upper(),
                            'last_step_created_by': self.env['res.users'].sudo().browse([int(user_portal)]).id if user_portal else self.env.user.id,
                            'last_step_created_at': date.today()
                        })
                    if allowed_users_next_transition:
                        transition.notify_helper(record_id, next_transition, allowed_users_next_transition)
                        record_id.write({'concerned_user_ids':  [(6, 0, allowed_users_next_transition.ids)]})
                    else:
                        record_id.concerned_user_ids = [(5, 0, 0)]
                # If this is the last transition
                elif record_id._name == 'thiqah.project.service.request' and transition.state_to.is_approved:
                    record_id.write({'is_approved': True, 'concerned_user_ids': [(5, 0, 0)]})
                    user_to_notify = record_id.create_uid
                    domain = [('related_code', '=', record_id.sequence)]
                    requiring_action = self.env['thiqah.portal.requiring.action'].sudo()
                    action_exists = requiring_action.search(domain, limit=1)
                    if len(action_exists) > 0:
                        values = {
                            'service_status': transition.state_to.name,
                            'user_ids': [(6, 0, [user_to_notify.id])],
                            'current_step': transition.state_to.name,
                            'last_step': transition.state_from.name,
                            'last_step_created_by': current_user,
                            'last_step_created_at': datetime.now().date(),
                            'users_ids': [(6, 0, [user_to_notify.id])]
                        }
                        action_exists.write(values)
                    # Dynamic Formatting Message && Url Redirect
                    message_approve = _('This request was approved: ') +  str(record_id.sequence)
                    url_redirect = str( record_id.get_change_status_url())
                    domain_attachment = [('res_model', '=', record_id._name),
                        ('res_id', '=', record_id.id)]
                    resource_attachments = self.env['ir.attachment'].sudo().search(
                        domain_attachment)
                    if len(resource_attachments) > 0:
                        message_approve = _('The request ' + str(record_id.sequence) + ' was approved with attachments (see documents section).')
                        # url_redirect += "#redirect_documents_section"
                    notif_id = self.env['notification.system'].sudo().create({
                            'message_id': get_random_string(23),
                            'name': _('Service Request APPROVED'),
                            'description': _(message_approve),
                            'user_id': user_to_notify.id,
                            'url_redirect': url_redirect,
                            'model_id': record_id.id,
                            'model_name': 'thiqah.project.service.request',
                            'type': 'confirm'
                        })
                    notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
                    
