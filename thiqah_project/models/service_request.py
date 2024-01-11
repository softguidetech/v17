# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.http import request
from ...thiqah_base.models.tools import get_random_string


class RequestService(models.Model):
    _name = 'thiqah.project.service.request'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin', 'thiqah.project.mixin', 'workflow.engine']
    _description = 'Thiqah Service Request'

    @api.model
    def _default_notification_mail_template(self):
        try:
            return self.env.ref('thiqah_project.internal_notifcation_template_service_request').id
        except ValueError:
            return False
        
    def _compute_current_step(self):
        for record in self:
            record.current_step = str(record.state)
    
    name = fields.Char()
    sequence = fields.Char(string='Request Number', required=True,readonly=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', required=True, help='List contains all projects.')
    project_manager_id = fields.Many2one( related='project_id.user_id', store=True)
    # Project accountant
    project_accountant_id = fields.Many2one( related='project_id.project_accountant_id', string='Project accountant')
    vp_id = fields.Many2one( related='project_id.vp', string='VP')
    director_finance_id = fields.Many2one( related='project_id.director_finance', string='Project accountant')
    client_id = fields.Many2one( related='project_id.partner_id', store=True,  default=lambda self: self.partner_id, help='List contains all clients related to a project.')
    department_id = fields.Many2one( 'hr.department',  required=True, help='List contains all departments.')
    catalog_id = fields.Many2one( 'thiqah_project.service_catalog', required=True, string="Service Catalog",  help='List contains all service catalogs.')
    user_id = fields.Many2one('res.users', 'Requester', default=lambda self: self.env.user)
    employee_id = fields.Many2one( 'hr.employee', string="Employee", default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1), readonly=True)
    request_status = fields.Selection([
        ('submitted', 'Submitted'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], string="Status", default="submitted", compute="_compute_request_status", store=True)
    access_token = fields.Char()
    description = fields.Text('Description', help='Request description.')
    date_from = fields.Date( 'Request date', required=True, help='The request date')
    notes = fields.Text('Remarks')
    document_description = fields.Text('Document Description')
    # For technical purpose (Make the website form process more flexible regarding the related field)
    partner_id = fields.Many2one('res.partner')
    sla = fields.Integer(related='catalog_id.sla', store=True)
    sla_indicator = fields.Selection([('late', 'Late'), ('on_time', 'On Time'), ('n_a', 'N/A')], default='on_time')

    # Fields depending of SLA
    sla_end_date = fields.Date( 'SLA End date', help='SLA deadline.', readonly=True)
    delivery_date = fields.Date('Delivery Date', readonly=True)
    remaining_day = fields.Integer( 'Remaining Day', compute="_compute_remaining_day", readonly=True)
    actual_working_date = fields.Integer( 'Number of actual workning days.', compute="_compute_actual_working_date", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True, default=lambda self: self.env.company)
    current_step = fields.Char('Current Step', compute='_compute_current_step')
    last_step = fields.Char('Last Step')
    last_step_created_by = fields.Many2one('res.users')
    last_step_created_at = fields.Date('Last Step Create At')

    # Workflow | HR
    project_user_id = fields.Many2one('res.users')
    for_hr = fields.Boolean(default=False)
    last_message = fields.Char()
    need_to_be_approved = fields.Boolean(default=False)

    # Each actor view only the service requests that he supposed to do action on them.
    is_approved = fields.Boolean(default=False)
    # new need : add traceability on all services requests that  the actor do action (reject or approved).
    concerned_user_ids = fields.Many2many( 'res.users', 'service_actor_rel', 'service_id', 'actor_id')
    traceability_actors_ids = fields.Many2many( 'res.users', 'traceability_actors_rel', 'service_id', 'actor_id')
    justification_text = fields.Text()
    notifcation_template_id = fields.Many2one('mail.template', string="Email Template Notification ",
                                              domain="[('model', '=', 'thiqah.project.service.request')]",
                                              default=_default_notification_mail_template,
                                              help="Email sent to the concerned employee once the status is changed.")
    line_manager_id = fields.Many2one(related='project_id.user_id.employee_ids.parent_id.user_id')

    def get_line_manager(self):
        return self.line_manager_id
    
    def name_get(self):
        res = []
        for request_service in self:
            name = request_service.sequence
            res += [(request_service.id, name)]
        return res
    
    @api.model
    def create(self, vals):
        """
        override the create method to add sequence processing.
        """
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('thiqah_project_service_request') or _('New')
        context = {}
        if request:
            geoip = request.session.geoip
            device = request.httprequest.user_agent.platform
            browser = request.httprequest.user_agent.browser
            context.update({ 'location': f"{geoip['city']}, {geoip['country_name']}" if geoip else None, 
                             'device': device and device.capitalize() or None, 
                             'browser': browser and browser.capitalize() or None,
                             'ip': request.httprequest.environ['REMOTE_ADDR'], })
        # to note : the project_manager_id is related to the project and there is no key('project_manager_id') in the vals.
        project_manager_id = self.env['project.project'].sudo().search([('id', '=', int(vals['project_id']))]).user_id
        is_project_manager = False
        to_project_manager = False
        # duplicated condition to ensure the update of the request_status
        if project_manager_id.id == self.env.user.id:
            is_project_manager = True
            vals['request_status'] = 'pending'
        if vals.get('date_from') and vals.get('catalog_id'):
            catalog_id = self.env['thiqah_project.service_catalog'].sudo().browse(vals['catalog_id'])
            vals['sla_end_date'] = vals['date_from'] + timedelta(days=catalog_id.sla)
        # get the workflow depending on the service catalog
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'thiqah.project.service.request')])
        workflow_id = request.env['workflow.workflow'].sudo().search([('model_id', '=', model_id.id)]).filtered(lambda r: vals['catalog_id'] in r.criteria_ids.mapped('criteria_id'))
        if workflow_id:
            #Just in case if search return more than one workflow which is not possible by business
            workflow_id = workflow_id[0]
            state_ids = workflow_id.state_ids.filtered(lambda r: r.flow_start == True)
            vals['state'] = state_ids[0].technical_name if state_ids else False
        res = super(RequestService, self).create(vals)
        
        #if no workflow found ==> nothing to to
        if not workflow_id:
            return res
        allowed_users = self.env['res.users']
        transition_id = workflow_id.transition_ids.filtered(lambda r: r.sequence == 0)
        for transition_validation_id in transition_id.transition_validation_ids:
            if transition_validation_id.is_project_manager:
                to_project_manager = True
        if is_project_manager and to_project_manager:
            for action in workflow_id.action_ids:
                action.transition_id.trigger_transition(res.id, self._name)
                break
        # get users for workflow_validation | Groups Domain
        for validation in transition_id.transition_validation_ids:
            if validation.type == 'by_user': 
                allowed_users += validation.get_dedicated_users(res)
            else:
                for group in validation.group_ids:
                    allowed_users += group.users
        for allowed_user in allowed_users.ids:
            notif_id = self.env['notification.system'].sudo().create({
                'message_id': get_random_string(23),
                'name': _('Service Request Assignment'),
                'description': _('You need to do action to this service request: ' + vals['sequence']),
                'user_id': allowed_user,
                'url_redirect': res.get_change_status_url(),
                'model_id': res.id,
                'model_name': 'thiqah.project.service.request'
            })
            notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
        res.send_mail_notification(allowed_users)
        # Let the client submit wihtout any odoo core restriction.
        res = res.sudo()
        if allowed_users:
            res.concerned_user_ids = [(6, 0, allowed_users.ids)]
            res.traceability_actors_ids = [(6, 0, allowed_users.ids)]
        
        # if is_project_manager:
        #     # delete from the concerned users to enusre the visibility of the requests .
        #     self.env.cr.execute( "DELETE FROM service_actor_rel WHERE actor_id = %s", tuple([concerned_user.id]))
        return res

    def unlink(self):
        """
        restrict the ungroup action for those who do not belong to the project manager group.
        """
        if self.user_has_groups('base.group_system'):
            result = super().unlink()
            return result

        if not self.user_has_groups('project.group_project_manager'):
            raise UserError(
                _('You cannot perform this action, please contact your administrator.'))

        # Restrict deleting a request when there are replies
        # string frozen , don't touch
        body = '<p>Attached files : </p>'
        for message_id in self.message_ids:
            if message_id.message_type == 'comment':
                if message_id.body == body:
                    continue

                raise UserError(
                    _("You cannot delete the request because it has already been discussed in the replies area."))

        result = super().unlink()
        return result

    # Methods for Computed Fields
    @api.onchange('sla')
    def _compute_sla_end_date(self):
        """
        compute the sale end date based on the date of request.
        """
        for rec in self:
            if rec.date_from:
                rec.sla_end_date = rec.date_from + timedelta(days=rec.sla)

    @api.onchange('sla')
    def _compute_actual_working_date(self):
        """
        compute the sale end date based on the date of request.
        Constraint: The request should be in progess.
        """
        for request_service in self:
            if request_service.create_date:
                result = datetime.now().date() - request_service.create_date.date()
                result = result.days
                request_service.actual_working_date = result

    @api.onchange('sla_end_date', 'create_date')
    def _compute_remaining_day(self):
        """
        compute the sla end date based on the sla and the actual working date.
        """
        for request_service in self:
            result = request_service.sla - request_service.actual_working_date
            request_service.remaining_day = result

    def get_project_manager(self):
        return self.project_manager_id

    def get_project_accountant(self):
        return self.project_accountant_id

    def get_project_vp(self):
        return self.vp_id

    def get_director_finance(self):
        return self.director_finance_id

    # For the HR Process (Customization)
    def get_priority_user(self, sequence):
        if sequence == 0:
            return self.get_project_manager()
        if sequence == 1:
            return self.get_line_manager()
        if sequence == 2:
            return self.get_project_accountant()
        if sequence == 3:
            return self.get_project_vp()
        return False

    # --------------------------------------------------
    # Portal tools
    # --------------------------------------------------

    def reject_request(self):
        self.write({
                'state': 'reject',
                'request_status': 'rejected'
            })

    def get_display_request_state(self):
        """
        Get the display state of the service request.
        :return: the repr string of the current state
        :rtype: str
        """
        self.ensure_one()
        return dict(self._get_state_items()).get(self.state), self.state

    # Override this to inject the permission of the use in the forms.
    def _register_hook(self):
        result = super()._register_hook()
        self.allows_model_in_forms()
        return result

    access_url_custom = fields.Char(
        'Portal Access URL Custom', compute='_compute_access_url',
        help='Customer Portal URL')

    def get_portal_url_custom(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url_custom + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    def _compute_access_url(self):
        super(RequestService, self)._compute_access_url()
        # for request in self.filtered(lambda request: request.is_active()):
        # TODO: Uses keep_query()
        for request in self:
            request.access_url_custom = '/my/request/page/%s' % (
                request.id) + '?mode=view'

            request.access_url = '/my/requests/%s' % (
                request.id) + '?mode=view'

    def get_portal_url_preview(self):
        for request in self:
            return request.access_url

    def get_change_status_url(self):
        for request in self:
            return '/my/requests/%s' % (
                request.id) + '?mode=change_status'

    def compute_request_status(self):
        self._compute_request_status()
 
    @api.depends('is_in_progress', 'state')
    def _compute_request_status(self):
        for rec in self:
            active_state, active_state_technical = rec.get_display_request_state()
            if rec.is_in_progress:
                self.write({'request_status': 'pending'})
            if active_state_technical == 'rejected':
                rec.write({'request_status': 'rejected'})

    def preview_service_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url_preview(),
        }

    # --------------------------------------------------
    # Report tools
    # --------------------------------------------------

    def _get_name_request_report(self):
        """ This method need to be inherit if there is need to to print a custom report instead of
        the default one. """
        self.ensure_one()
        return 'thiqah_project.report_service_request_document'

    def _get_service_request_display_name(self):
        ''' Helper to get the display name of an service request depending of the project and the manager.
        :return:            A string representing the service request.
        '''
        self.ensure_one()
        name = 'request_'
        return name + 'by_' + self.user_id.name + '_for_' + self.project_id.name

    def _get_report_base_filename(self):
        return self._get_service_request_display_name()

    # --------------------------------------------------
    # Dashboard tools
    # --------------------------------------------------

    is_active = fields.Boolean()
    is_late = fields.Boolean(default=False)
    is_due_date = fields.Boolean(default=False)
    is_on_time = fields.Boolean(default=True)

    # Cron Job to ensure the Sla Indicator
    def sla_indicator_cron(self):
        """or purly techincal prupose , we need to ensure the sla indicator wiht a cron job to bypass a unusefuull compute triggger."""
        # get all service requests
        request_ids = self.env[self._name].sudo().search([('is_done', '!=', True)])
        no_sla_request_ids = request_ids.filtered(lambda r: r.sla == 0)
        no_sla_request_ids.write({'sla_indicator': 'n_a', 'is_on_time': True, 'is_late': False})
        sla_request_ids = request_ids - no_sla_request_ids
        for service_request in sla_request_ids:
            # On Time
            if service_request.sla_end_date and service_request.sla_end_date > date.today():
                service_request.write({
                        'is_on_time': True,
                        'is_late': False,
                        'is_due_date': False,
                        'sla_indicator': 'on_time'
                    })
            # Late
            elif service_request.sla_end_date and service_request.sla_end_date < date.today():
                service_request.write({
                            'is_late': True,
                            'is_active': False,
                            'is_due_date': False,
                            'sla_indicator': 'late'
                        })
            # Today Due Date | Check
            elif service_request.sla_end_date:
                service_request.write({
                        'is_due_date': True,
                        'is_late': False,
                        'is_on_time': True,
                        'sla_indicator': 'on_time'
                    })
            #No SLA End Date
            else:
                service_request.write({
                        'is_due_date': False,
                        'is_late': False,
                        'is_on_time': False,
                        'sla_indicator': 'n_a'
                    })
            
