# -*- coding:utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError
from lxml import etree
import ast
import json
import logging
_logger = logging.getLogger(__name__)


ELEMENT = "//form/header"

MODEL_NAME = 'workflow.workflow'

# TODO: AbstractModel and chech the loading order in __init__.


class WorkflowEngine(models.Model):
    _name = 'workflow.engine'
    _description = 'Workflow Engine'

    is_visible = fields.Boolean(default=False)
    is_done = fields.Boolean(default=False)
    is_in_progress = fields.Boolean(default=False)

    # Mailing | Tracking Tools

    def _send_email(self):
        """ send notification email to a concerned employee related to the workflofw action. """
        self.ensure_one()

        # determine subject and body in the portal user's language
        template = self.env.ref(
            'thiqah_mail.mail_template_service_request')

        if not template:
            raise UserError(
                _('The template "Service : new user" not found for sending email.'))

        lang = self.user_id.sudo().lang
        partner = self.user_id.sudo().partner_id

        mail = template.send_mail(self.id, force_send=True)

        return True

    def reply_tracking(self, body):
        for service_request in self:
            service_request.message_post(
                body=body,
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )
            # service_request.action_send_email(email_values)

    def action_internal_notifcation(self, notification_ids, message):
        # self.env.ref('thiqah_project.internal_notifcation_template_service_request')
        channel_id = self.env.ref('thiqah_mail.channel_change_status_assignees')

        # for notification_id in notification_ids:
        channel_id.message_post(author_id=self.env.user.id,
                                body=message,
                                message_type='notification',
                                subtype_xmlid="mail.mt_comment",
                                notification_ids=notification_ids,
                                notify_by_email=False,
                                )

    def action_external_notifcation(self, notification_ids, record_id, attachments_ids=None):
        notifcation_template_id = self.env.ref(
            'thiqah_project.internal_notifcation_template_service_request')
        # if template_id:
        #     notifcation_template_id = template_id
        if attachments_ids:
            notifcation_template_id.attachment_ids = [
                (6, 0, attachments_ids.ids)]

        # try:
        # get email dynamically
        # [(0, 0, {'res_partner_id': 1397, 'notification_type': 'inbox'}), (0, 0, {'res_partner_id': 3, 'notification_type': 'inbox'})]

        for notification_id in notification_ids:
            email = self.env['res.partner'].search(
                [
                    ('id', '=', int(notification_id[2]['res_partner_id']))
                ]
            ).email

            if email:
                notifcation_template_id.send_mail(record_id.id, email_values={
                    'email_from': 'cxp@thiqah.sa',
                    'email_to': email
                })

        if attachments_ids:
            for attachment_id in notifcation_template_id.attachment_ids:
                notifcation_template_id.attachment_ids = [
                    (3, attachment_id.id)]

        # except Exception as exception:
        #     _logger.exception("Exception sending mail: ", str(exception))

    def action_notification(self, notification_ids, message, record_id, attachments_ids=None):
        try:
            self.action_internal_notifcation(
                notification_ids, message)
            # self.action_external_notifcation(
            #     notification_ids, record_id, attachments_ids)
        except Exception as exception:
            json.dumps('Exception sending mail: '+str(exception))

    def reload(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model_create_multi
    def create(self, vals_list):
        res = super(WorkflowEngine, self).create(vals_list)
        if not res.state:
            # compute default state depending from each workflow.
            result = self.check_active_id(res.id)
            workflow_id = self.env[MODEL_NAME].sudo().browse([
                int(result['workflow_id'])
            ])
            _pass = bool(result['result'])
            states_visible = []
            if _pass:
                for workflow in workflow_id:
                    for action in workflow.action_ids:
                        states_visible.append(action.state_id.technical_name)
                if states_visible:
                    res.update({'state': states_visible[0]})
        return res

    @api.model
    def _get_worflow_id(self):
        ir_model = self.env['ir.model'].sudo()
        workflow_workflow = self.env[MODEL_NAME].sudo()
        model_id = ir_model.search([('model', '=', self._name)])
        workflows = workflow_workflow.search([('model_id', '=', model_id.id)])
        active_id = self._context.get('params', {}).get('id', False)
        active_model = self._context.get('params', {}).get('model', '')
        if active_id and active_model and active_model == 'thiqah.project.service.request':
            rec_id = self.env[active_model].browse(active_id)
            workflows = workflows.filtered(lambda r: rec_id.catalog_id and rec_id.catalog_id.id in r.criteria_ids.mapped('criteria_id'))
            for workflow in workflows:
                workflow.mapping_records_criterias()
        return workflows

    @api.model
    def check_active_id(self, record_portal=None):
        context = self.env.context.copy() or {}
        record_id = 0
        if 'params' in context:
            if 'id' in context['params']:
                record_id = context['params']['id']

        if record_portal:
            record_id = record_portal

        workflows = self.with_context(params={'model': self._name, 'id':record_id})._get_worflow_id()
        result = {'workflow_id': 0, 'result': False}
        if workflows:
            result = {'workflow_id': workflows[0].id, 'result': True}

        for workflow in workflows:
            if workflow.criteria_ids:
                if workflow.workflow_records:
                    if record_id in ast.literal_eval(workflow.workflow_records):
                        result['workflow_id'] = workflow.id
                        result['result'] = True
                        return result
        return result

    def _get_buttons_data(self, workflow_id):
        # workflow_id = self._get_worflow_id()
        # prepare //button data.
        buttons = []
        if workflow_id:
            for action_id in workflow_id.action_ids:
                buttons.append(
                    {
                        'name': action_id.name,
                        'type': action_id.type,
                        'description': action_id.description,
                        'button_key': action_id.button_key,
                        'state_id': action_id.state_id.technical_name
                    }
                )
        return buttons

    def _get_state_items(self, workflow_=None, exclude_approved_rejected=False):
        workflows = workflow_ if workflow_ else self._get_worflow_id()
        selection_content = []
        for worklfow_id in workflows:
            for action in worklfow_id.action_ids.filtered(lambda r: not r.is_return_action):
                selection_content.append((action.state_id.technical_name, action.state_id.name))
                if action.state_to.flow_end and (not exclude_approved_rejected or not action.state_to.is_approved): 
                    selection_content.append((action.state_to.technical_name, action.state_to.name))
        if not exclude_approved_rejected:
            selection_content.append(('reject', 'Rejected'))
        return selection_content

    @api.model
    def get_display_request_state(self):
        """
        Get the display state of the service request.
        :return: the repr string of the current state
        :rtype: str
        """
        self.ensure_one()
        return dict(self._get_state_items()).get(self.state), self.state

    @api.model
    def _compute_default_state(self, workflow_=None):
        """
        .
        """
        workflow_obj = self.env[MODEL_NAME]
        workflow_objs = workflow_obj.search([('model_id', '=', self._name)])
        if workflow_:
            workflow_objs = workflow_objs
            selection_content = self._get_state_items(workflow_)
            return selection_content[0][0]

        # for workflow in workflow_objs:
        #     for state in workflow.state_ids:
        #         if state.flow_start:
        #             return state.technical_name

    state = fields.Selection(
        _get_state_items, string="Request Service Status", default=_compute_default_state)

    def _locate_arch_target(self, xmlid_to_res_id):
        """
        .
        """
        form_view_id = self.env['ir.model.data']._xmlid_to_res_id(
            xmlid_to_res_id)

        form_view = self.env.ref(
            xmlid_to_res_id)

        return form_view_id, form_view

    def _check_header(self, view_type, arch_tree):
        """
        cehck if there is header in arch_tree
        """
        header = False
        if view_type == 'form':
            header = arch_tree.xpath(ELEMENT)
            if len(header) > 0:
                return True, header
            header = False
        return False, header

    def _remove_current_header(self, arch_tree, view_type, form_view, res, element=ELEMENT):
        """
            Removes current header element from form view.
            :param view_type: Type of view now rendering.
            :param res: View resource data.
            :return: Updated view resource.
        """
        header_check, header = self._check_header(view_type, arch_tree)
        if header_check:
            header_target = header[0]

            if header_target is not False:
                header_target.getparent().remove(header[0])
                no_header = True
        else:
            no_header = True

        # no_header = False
        # if view_type == 'form':
        #     header = arch_tree.xpath(element)

        #     if len(header) > 0:
        #         header_target = header[0]

        #         if header_target is not False:
        #             header_target.getparent().remove(header[0])
        #             no_header = True
        #     else:
        #         no_header = True

        form_view.sudo().write(
            {'arch': etree.tostring(arch_tree, encoding='unicode')})

        return res, no_header

    def _insert_header(self, arch_tree, form_view, no_header, res):
        """
        insert into arch_tree if there is header.
        """
        if no_header:
            # Create Header Element If not Exists
            header_el = etree.Element('header')
            arch_tree[0].getparent().insert(0, header_el)
            form_view.sudo().write(
                {'arch': etree.tostring(arch_tree, encoding='unicode')})
            is_injected = True
        return res, is_injected

    def _inject_states(self, arch_tree, form_view, res, workflow_id=None):
        """
        .
        """
        # Don't force people to update 'this' current module.
        # Preparing basic state field
        state_element = etree.Element('field', attrib={
            'name': 'state',
            'widget': 'statusbar',
        })

        # Handling visibility
        # workflow_id = self._get_worflow_id()
        result = self.check_active_id()
        workflow_id = self.env[MODEL_NAME].sudo().browse([
            int(result['workflow_id'])
        ])
        _pass = bool(result['result'])
        states_visible = []
        if _pass:
            for workflow in workflow_id:
                for action in workflow.action_ids:
                    states_visible.append(action.state_id.technical_name)

            if states_visible:
                states_visible = ','.join(states_visible)
                # handling the visibilty depending on the active_id and it present in the workflow_records
                state_element.set('statusbar_visible', states_visible)

        else:
            state_element.set('invisible', '1')
            state_element.set('statusbar_visible', "")
        arch_tree[0].insert(0, state_element)
        res['arch'] = etree.tostring(arch_tree, encoding='unicode')
        return res

    def _inject_buttons(self, arch_tree, form_view, res, workflow_id):
        """
        .
        """
        # Don't force people to update 'this' current module.
        # Handling visibility
        # workflow_id = self._get_worflow_id()
        result = self.check_active_id()
        workflow_id = self.env[MODEL_NAME].sudo().browse([
            int(result['workflow_id'])
        ])

        _pass = bool(result['result'])
        if _pass:
            # Preparing buttons
            buttons = self._get_buttons_data(workflow_id)
            for button in buttons:
                state_element = etree.Element('button')
                state_element.set('name', 'abstract_button_execution')
                state_element.set('string', button['name'])
                state_element.set('type', 'object')
                # if button.is_highlight:
                #     state_element.set('class', 'oe_highlight')
                # if button.has_icon:
                #     state_element.set('icon', button.icon)
                state_element.set('attrs', "{'invisible':[('state','!=','%s')]}" % button['state_id'])
                state_element.set('context', "{'button_key':'%s','active_model':'%s'}" % (button['button_key'], self._name))
                arch_tree[0].insert(0, state_element)
        res['arch'] =  etree.tostring(arch_tree, encoding='unicode')
        return res

    @staticmethod
    def abstract_button_execution(self, button_key=None, user_portal_id=None):
        context = self.env.context.copy() or {}

        # update the context with the current record data.
        context.update({'active_id': self.id, 'active_ids': self.ids})

        # get the current action related to the button rendering in the view respecting the context.
        delegate_action = self.env['workflow.action'].sudo()
        current_action = delegate_action.search([('button_key', '=', context.get('button_key', False))])

        # Handle the events comming from the portal.
        if button_key and user_portal_id:
            context.update({
                    'active_model_portal': self._name,
                    'user_portal_id': user_portal_id
                })
            current_action = delegate_action.search([('button_key', '=', button_key)])

        if current_action:
            action_ = current_action.with_context(context).execute_action()
            return action_
        else:
            raise UserError(_('Please Verify the backend configuration.'))

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # Monkey Patch
        # OVERRIDE to add the 'state' field dynamically inside the view.
        res = super().fields_view_get(view_id=view_id,
                                      view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            form_view_id, form_view = self._locate_arch_target(
                'thiqah_project.service_request_form')

            if res.get('view_id') == form_view_id:
                tree = etree.fromstring(res['arch'])
                arch_tree = etree.fromstring(form_view.arch)

                if arch_tree.tag == 'form':
                    # get all workflows
                    workflow = self._get_worflow_id()

                #     # this loop to ensure the reset of each header.
                #     for workflow_id in workflows:
                #         # For a prupose purly technical , this process is sperated from the next loop although the latter is the same
                    res, no_header = self._remove_current_header(
                        arch_tree, view_type, form_view, res)

                    # for workflow_id in workflow:
                    #     # inject this statusbar_visible="open,posted,confirm"
                    if True:
                        res, is_injected = self._insert_header(
                            arch_tree, form_view, no_header, res)

                        if is_injected:
                            res = self._inject_states(
                                arch_tree, form_view, res, workflow)

                            res = self._inject_buttons(
                                arch_tree, form_view, res, workflow)

                        form_view.sudo().write(
                            {'arch': etree.tostring(arch_tree, encoding='unicode')})

                return super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        return res
    
    def send_mail_notification(self, users):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        link = f"{base_url}{self.get_change_status_url()}"
        mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        for user in users:
                from_user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
                mail_values = {
                    'subject': _('Request Approval'),
                    'email_from': from_user.partner_id.email_formatted,
                    'email_to': user.email,
                    'mail_server_id':mail_server.id,
                    'body_html': _(f'''
                                    <p style="margin: 0px;">
                                        <span>Dear {user.name},</span><br />
                                        
                                        <span style="margin-top: 8px;">You have a pending request that requires your approval. Please review the details and take action accordingly.</span>
                                    </p>
                                    <p style="padding-top: 24px; padding-bottom: 16px;">
                                        <a href="{link}" t-att-data-oe-model="object._name" t-att-data-oe-id="object.id" style="background-color:#36b4e5; padding: 10px; text-decoration: none; color: #fff; border-radius: 5px;">
                                            View here
                                        </a>
                                    </p>
                    '''),                     
                    'auto_delete': False,
                }
                mail = self.env['mail.mail'].sudo().create(mail_values)
                mail.send(raise_exception=False)
