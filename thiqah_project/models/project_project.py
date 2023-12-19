# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

from odoo.osv.expression import AND, OR


_content_selection = [
    ('pending', 'Pending'),
    ('base_line', 'Base Line'),
    ('in_progress', 'In Progress'),
    ('closing', 'Closing'),
]


class ProjectExtension(models.Model):
    _inherit = 'project.project'

    # --------------------------------------------------
    # Basic Data
    # --------------------------------------------------

    # name_en == name
    # sequence = fields.Char(string='Project Number', required=True,
    #                        readonly=True, default=lambda self: _('New'))

    thqiah_project_number = fields.Char('Project Number')

    name_arabic = fields.Char('Project name(Arabic)')

    name = fields.Char('Project name')

    date_start = fields.Date('Start Date')

    date = fields.Date('Completion Date')

    currency_id = fields.Many2one('res.currency')

    project_value = fields.Monetary(
        'Budget (value)', currency_field='currency_id')

    state = fields.Selection(
        _content_selection, default=_content_selection[0][0])

    requester_id = fields.Many2one('res.users')

    department_id = fields.Many2one(related='requester_id.department_id')

    thiqah_department_id = fields.Many2one(
        related='user_id.employee_id.department_id', store=True)

    service_catalog_id = fields.Many2one(
        'thiqah_project.service_catalog', compute='compute_service_catalog')

    # Project accountant
    project_accountant_id = fields.Many2one(
        'res.users', string='Project accountant')
    # _id
    vp = fields.Many2one(
        'res.users', string='VP', domain=[('is_vp', '=', True)])

    # _id
    director_finance = fields.Many2one(
        'res.users', domain=[('is_director_finance', '=', True)])
    
    line_manager_id = fields.Many2one(related='user_id',string='',)
    hr_business_partner_id = fields.Many2one(
        'res.users', string='HR Business Partner', domain=lambda self: [('groups_id.id', '=', self.env.ref('thiqah_base.group_hr_business_partner').id)])

    # Outil form record rule
    user_rule_id = fields.Many2one('res.users')

    # Outil for conversion to project.
    lead_id = fields.Many2one('crm.lead')

    # Co-field One2many with the res.partner to ensure the filter in the financial dahsboard
    partner_id_financial = fields.Many2one('res.partner')

    # Extension:
    duration = fields.Char(string='Duration')  # OK && main.py

    client_id = fields.Many2one('res.partner', string='Client')  # OK

    vat = fields.Monetary(string='VAT')  # OK && main.py

    rev_plan_na = fields.Monetary(string='Rev plan NA')  # OK && main.py

    actual_cost_pos = fields.Monetary(string='Actual Cost “Pos”')  # OK

    commitments_mp = fields.Monetary(string='Commitments “MP”')  # OK

    commitments_pos = fields.Monetary(string='Commitments “Pos”')  # OK

    commitments_miscellaneous = fields.Monetary(
        string='Commitments Miscellaneous')  # OK

    total_commitments = fields.Monetary(
        string='Total commitments')  # OK && main.py

    billed_amount_no_vat = fields.Monetary(
        string='Billed amount “without VAT”')  # OK

    contract_unbilled_revenues = fields.Monetary(
        string='Contract as “unbilled revenues”')  # OK

    contract_liability = fields.Monetary(
        string='Contract liability')  # OK

    # Outil for Notification && assignment to the project manager concerned
    assing_to_id = fields.Many2one('res.users')

    @staticmethod
    def get_active_project_managers(cr):
        sql_query = '''
                SELECT user_id
                FROM project_project
                WHERE active = true;
            '''
        cr.execute(sql_query)
        return list(set([proj['user_id'] or False for proj in cr.dictfetchall()]))
    
    @staticmethod
    def get_active_project_accountant_managers(cr):
        sql_query = '''
                SELECT project_accountant_id
                FROM project_project
                WHERE active = true;
            '''
        cr.execute(sql_query)
        return list(set([proj['project_accountant_id'] or False for proj in cr.dictfetchall()]))
    
    @staticmethod
    def get_active_project_hrbp(cr):
        sql_query = '''
                SELECT hr_business_partner_id
                FROM project_project
                WHERE active = true;
            '''
        cr.execute(sql_query)
        return list(set([proj['hr_business_partner_id'] or False  for proj in cr.dictfetchall()]))
    
    def compute_service_catalog(self):
        for project in self:
            project.service_catalog_id = self.env['thiqah_project.service_catalog'].search([
                ('department_id', '=', project.department_id.id)
            ], limit=1).id

    def _compute_progress_percent(self):
        for project in self:
            present_date = date.today()
            if project.date_start and project.date:
                date_start = project.date_start
                date_end = project.date

                # expected_duration
                expected_duration = date_end - date_start
                expected_duration = expected_duration.days

                # elapsed_duration
                elapsed_duration = present_date - date_start
                elapsed_duration = elapsed_duration.days

                if elapsed_duration >= 0 and expected_duration > 0:
                    percent = (elapsed_duration / expected_duration) * 100

                    percent = float("{:.2f}".format(percent))
                    if percent >= 100.00:
                        percent = '100'
                else:
                    percent = 'N/A'

                project.progress_percent = str(percent) + '%'
            else:
                project.progress_percent = 'N/A'

    progress_percent = fields.Char(compute=_compute_progress_percent)

    requests_count = fields.Integer(
        'Service Requests Count', compute='_compute_requests_count')

    def _compute_requests_count(self):
        """."""
        for project in self:
            project.requests_count = self.env['thiqah.project.service.request'].sudo().search_count([
                ('project_id', '=', project.id)
            ])

    # Change Status Actions
    def _set_pending(self):
        for project in self:
            result = project.write({
                'state': 'pending'
            })
            return result

    def _set_base_line(self):
        for project in self:
            result = project.write({
                'state': 'base_line'
            })
            return result

    def _set_in_progress(self):
        for project in self:
            result = project.write({
                'state': 'in_progress'
            })
            return result

    def _set_closing(self):
        for project in self:
            result = project.write({
                'state': 'closing'
            })
            return result

    def preview_project_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url_preview(),
        }

    # Relations
    contract_type_id = fields.Many2one('thiqah.project.contract.type')

    @api.model
    def create(self, vals):
        """
        override the create method to add sequence processing.
        Purpose : Record Rules bypass.
        """
        res = super(ProjectExtension, self).create(vals)
        if vals.get('user_id', False):
            user_id = self.env['res.users'].sudo().browse([int(vals['user_id'])])
            user_id.write({'thiqah_projects_ids': [(6, 0, [res.id])]})
        return res

    # --------------------------------------------------
    # Project Overall Summary
    # --------------------------------------------------

    financial_report_date = fields.Date(default="2030-07-20")

    # MP Actual Cost
    number_headcount = fields.Integer(
        string='Total of HC', help='Number Of headcount.')  # OK

    total_cost_mp = fields.Monetary(
        string='Actual cost (MP)', help='Total manpower Actual Cost.', currency_field='currency_id')  # OK

    forecasted_cost = fields.Monetary(
        help='Project expiration.', currency_field='currency_id')

    # Project and Supply Actual Cost
    number_of_pos = fields.Float(
        string='Total Pos', help='Total Number of POs.')  # OK

    total_actual_cost = fields.Monetary(
        help='Total Actual Cost', currency_field='currency_id')  # OK

    open_po_amount = fields.Monetary(
        help='Open PO Amount(Not billed) Not Input Vat.', currency_field='currency_id')

    cost_spending_limit = fields.Monetary(
        string='Cost plan “spending limit”', currency_field='currency_id')  # OK

    #  Miscellaneous Actual Cost
    actual_total_miscellaneous = fields.Monetary(
        string='Actual Cost Miscellaneous', currency_field='currency_id')  # OK

    miscellaneous_forecasted_cost = fields.Monetary(
        help='Forecasted Cost.', currency_field='currency_id')

    # Total utilization and Remaining balance
    total_margin_vat = fields.Monetary(
        string="Total Utilization with Margin and VAT", currency_field='currency_id')

    remaining_balance = fields.Monetary(
        string='Actual Available Balance', currency_field='currency_id')  # OK

    remaining_balance_date = fields.Date()

    # Total utilization and project utilization with remaining budget
    total_utilization_expectations = fields.Monetary(
        help='Total utilization and Project Expectations.', currency_field='currency_id', default=0.00)

    # change from available_budget to balance_after_commitment
    available_budget = fields.Monetary(
        string='Balance after Commitment', currency_field='currency_id', default=0.00)  # Ok

    # Invoices
    billed_amount = fields.Monetary(
        string='Billed Amount', currency_field='currency_id', default=0.00)  # OK
    collected_amount = fields.Monetary(
        string='Collected Amount', currency_field='currency_id', default=0.00)  # OK
    due_amount = fields.Monetary(
        string='Due Amount', currency_field='currency_id', default=0.00)  # OK

    cash_position = fields.Monetary(
        help='Cash Position.', currency_field='currency_id', default=0.00)

    # Acutal Cost
    margin_percent = fields.Float(string='Margin %', help='Margin %.')  # OK
    actual_cost = fields.Monetary(
        help='Actual Cost', currency_field='currency_id', default=0.00)  # OK
    # actual_margin_amount = fields.Monetary(
    #     help='Actual Margin Amount.', currency_field='currency_id')
    actual_margin_amount = fields.Monetary(
        string='Margin', currency_field='currency_id')  # OK

    actual_revenue = fields.Monetary(string='Actual Revenue',
                                     help='Actual Revenue.', currency_field='currency_id', default=0.00)  # OK

    actual_margin_percent = fields.Float(string='Actual Margin %',
                                         help='Actual Margin %.')

    # --------------------------------------------------
    # Project Resources
    # --------------------------------------------------

    resource_ids = fields.One2many('thiqah.project.resource', 'project_id')

    # --------------------------------------------------
    # Risk and issues
    # --------------------------------------------------

    risk_ids = fields.One2many('thiqah.project.risk', 'project_id')

    # --------------------------------------------------
    # Revenue Plans
    # --------------------------------------------------

    revenue_plan_ids = fields.One2many('thiqah.revenue.plan', 'project_id')

    # --------------------------------------------------
    # Deliverables
    # --------------------------------------------------

    deliverable_ids = fields.One2many(
        'thiqah.project.deliverable', 'project_id')

    # --------------------------------------------------
    # Utilizations
    # --------------------------------------------------

    utilization_ids = fields.One2many(
        'thiqah.project.utilization', 'project_id')

    # --------------------------------------------------
    # Documents
    # --------------------------------------------------

    document_ids = fields.One2many('documents.document', 'project_id')

    # Documents
    documents_count = fields.Integer(
        compute='_compute_documents_count', string="File")

    def _compute_documents_count(self):
        for project in self:
            project.documents_count = self.env['documents.document'].search_count([
                ('res_model', '=', self._name), ('res_id', '=', project.id)
            ])

    def action_open_documents(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'documents.document_action')
        action['domain'] = [('res_model', '=', 'project.project'),
                            ('res_id', '=', self.id)]

        return action

    # --------------------------------------------------
    # Core Tools
    # --------------------------------------------------

    def allows_model_in_forms(self):
        """
        .
        """
        ir_model = self.env['ir.model'].sudo()
        service_request_model = ir_model.search([
            ('model', '=', self._name)
        ])
        if not service_request_model.website_form_access:
            service_request_model.write({
                'website_form_access': True
            })
            return True
        pass

    # Override this to inject the permission of the use in the forms.
    def _register_hook(self):
        result = super()._register_hook()
        self.allows_model_in_forms()
        return result

    # --------------------------------------------------
    # Portal Tools
    # --------------------------------------------------

    def project_get_portal_domain(self):
        domain = []
        if self.env.user.has_group('thiqah_project.project_manager_group'):
            # Then, he is internal user, and we take the domain for this current user.
            # return self.env['ir.rule']._compute_domain(self._name)
            return []

        if self.env.user.partner_id.is_customer:
            if self.env.user.has_group('base.group_portal'):
                project_ids = self.env['project.project'].sudo().search([
                    ('partner_id', '=', self.env.user.partner_id.id)
                ])
                domain = AND([
                    domain, [('id', 'in', project_ids.ids)]
                ])
                return domain

        # TODO : If he is not an internal user(Portal User),
        # and we should prepare the domain from scratch.
        return domain

    @api.model
    def _get_states(self):
        """."""
        states = [item[1] for item in _content_selection]
        return states

    @api.model
    def _get_states_values(self):
        """."""
        states = [item[0] for item in _content_selection]
        return states

    def get_display_project_state(self):
        """
        Get the display state of the current project.
        :return: the repr string of the current state
        :rtype: str
        """
        self.ensure_one()
        return dict(_content_selection).get(self.state)

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
        super(ProjectExtension, self)._compute_access_url()
        # for request in self.filtered(lambda request: request.is_active()):
        for request in self:
            request.access_url_custom = '/my/project/page/%s' % (
                request.id) + '?mode=view'

            request.access_url = '/my/projects/%s' % (
                request.id) + '?mode=view'

    def get_portal_url_preview(self):
        for request in self:
            return request.access_url
