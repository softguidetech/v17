# -*- coding: utf-8 -*-


from odoo import models, fields, _, api
from odoo.osv.expression import AND
from datetime import date


MODEL_LOGINS = 'auditlog.login'
MODEL_REQUESTS = 'auditlog.log'


class userAnalysisReport(models.TransientModel):
    _name = 'user.analysis.report'

    report_type_ids = fields.Many2many('user.category')

    type = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
    ], default='pdf', required=True)

    analysis_type = fields.Selection([
        ('login', 'Logins'),
        ('request', 'Requests'),
    ], default='login', required=True)

    def _get_report_type_items(self):
        return [(report_type.code, report_type.name) for report_type in self.env['user.category'].sudo().search([])]

    @api.model
    def _compute_default_state(self):
        """
        .
        """
        return self._get_report_type_items()[0]

    report_types = fields.Selection(
        _get_report_type_items, string="Report Type(s)")

    date_start = fields.Date()
    date = fields.Date()

    def name_get(self):
        return [(analysis.id, analysis.analysis_type) for analysis in self]

    def _get_report_base_filename(self):
        """."""
        if self.analysis_type == 'login':
            return _("Users Logins Report")

        if self.analysis_type == 'request':
            return _("Users Requests Report")

    def _get_ref_categories(self):
        return self.report_type_ids

    def _get_domain(self):
        if self.report_type_ids:
            domain = [
                ('user_id.thiqah_category_id', 'in', self._get_ref_categories().ids)
            ]
        if self.analysis_type == 'request' or not self.report_type_ids:
            domain = []

        if self.date_start and self.date:
            domain = AND([domain, [
                ('create_date', '>=', self.date_start),
                ('create_date', '<=', self.date)
            ]])

        return domain

    def _format_period(self):
        """."""
        if self.date_start and self.date:
            return 'CXP adaptation report from ' + self.date_start.strftime('%Y-%m-%d')+' To '+self.date.strftime('%Y-%m-%d')
        else:
            return 'CXP adaptation report in all periods'

    def _update_values(self, values, data):
        """."""
        values.update(
            {'get_data': data,
                'analysis_type': self.analysis_type,
                'header': self._format_period()
            }
        )
        return values

    def _get_logins(self, values):
        """."""
        # Prepare Domain
        domain = self._get_domain()
        # gathering login data for the traceability.
        audit_login = self.env[MODEL_LOGINS].sudo().search(domain)
        get_logins = []
        i = 1
        for record in audit_login:
            get_logins.append({
                'row': i,
                'user': record.user_id.name if record.user_id.id else '',
                'login_date': record.create_date if record.create_date else '',
                'redirect_to': record.redirect_to,
            })
            i += 1

        values = self._update_values(values, get_logins)
        return values

    def _formatting_method(self, audit_request):
        """."""
        if audit_request.method == 'write':
            return 'edit'
        elif audit_request.method == 'unlink':
            return 'delete'
        else:
            return audit_request.method

    def _get_requests(self, values):
        """."""
        # Prepare Domain
        domain = self._get_domain()
        users_ids = []
        # get category
        category_ids = False
        if self.report_type_ids:
            category_ids = self._get_ref_categories()
            # get the user by categroy ==> gathering from the log by user_id(res_id)
            users_ids = self.env['res.users'].search([('thiqah_category_id', 'in', category_ids.ids)]).ids

            domain = AND([domain, [('user_id', 'in', users_ids)]])
        else:
            domain = AND([domain, [('user_id', '!=', None)]])
        # gathering login data for the traceability.(Period Filtering)
        audit_requests = self.env[MODEL_REQUESTS].sudo().search(domain)
        get_requests = []
        i = 1
        for audit_request in audit_requests:
            # Extra Condition
            if not audit_request.user_id.name == 'OdooBot':
                get_requests.append({
                    'row': i,
                    'user_id': audit_request.user_id.name,
                    'create_date': audit_request.create_date,
                    'category_type': audit_request.user_id.thiqah_category_id.name,
                    # 'resource_name': audit_request.name if audit_request.method == 'write' else audit_request.user_id.name,
                    # 'http_request': audit_request.http_request_id.name_get()[0][1],
                    'method': self._formatting_method(audit_request),
                })
                i += 1
        values = self._update_values(values, get_requests)
        return values

    def get_thiqah_user_analysis_data(self):
        """."""
        values = {}
        # gathering Data.
        if self.analysis_type == 'login':
            return self._get_logins(values)
        if self.analysis_type == 'request':
            return self._get_requests(values)
        return values

    def action_report_print(self):
        if self.type == 'pdf':
            return self.env.ref('thiqah_base.user_analysis_report_pdf').report_action(self)
        if self.type == 'xlsx':
            return self.env.ref('thiqah_base.user_analysis_report_xlsx').report_action(self,data={'user_analysis_data' : self.get_thiqah_user_analysis_data()})
