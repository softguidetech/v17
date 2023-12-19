# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from decimal import *
from odoo.osv.expression import AND, OR
from odoo.exceptions import AccessError
from ...thiqah_base.controllers import thiqah_portal
import json
import ast
import pandas as pd
from datetime import date

from ...thiqah_crm.models.crm_lead import aahd_source_content


def human_format(num):
    if num:
        # set decimal default options!
        getcontext().prec = 1
        getcontext().rounding = ROUND_DOWN

        _num = Decimal(num)
        num = float(f'{_num:.3g}')

        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        num = int(num * 10) / 10
        return f"{f'{num:f}'.rstrip('0').rstrip('.')}{['', 'k', 'M', 'B', 'T'][magnitude]}"


def apply_humain_format(result, to_include):
    for x, y in result.items():
        if x in to_include:
            if result[x] != None:
                result[x] = human_format(y)
            else:
                result[x] = '0'
    return result


class ServiceRequest(thiqah_portal.ThiqahPortal):

    def _get_domain(self, criteria):
        # Only users with project manager group can see all data.
        current_partner = request.env.user.partner_id
        domain = [(criteria, '=', current_partner.id)]
        if request.env.user.has_group('project.group_project_manager'):
            domain = []
        if request.env.user.has_group('base.group_portal'):
            # check the groups dedicated to the external users (Portal or Public)
            quality_assurance_group_id = request.env.ref('thiqah_project.quality_assurance_group')
            vp_group_id = request.env.ref('thiqah_project.vp_group')
            if quality_assurance_group_id.id in request.env.user.get_external_group_ids() or vp_group_id.id in request.env.user.get_external_group_ids():
                domain = []
        return domain

    def _get_manager_projects(self):
        return request.env['project.project'].sudo().search([
            ('active', '=', True), ('user_id', '=', request.env.user.id)
        ])

    # --------------------------------------------------
    # Dashboard tools
    # --------------------------------------------------

    # Access Rights (Portal permissin)
    def _service_request_check_access(self, domain):
        # for the department employees, render only the data related to their departments.
        if request.env.user.has_group('thiqah_project.group_portal_department'):
            # Add Deparmtent constraint
            if request.env.user.employee_id:
                domain = AND([domain,
                              [('department_id', '=',
                                   request.env.user.employee_id.department_id.id)
                              ]])
            else:
                raise AccessError(_('There is no employee related to the current user !'))

        # for the project manager group
        if request.env.user.has_group('thiqah_project.project_manager_group'):
            domain = []
            # get current user's all projects.
            project_ids = self._get_manager_projects()
            domain = AND([domain, [('project_id', 'in', project_ids.ids)]])

        if request.env.user.has_group('base.group_portal'):
            domain = self._get_domain('client_id')

            vp_group_id = request.env.ref(
                'thiqah_project.vp_group')

            if vp_group_id.id in request.env.user.get_external_group_ids():
                domain = AND([domain,
                              [('vp_id', '=',
                                   request.env.user.id)
                              ]])
        return domain

    def get_count_by_criteria(self, model, criteria, indice, values, field_id, is_field=None, shown_in_portal=None, expand_domain=None):
        """
        Only For Relationship Models.
        """
        # get all criteria data
        criteria_datas = request.env[criteria].sudo().search([
            (is_field, '=', True),
            (shown_in_portal, '=', True)
        ]) if is_field else request.env[criteria].sudo().search([])

        xValues = []
        yValues = []
        domain = self._get_domain('client_id')

        if expand_domain:
            domain = AND([domain, expand_domain])

        if not expand_domain:
            # Check access: render only the data related to their specification.
            domain = self._service_request_check_access(domain)

        for criteria_data in criteria_datas:
            xValues.append(criteria_data.name_get()[0][1])
            yValues.append(
                request.env[model._name].sudo().search_count(
                    AND([domain, [(field_id, '=', criteria_data.id)]])
                )
            )
        values[indice] = [xValues, yValues]

        return values

    def exceute_select_query(self, query):
        request.env.cr.execute(query)
        return request.env.cr.dictfetchall()

    @http.route('/get/projects/details', type="http", methods=['GET'], website=True)
    def render_projects_details(self):
        """
        :return list(lists)
        """
        # project_number,project_name,project_manager,requests_counts
        response = {}
        # domain = self._service_request_check_access([])

        grouped_projects = request.env['project.project'].sudo().search([])

        projects_details_data = []
        for grouped_project in grouped_projects:
            projects_details_data.append(
                [
                    grouped_project.thqiah_project_number,
                    grouped_project.name,
                    grouped_project.user_id.name,
                    request.env['thiqah.project.service.request'].sudo().search_count([
                        ('project_id', '=', grouped_project.id)
                    ])
                ]
            )

        response.update({
            'projects_details_data': projects_details_data
        })

        try:
            return json.dumps(response)
        except Exception as exception:
            return str(exception)

    @http.route('/render/dashboard/data', type='json', auth='user', website=True)
    def render_chart_dashboard_data(self, **kw):
        """
        .
        """
        values = {}
        dashboard_name = kw['dashboard']
        domain = self._get_domain('client_id')

        ordered_dict_params = request.params
        params = dict(ordered_dict_params)
        project_id = params.get('project_id', False)

        if dashboard_name == 'requests_dashboard':
            service_requests = request.env['thiqah.project.service.request'].sudo().search([
            ])

            # By Creation date
            # by_creation_date_count = []  # Format = {x:'',y:''}

            # TODO : this section needs more optimization.
            base_query = """
                SELECT date_trunc('day',create_date) upd_time,
                COUNT (*) AS total
                FROM thiqah_project_service_request
            """
            if domain:
                base_query += 'where '+str(domain[0][0]) + \
                    '=' + str(domain[0][2]) + ' '

            if project_id:
                base_query += 'and project_id='+str(project_id)
                expand_domain = [('project_id', '=', int(project_id))]
                domain = AND([domain, expand_domain])
            else:
                expand_domain = None

            group_by = """
                GROUP BY date_trunc('day',create_date)
                ORDER BY date_trunc('day',create_date) asc;
            """
            base_query += group_by
            request.env.cr.execute(base_query)

            if request.env.user.has_group('thiqah_project.project_manager_group'):
                base_query = """
                SELECT date_trunc('day',create_date) upd_time,
                COUNT (*) AS total
                FROM thiqah_project_service_request
                where project_id IN %s
                """
                base_query += group_by

                # projects = request.env['project.project'].sudo().search([
                #     ('user_id', '=', request.env.user.id)
                # ])

                projects = self._get_manager_projects()

                # self.env.cr.execute(f"DELETE FROM {attachments._table} WHERE id IN %s", [
                #                     tuple(attachments.ids)])
                request.env.cr.execute("""
                                        SELECT date_trunc('day',create_date) upd_time,COUNT (*) AS total
                                        FROM thiqah_project_service_request where project_id IN %s
                                        GROUP BY date_trunc('day',create_date)
                                        ORDER BY date_trunc('day',create_date) asc;
                                        """, [
                    tuple(projects.ids)
                ])

            results = request.env.cr.fetchall()
            # for result in results:
            #     by_creation_date_count.append(
            #     )
            min_max = []
            if results:
                min_max = [
                    results[0][0], results[-1][0]
                ]

            results.append(min_max)
            values['byCreateDate'] = results

            # # By Status
            # get all states linked to the service request.
            ir_model = request.env['ir.model'].sudo()

            model_id = ir_model.search([
                ('model', '=', 'thiqah.project.service.request')
            ])

            workflows = request.env['workflow.workflow'].sudo().search([
                ('model_id', '=', model_id.id)
            ])
            all_states = []
            for workflow in workflows:
                all_states.append(request.env['workflow.engine'].sudo(
                )._get_state_items(workflow))

            all_states = [item for sublist in all_states for item in sublist]

            by_status = []
            values_ = []
            xValues = []
            yValues = []

            domain = self._service_request_check_access(domain)

            for state_tuple in all_states:
                values_.append(state_tuple[1])
                by_status.append(
                    (
                        state_tuple[0],
                        state_tuple[1],
                        service_requests.search_count(
                            AND([domain, [('state', '=', state_tuple[0])]])
                        )
                    )
                )

            # Link each count to a state
            values_ = set(values_)
            values_ = list(values_)
            final_by_status = []

            for value in values_:
                count = 0
                for status in by_status:
                    if value == status[1]:
                        count += int(status[2])

                xValues.append(value)
                yValues.append(count)

                final_by_status.append(
                    (value, count)
                )
                count = 0

            values['byStatus'] = [xValues, yValues]

            # Requests By Department
            values = self.get_count_by_criteria(
                service_requests, 'hr.department', 'byDepartment', values, 'department_id', None, None, expand_domain)

            # By SLA Indicator
            # get all criteria data
            # ('sla_indicator', '=', sla_indicator)

            xValues = ['Late', 'On Time', 'N/A']
            yValues = []
            sla_indicators = ['late', 'on_time', 'n_a']

            for sla_indicator in sla_indicators:
                yValues.append(
                    request.env['thiqah.project.service.request'].sudo().search_count(
                        AND([
                            domain, [('sla_indicator', '=', sla_indicator),
                                     ]
                        ])
                    )
                )

            values['BySlaIndicator'] = [xValues, yValues]

            # By service category
            values = self.get_count_by_criteria(
                service_requests, 'thiqah_project.service_catalog', 'byServiceCategory', values, 'catalog_id', None, None, expand_domain)

            # By Client
            values = self.get_count_by_criteria(
                service_requests, 'res.partner', 'byClient', values, 'client_id', 'is_customer', 'shown_in_portal', expand_domain)

            return values

        elif dashboard_name == 'financial_dashboard':
            project_project = request.env['project.project'].sudo()
            project_count = project_project.search_count([])

            query = """
            select
            count(*) as project_count,
            sum(project_value) as project_value_sum,
            sum(remaining_balance) as available_balance,
            sum(available_budget) as balance_after_commitment,
            sum(cash_position) as cash_position,

            sum(number_headcount) as number_headcount,
            sum(number_of_pos) as number_of_pos,
            sum(margin_percent) as margin_percent,
            sum(actual_margin_percent) as actual_margin_percent,
            sum(actual_margin_amount) as actual_margin_amount,

            sum(total_cost_mp) as actual_mp,
            sum(forecasted_cost) as forecasted_mp,
            sum(open_po_amount) as supply_pos_amount,
            sum(actual_cost_pos) as supply_po_forecasted_cost,
            sum(actual_total_miscellaneous) as miscellaneous_total,
            sum(miscellaneous_forecasted_cost) as miscellaneous_forecasted,

            sum(project_value) as project_value,
            sum(billed_amount) as total_amount_billed,
            sum(collected_amount) as total_amount_received,
            sum(due_amount) as due_amount,
            sum(contract_unbilled_revenues) as contract_unbilled_revenues,
            sum(contract_liability) as contract_liability,
            sum(cost_spending_limit) as cost_spending_limit,
            sum(total_actual_cost) as total_actual_cost,

            sum(total_margin_vat) as total_margin_vat,
            sum(remaining_balance) as remaining_balance,
            sum(billed_amount_no_vat) as billed_amount_no_vat,
            sum(vat) as vat,
            sum(total_actual_cost) as supply_acutal,sum(available_budget) as available_budget,

            sum(commitments_mp) as commitments_mp,
            sum(commitments_pos) as commitments_pos,
            sum(commitments_miscellaneous) as commitments_miscellaneous,
            sum(total_commitments) as total_commitments,
            sum(actual_revenue) as actual_revenue,

            sum(total_utilization_expectations) as total_utilization_expectations
            from project_project
            """
            # Trash ; Query
            # sum(outstanding_amount) as outstanding_amount,sum(total_actual_cost) as supply_acutal,sum(available_budget) as available_budget

            query_copy = [query].copy()
            # get the project_id comming from the redirection from the dashboard user.
            project_id_ = params.get('project_id', False)

            if project_id_:
                if project_id_ == 0:
                    return False

            # Filter
            parms_ = params.get('filter_by_id', False)

            client_id = 0
            project_id = 0
            if parms_:
                params_ = parms_.split('and')
                client_id = params_[0] if int(params_[0]) > 0 else False
                project_id = params_[1] if int(params_[1]) > 0 else False

            domain = self._get_domain('partner_id')

            if domain:
                query += 'where '+str(domain[0][0]) + \
                    '=' + str(domain[0][2]) + ' '

            if client_id and not project_id_:
                if request.env['project.project'].sudo().search([
                    ('partner_id', '=', int(client_id))
                ]):
                    # Inject the condition into the query
                    query += "where partner_id="+str(client_id)

            # handling the filter(s) by project_id
            if project_id:
                query += " and id="+str(project_id)

            if project_id_ and not project_id:
                query += "where id="+str(project_id_)
            result = self.exceute_select_query(query)[0]

            # TODO: handling percent(s)
            if not domain:
                if not client_id and not project_id_:
                    if result['margin_percent'] and result['actual_margin_percent']:
                        if project_count:
                            result['margin_percent'] /= project_count
                            result['actual_margin_percent'] /= project_count

                elif client_id and not project_id:
                    projects_linked_count = request.env['project.project'].sudo().search_count([
                        ('partner_id', '=', int(client_id))
                    ])

                    if result['margin_percent'] and result['actual_margin_percent']:
                        result['margin_percent'] /= projects_linked_count
                        result['actual_margin_percent'] /= projects_linked_count

                elif project_id:
                    project_id = request.env['project.project'].sudo().search([
                        ('id', '=', int(project_id))
                    ])
                    result['margin_percent'] = project_id.margin_percent
                    result['actual_margin_percent'] = project_id.actual_margin_percent

            if domain:
                project_count = request.env['project.project'].sudo().search_count([
                    (domain[0][0], '=', int(domain[0][2]))
                ])
                if project_count and result['margin_percent'] and result['actual_margin_percent']:
                    result['margin_percent'] /= project_count
                    result['actual_margin_percent'] /= project_count

            if result['margin_percent'] and result['actual_margin_percent']:
                result['margin_percent'] = "{:.2f}".format(
                    result['margin_percent'])

                result['actual_margin_percent'] = "{:.2f}".format(
                    result['actual_margin_percent'])

            # Extension
            # TODO: this section need more optimization
            if request.env.user.has_group('thiqah_project.project_manager_group'):
                # projects = request.env['project.project'].sudo().search([
                #     ('user_id', '=', request.env.user.id)
                # ])
                projects = self._get_manager_projects()
                query = query_copy[0] + " where id IN %s"

                request.env.cr.execute(query, [
                    tuple(projects.ids)
                ])

                result = request.env.cr.dictfetchall()[0]

                project_count = result['project_count']
                if project_count and result['actual_margin_percent'] and result['margin_percent']:
                    result['margin_percent'] /= project_count
                    result['actual_margin_percent'] /= project_count

                    result['margin_percent'] = "{:.2f}".format(
                        result['margin_percent'])

                    result['actual_margin_percent'] = "{:.2f}".format(
                        result['actual_margin_percent'])

            # if project_id_ and not project_id:
            #     result['margin_percent'] = project_count
            #     result['margin_percent'] = project_count

            # change from available_project_budgets(available_budget) to balance_after_commitment
            to_include = ['project_value_sum', 'available_balance', 'balance_after_commitment', 'actual_revenue',
                          'total_margin_vat', 'number_of_pos', 'vat', 'actual_margin_amount']

            result = apply_humain_format(result, to_include)

            # Project Utilities Actual Hours ==> Total Utilizations Hours
            actual_hours = 0
            planned_hours = 0
            forecasted_hours = 0
            projects_client = []
            if client_id:
                projects_client = request.env['project.project'].sudo().search([
                    ('partner_id', '=', int(client_id))
                ])
            elif not client_id:
                projects_client = project_project.search([])

            for project_client in projects_client:
                for project_utility in project_client.utilization_ids:
                    actual_hours += int(project_utility.actual_hours)
                    planned_hours += int(project_utility.planned_hours)
                    forecasted_hours += int(project_utility.forecasted_hours)

            result['TotalUtilizationsHours'] = str(actual_hours)

            values['cards_data'] = result

            # CHART(s)
            # Common ( 'Cost Plan')
            x_axis = ['MP', 'POS', 'MISC', 'Total']

            ##################
            # Actual Cost
            ##################
            yValues = [result['actual_mp'], result['forecasted_mp']]

            values['MPActualCost'] = [['Actual', 'Forecasted'], yValues]

            # Actual Cost (MP,POS,MISC,Total,Cost Plan)
            # MP ==> total_cost_mp (actual_mp)
            # POS ==> actual_cost_pos (supply_po_forecasted_cost)
            # MISC ==>  actual_total_miscellaneous (miscellaneous_total)
            # Total ==> total_actual_cost
            # Cost Plan ==> cost_spending_limit
            x_axis_copy = x_axis.copy()
            x_axis_copy.append('Cost Plan')

            yValues = [result['actual_mp'], result['supply_po_forecasted_cost'],
                       result['miscellaneous_total'], result['total_actual_cost'], result['cost_spending_limit']]

            values['ActualCost'] = [x_axis_copy, yValues]

            ##################
            # Commitments
            ##################
            # MP ==> commitments_mp
            # POS ==> commitments_pos
            # MISC ==>  commitments_miscellaneous
            # Total ==> total_commitments

            yValues = [result['commitments_mp'], result['commitments_pos'],
                       result['commitments_miscellaneous'], result['total_commitments']]
            values['Commitments'] = [x_axis, yValues]

            # Miscellaneous Actual Cost
            yValues = [result['miscellaneous_total'],
                       result['miscellaneous_forecasted']]
            values['MiscellaneousActualCost'] = [
                ['Actual', 'Forecasted'], yValues]

            values['ProjectUtilitiesActualHours'] = [['Actual', 'Planned', 'Forecasted'], [
                actual_hours, planned_hours, forecasted_hours]]

            # Invoices (billed_amount,billed_amount_no_vat,collected_amount,,due_amount)
            yValues = [result['total_amount_billed'], result['billed_amount_no_vat'],
                       result['total_amount_received'], result['due_amount']]

            values['ProjectsInvoices'] = [
                ['Billed', 'Billed without VAT', 'Collected', 'Due'], yValues]

            # Contract (Un-billed Revenues,liability)
            yValues = [result['contract_unbilled_revenues'],
                       result['contract_liability']]

            values['Contract'] = [['Un-billed Revenues', 'Liability'], yValues]

            # Total Utilization With Margin And VAT
            yValues = [result['total_margin_vat'],
                       result['remaining_balance'], result['project_value']]
            values['TotalMarginVat'] = [
                ['Actual', 'Remaining', 'Project Value'], yValues]

            # Total Actual utilization With Margin And VAT + Project Expectations
            yValues = [result['total_utilization_expectations'],
                       result['available_budget'], result['project_value']]
            values['TotalMarginVatExpectations'] = [
                ['Actual', 'Remaining', 'Project Value'], yValues]

            # Project And Supply Actual Cost
            yValues = [result['supply_acutal'],
                       result['supply_pos_amount'], result['supply_po_forecasted_cost']]
            values['ProjectSupplyCost'] = [
                ['Actual', 'OpenPOs', 'Forecasted'], yValues]

            return values

    # Financial Dashboard
    @http.route('/my/financial/dashboard', type='http', auth='user', website=True)
    def financial_dashboard(self, filter_by_id=None):
        """."""

        if request.env.user.has_group('thiqah_project.group_portal_department'):
            return '404 Not Found'

        values = {}
        project_project = request.env['project.project'].sudo()
        res_partner = request.env['res.partner'].sudo()
        project_count = project_project.search_count([])

        # Clients
        values['customers'] = res_partner.search(
            [
                ('is_customer', '=', True),
                ('shown_in_portal', '=', True)
            ])

        # Projects
        values['projects'] = request.env['project.project'].sudo().search(
            [('active', '=', True)])

        # Filter for the project manage
        if request.env.user.has_group('thiqah_project.project_manager_group'):
            projects = self._get_manager_projects()

            # get only the customers linked to the projects that self(user) is the project manager.
            partners = []
            for project in projects:
                partners.append(project.partner_id.id)

            values['customers'] = res_partner.browse(partners)

        if request.env.user.has_group('base.group_portal'):
            # check the groups dedicated to the external users (Portal or Public)
            quality_assurance_group_id = request.env.ref(
                'thiqah_project.quality_assurance_group')

            if not request.env.user.partner_id.is_customer:
                if not quality_assurance_group_id.id in request.env.user.get_external_group_ids():
                    return '404 Not found'

        values['is_customer'] = request.env.user.partner_id.is_customer

        return request.render("thiqah_portal.financial_dashboard", values)

    # Department Task Dashboard
    @http.route('/department/task/dashboard', type='http', auth='user', website=True)
    def task_dashboard_action(self, page=1):
        """."""
        if not self.can_access_route('task_dashboard'):
            return request.redirect('/access/access_denied')
        # get requester group(s)
        pass_ = False
        if request.env.user.has_group('thiqah_project.group_portal_department') or request.env.user.has_group('thiqah_project.project_manager_group'):
            pass_ = True
        values = {}

        # Requiring Actions
        requiring_actions = request.env['thiqah.portal.requiring.action'].search([
            ('user_ids', 'in', request.env.user.id)
        ])
        ServiceRequest = request.env['thiqah.project.service.request']
        service_request_sudo = ServiceRequest.sudo()
        domain = self._service_request_check_access([])
        if request.env.user.has_group('base.group_portal'):
            # check the groups dedicated to the external users (Portal or Public)
            quality_assurance_group_id = request.env.ref(
                'thiqah_project.quality_assurance_group')

            if quality_assurance_group_id.id in request.env.user.get_external_group_ids():
                domain = AND([domain, domain])

            pass_ = True
        if not pass_:
            return request.redirect('/access/access_denied')
        requests = service_request_sudo.search(domain)
        request.session['my_requests_history'] = requests.ids[:100]
        grouped_requests = [requests]

        # Service Requests Count
        requests_count = service_request_sudo.search_count(domain)
        values.update({
            'requests': requests,
            'grouped_requests': grouped_requests,
            'page_name': 'service_requests',
            'requests_count': requests_count,
            'requiring_actions': requiring_actions,
            'requiring_actions_count': len(requiring_actions),
            })
        return request.render("thiqah_portal.department_task_dashboard_id", values)

    @http.route('/tasks/api/mydata', type="http", methods=['GET'], website=True)
    def render_json_data(self, access_token=None, **kwargs):
        """."""
        # preparing data
        requiring_actions = request.env['thiqah.portal.requiring.action'].search([
            # ('user_ids', 'in', request.env.user.id)
        ])

        actions_data = []
        for requiring_action in requiring_actions:
            user_ids = ast.literal_eval(requiring_action.users_ids)
            if request.env.user.id in user_ids[0][2]:
                date_time = requiring_action.last_step_created_at.strftime(
                    "%m/%d/%Y") if requiring_action.last_step_created_at else None
                actions_data.append(
                    ['', requiring_action.related_code,
                        requiring_action.service_catalog,
                        'Request Workflow',
                        requiring_action.service_status.upper() if requiring_action.service_status else None,
                        requiring_action.current_step,
                        requiring_action.last_step,
                        requiring_action.last_step_created_by.name,
                        date_time,
                        requiring_action.service_request_id
                     ]
                )

        response = {
            'requiring_actions': actions_data
        }

        # servcice requests
        domain = self._service_request_check_access([])

        grouped_requests = request.env['thiqah.project.service.request'].sudo().search(
            domain)

        requests_data = []
        for grouped_request in grouped_requests:
            requests_data.append(
                [grouped_request.sequence,
                 grouped_request.project_id.name,
                 grouped_request.client_id.name,
                 grouped_request.user_id.name,
                 grouped_request.sla,
                 grouped_request.sla_indicator,
                 grouped_request.department_id.name,
                 grouped_request.catalog_id.name_en,
                 grouped_request.state.upper() if grouped_request.state else None,
                 ]
            )

        response.update({
            'service_requests_task': requests_data
        })

        # draft requests
        draft_requests = request.env['thiqah.portal.draft.request'].sudo().search([
        ])
        draft_requests_ = []
        for draft_request in draft_requests:
            date_time = draft_request.date.strftime(
                "%m/%d/%Y") if draft_request.date else None
            draft_requests_.append(
                [
                    draft_request.partner_to,
                    draft_request.partner_from,
                    draft_request.assign_to,
                    draft_request.assign_number,
                    # draft_request.date,
                    date_time,
                    draft_request.subject,
                ]
            )

        response.update({
            'draft_requests': draft_requests_
        })
        try:
            return json.dumps(response)
        except Exception as exception:
            return str(exception)

    # @http.route('/tasks/manager/mydata', type="http", methods=['GET'], website=True)
    # def render_json_data(self, access_token=None, **kwargs):
    #     """."""
    #     # preparing data
    #     requiring_actions = request.env['thiqah.portal.requiring.action'].search([
    #         # ('user_ids', 'in', request.env.user.id)
    #     ])

    #     actions_data = []
    #     for requiring_action in requiring_actions:
    #         user_ids = ast.literal_eval(requiring_action.users_ids)
    #         if request.env.user.id in user_ids[0][2]:
    #             date_time = requiring_action.last_step_created_at.strftime(
    #                 "%m/%d/%Y") if requiring_action.last_step_created_at else None
    #             actions_data.append(
    #                 ['', requiring_action.related_code,
    #                     requiring_action.service_catalog,
    #                     'Request Workflow',
    #                     requiring_action.service_status.upper() if requiring_action.service_status else None,
    #                     requiring_action.current_step,
    #                     requiring_action.last_step,
    #                     requiring_action.last_step_created_by.name,
    #                     date_time,
    #                     requiring_action.service_request_id
    #                  ]
    #             )

    #     response = {
    #         'requiring_actions': actions_data
    #     }

    #     # servcice requests
    #     domain = self._service_request_check_access([])

    #     grouped_requests = request.env['thiqah.project.service.request'].sudo().search(
    #         domain)

    #     requests_data = []
    #     for grouped_request in grouped_requests:
    #         requests_data.append(
    #             [grouped_request.sequence,
    #              grouped_request.project_id.name,
    #              grouped_request.client_id.name,
    #              grouped_request.user_id.name,
    #              grouped_request.sla,
    #              grouped_request.sla_indicator,
    #              grouped_request.department_id.name,
    #              grouped_request.catalog_id.name_en,
    #              grouped_request.state.upper() if grouped_request.state else None,
    #              ]
    #         )

    #     response.update({
    #         'service_requests_task': requests_data
    #     })

    #     # draft requests
    #     draft_requests = request.env['thiqah.portal.draft.request'].sudo().search([
    #     ])
    #     draft_requests_ = []
    #     for draft_request in draft_requests:
    #         date_time = draft_request.date.strftime(
    #             "%m/%d/%Y") if draft_request.date else None
    #         draft_requests_.append(
    #             [
    #                 draft_request.partner_to,
    #                 draft_request.partner_from,
    #                 draft_request.assign_to,
    #                 draft_request.assign_number,
    #                 # draft_request.date,
    #                 date_time,
    #                 draft_request.subject,
    #             ]
    #         )

    #     response.update({
    #         'draft_requests': draft_requests_
    #     })

    #     try:
    #         return json.dumps(response)
    #     except Exception as exception:
    #         return str(exception)

    # Department Manager Task Dashboard
    # @http.route('/department/manager/dashboard', type='http', auth='user', website=True)
    # def manager_dashboard_action(self, page=1):
    #     """."""

    #     if request.env.user.has_group('thiqah_project.group_portal_department'):
    #         return '404 Not Found'

    #     values = {}

    #     return request.render("thiqah_portal.manager_task_dashboard_id", values)

    @http.route('/aahd/sales/dashboard', type='json', website=True)
    def render_aahd_sales_dashboard(self, **kw):
        """."""
        values = {}
        filter_year = int(kw['year'])
        filter_date_from = date.today().replace(year=filter_year,month=1,day=1)
        filter_date_to = date.today().replace(year=filter_year,month=12,day=31)
        won_stage_id = request.env['crm.stage'].sudo().search([('is_won', '=', True)])
        current_year = int(date.today().strftime("%Y"))
        # Add another restriction services not null (product_for_filter_id)
        # Expliclity domain(s)

        base_domain = [
            ('for_aahd', '=', True), ('stage_id', '!=', False),
                  ('type', '=', 'opportunity'), ('is_wathiq', '=', False),
        ]
        domain_won = AND([base_domain,[ ('product_for_filter_id', '!=', None),('date_open_won',">=",filter_date_from),('date_open_won',"<=",filter_date_to),('stage_id','in',won_stage_id.ids),('active', 'in', [True, False])]])
        domain_lost = AND([base_domain,[('create_date',">=",filter_date_from),('create_date',"<=",filter_date_to),'|',('probability', '=', 0.0),('active', '=', False)]])
        domain_active = AND([base_domain,[('stage_id','not in',won_stage_id.ids),('probability', '!=', 0.0),('active', '=', True),('is_global_archived', '=', False)]])
        
        crm_lead_sudo = request.env['crm.lead'].sudo()
        won_opportunities = crm_lead_sudo.search(domain_won)
        active_opportunities = crm_lead_sudo.search(domain_active)
        lost_opportunities = crm_lead_sudo.search(domain_lost)

        # Total of Opportunities | by default , the orm don't retrieve the inactive record so i will add the number of the lost opportunities explicitly without modify the domain as naive solution.
        # And especially to avoid any side effect (s) because the first doamin is shared by multiple ORM methods as things progress.

        total_opportunities = len(won_opportunities) + len(lost_opportunities) + len(active_opportunities)
        margin = sum(won_opportunities.mapped('profit_margin')) / len(won_opportunities) if won_opportunities else 0.0
        values['margin_percent'] = str(margin) + '%'
        values['total_opportunities'] = total_opportunities
        values['non_digital_opportunities'] = crm_lead_sudo.search_count(
                                                AND([domain_won, [
                                                    ('is_non_digital_aahd', '=', True)
                                                ]])) 

        values['digital_opportunities'] = crm_lead_sudo.search_count(
                                            AND([domain_won, [
                                                ('is_digital_aahd', '=', True)
                                            ]]))
        ############################
        # distribution chart(s)
        ############################
        # opportunity received product
        # get services
        xValues_product = []
        yValues_product = []
        products_amount = []
        for service in request.env['product.template'].sudo().search([('detailed_type', '=', 'service')]):
            xValues_product.append(service.display_name)
            crm_products_filter = request.env['crm.lead'].sudo().search(
                AND([domain_won, [('product_for_filter_id', '=', service.id)]])
            )
            # get sum of Won Proposal Amount(s)
            products_amount.append(str(sum([r.won_revenue for r in crm_products_filter])))
            # get the number of opportunities
            yValues_product.append(len(crm_products_filter))
        values['distributionProduct'] = [xValues_product, yValues_product, products_amount]

        # opportunity received source
        xValues_source = []
        yValues_source = []

        for source in aahd_source_content:
            xValues_source.append(source[1])
            yValues_source.append(request.env['crm.lead'].sudo().search_count(
                    AND([domain_won, [
                        ('aahd_source', '=', source[0])
                    ]])
                ))
        values['distributionSource'] = [xValues_source, yValues_source]

        base_status = {
            'proposal': ['under_development'],
            'submission': ['awarded', 'draft', 'rejected', 'cancelled'],
        }

        status = ['awarded', 'draft', 'under_development', 'rejected', 'cancelled']

        yValues_non_digital = []
        yValues_digital = []
        constraint_status = ''
        for status_ in status:
            domain_copy = OR([domain_won.copy(), domain_active.copy()])
            if status_ in base_status['proposal']:
                # domain_copy = AND([domain_copy, [('stage_is_proposal', '=', True)]])
                constraint_status = 'proposal_status'

            elif status_ in base_status['submission']:
                # domain_copy = AND(
                #     [domain_copy, ['|', ('stage_is_submitted', '=', True), ('is_opportunity_won', '=', True)]])
                constraint_status = 'submission_status'

            yValues_non_digital.append(
                request.env['crm.lead'].sudo().search_count(
                    AND([domain_copy, [(constraint_status, '=', status_),
                        ('is_non_digital_aahd', '=', True)]])
                )
            )

            yValues_digital.append(
                request.env['crm.lead'].sudo().search_count(
                    AND([domain_copy, [(constraint_status, '=', status_),
                        ('is_digital_aahd', '=', True)]])
                )
            )

        xValues_statistics = ['Awarded', 'Submitted', 'Under Development', 'Rejected', 'Cancelled']

        values['distributionNonDigital'] = [xValues_statistics, yValues_non_digital]
        values['distributionDigital'] = [xValues_statistics, yValues_digital]

        domain = AND(
            [domain_won, [('is_opportunity_won', '=', True),
                      ('profit_margin', '>', 0.00)]]
        )
        revenues_won_stage = 0.00
        won_oppotunities = crm_lead_sudo.search(domain_won)
        for won_oppotunity in won_oppotunities:
            revenues_won_stage += won_oppotunity.won_revenue

        # Distribution |  opportunity value chart | won , lost(active=False)
        lost_amount = 0.00
        lost_opportunities = crm_lead_sudo.search(domain_lost)
        for lost_opportunity in lost_opportunities:
            lost_amount += float(lost_opportunity.won_revenue)

        # Exclude the expected value from any winning opportunity
        expected_opportunites = request.env['crm.lead'].search(domain_active)
        expected_revenue_all = sum(
            opportunity_stage.expected_revenue for opportunity_stage in expected_opportunites)

        revenues_all = revenues_won_stage + lost_amount + expected_revenue_all

        xValues_opportunity_value = ['Won', 'Lost', 'Expected Opps', 'Total']
        yValues_opportunity_value = [
            revenues_won_stage,
            lost_amount,
            expected_revenue_all,
            revenues_all
        ]

        won_oppotunities_count = len(won_oppotunities)
        lost_opportunities_count = len(lost_opportunities)
        expected_opportunites_count = len(expected_opportunites)

        all_opportunites = won_oppotunities_count + \
            lost_opportunities_count + expected_opportunites_count

        opportunity_value_counts = [
            won_oppotunities_count, lost_opportunities_count, expected_opportunites_count, all_opportunites]

        values_rate = [
            "{:.2f}".format((revenues_won_stage/revenues_all)
                            * 100) + '%' if revenues_all > 0.00 else 'N/A',

            "{:.2f}".format((lost_amount/revenues_all)*100) +
            '%' if revenues_all > 0.00 else 'N/A',

            "{:.2f}".format((expected_revenue_all/revenues_all)
                            * 100) + '%' if revenues_all > 0.00 else 'N/A',

            # Total
            101

        ]

        quantities_rate = [

            "{:.2f}".format((won_oppotunities_count / total_opportunities)
                            * 100) + '%' if total_opportunities > 0.00 else 'N/A',

            "{:.2f}".format((lost_opportunities_count / total_opportunities)*100) +
            '%' if total_opportunities > 0.00 else 'N/A',

            "{:.2f}".format((expected_opportunites_count / total_opportunities)
                            * 100) + '%' if total_opportunities > 0.00 else 'N/A',
            101
        ]
        values['OpportunityValueChart'] = [
            xValues_opportunity_value, yValues_opportunity_value, opportunity_value_counts, values_rate, quantities_rate]

        value_winning_rate = ''
        if revenues_all > 0:
            value_winning_rate_ = (revenues_won_stage / revenues_all) * 100
            value_winning_rate = str("{:.2f}".format(
                value_winning_rate_)) + '%'
        else:
            value_winning_rate = 'N/A'

        values['value_winning_rate'] = str(value_winning_rate)

        #####################################
        # Quantity Value Rate
        #####################################
        count_won_oppotunities = crm_lead_sudo.search_count(
                AND([domain_won, [('is_opportunity_won', '=', True)]])
            )

        quantity_value_rate = ''
        if total_opportunities > 0:
            quantity_value_rate_ = (count_won_oppotunities / total_opportunities) * 100
            quantity_value_rate = str("{:.2f}".format(quantity_value_rate_)) + '%'
        else:
            quantity_value_rate = 'N/A'

        values['quantity_value_rate'] = str(quantity_value_rate)

        margin = 0.00
        margin_max = request.env.user.company_id.margin_max if request.env.user.company_id.margin_max else ''
        margin_min = request.env.user.company_id.margin_min if request.env.user.company_id.margin_min else ''
        values['margin_min'] = str(margin_min) + '%' if margin_min else 'N/A'
        values['margin_max'] = str(margin_max) + '%' if margin_max else 'N/A'
        if margin_min == 0.00:
            values['margin_min'] = str(0) + '%'

        if margin_max == 0.00:
            values['margin_max'] = str(0) + '%'

        margin_won_oppotunities_ = crm_lead_sudo.search(domain_won)
        revenue_margin = sum([
            opportunity_stage.profit_margin * opportunity_stage.won_revenue for opportunity_stage in margin_won_oppotunities_])

        won_oppotunities_revenue = sum(
            [opportunity_stage.won_revenue for opportunity_stage in margin_won_oppotunities_])

        margin_ = None
        if won_oppotunities_revenue > 0.00:
            margin_ = revenue_margin / won_oppotunities_revenue
            margin = str("{:.1f}".format(margin_)) + '%'
        else:
            margin = 'N/A'

        values['margin_percent'] = str(margin)

        #####################################
        # Goal
        #####################################

        goal_growth = request.env.user.company_id.growth_goal if request.env.user.company_id.growth_goal else ''
        margin_value = None
        if goal_growth and margin_:
            margin_value = (revenues_won_stage/100)*int(margin_)
            # margin_value = human_format(margin_value)

        values['margin_value'] = margin_value

        goal = 0.00
        if goal_growth:
            if goal_growth > 0:
                goal_ = (revenues_won_stage / goal_growth) * 100

                result = 100-goal_
                goal_status = None
                if result < 0:
                    goal_ = 100 + abs(result)
                    goal_status = True
                    values['goal_status'] = goal_status
                elif result > 0:
                    goal_ = abs(result)
                    goal_status = False
                    values['goal_status'] = False
                elif result == 100.0:
                    goal_status = 'no_status'
                    values['goal_status'] = goal_status

                goal = str("{:.1f}".format(goal_)) + '%'

            else:
                goal = 'N/A'

        values['goal_percent'] = str(goal)

        values['goal_growth'] = str(goal_growth)
        values['revenues_won_stage'] =str(revenues_won_stage)

        # Monthly revenue
        if filter_year == current_year:
            results = self.exceute_select_query(
                """
                select to_char(date_open_won,'Mon') as month,
                extract(month from date_open_won) as month_number,
                sum(won_revenue) as current_sale
                from crm_lead
                where is_opportunity_won is true and active is true and is_wathiq is false
                and date_part('year', date_open_won) = date_part('year', CURRENT_DATE)
                group by 1,2
                order by month_number
            """)
        else:
            results = self.exceute_select_query(
                """
                select to_char(date_open_won,'Mon') as month,
                extract(month from date_open_won) as month_number,
                sum(won_revenue) as current_sale
                from crm_lead
                where is_opportunity_won is true and active is true and is_wathiq is false
                and date_part('year', date_open_won) = date_part('year', CURRENT_DATE) - 1
                group by 1,2
                order by month_number
            """)

        xValues_monthly = []
        yValues_monthly = []

        for result in results:
            xValues_monthly.append(
                result['month'] if result['month'] else 'N/A')
            yValues_monthly.append(
                result['current_sale'] if result['current_sale'] else 0.00)

        values['MonthlyRevenue'] = [xValues_monthly, yValues_monthly]

        # Monthly growth
        # To calculate your month to month growth percentage, subtract the current month’s
        # revenue from the previous month, then divide the answer by the previous month’s
        # revenue and multiply by 100.
        # https://textexpander.com/blog/how-to-calculate-your-companys-sales-growth-rate#:~:text=To%20calculate%20your%20month%20to,revenue%20and%20multiply%20by%20100.

        # data={'Date':['Karan','Rohit','Sahil','Aryan'],'Value':[23,22,21,24]}

        xValus_growth = []
        yValues_growth = []
        if xValues_monthly and yValues_monthly:
            data = {'Date': xValues_monthly, 'Value': yValues_monthly}
            df = pd.DataFrame(data)

            # Clean The dataframe from the N/A.
            df.drop(df[df['Date'] == 'N/A'].index, inplace=True)

            df['Date'] = pd.to_datetime(
                df['Date'], format='%b').dt.to_period('M')

            df = df.set_index('Date')
            df = df.reindex(pd.period_range(
                df.index.min(), df.index.max(), freq='M'))
            df.index = df.index.strftime('%b')
            df = df.rename_axis('date').reset_index()
            df['otm'] = df.Value.diff()

            df = df.fillna(0)
            df = df.to_dict()

            date_df = df['date']
            values_df = df['Value']
            otm_df = df['otm']

            for x, y in values_df.items():
                xValus_growth.append(date_df[x])
                yValues_growth.append(
                    (int(otm_df[x])/values_df[x-1])*100 if x-1 >= 0 and values_df[x-1] > 0 else 0)

        # Monthly Growth Rate Formula  = (Current Month Value – Prior Month Value) / Prior Month Value
        values['MonthlyGrowth'] = [xValus_growth, yValues_growth]

        # Top 10 Projects Awarded
        if filter_year == current_year:
            query = """
                        select name,won_revenue
                        from crm_lead as lead_
                        where is_opportunity_won is true and active is true and is_wathiq is false and for_aahd is true
                        and date_part('year', date_open_won) = date_part('year', CURRENT_DATE)
                        order by won_revenue desc limit 10
                        """
        else:
            query = """
                select name,won_revenue
                from crm_lead as lead_
                where is_opportunity_won is true and active is true and is_wathiq is false and for_aahd is true
                and date_part('year', date_open_won) = date_part('year', CURRENT_DATE) - 1
                order by won_revenue desc limit 10
                """

        request.env.cr.execute(query)
        results_awarded = request.env.cr.fetchall()

        projects_awarded = []
        for project_awarded in results_awarded:
            projects_awarded.append((project_awarded[0], project_awarded[1]))

        # delete duplcated lead_.name
        values['projectsAwarded'] = projects_awarded
        return values

    @http.route('/check/is/customer', type='json', website=True)
    def check_is_customer(self, **kw):
        return request.env['res.users'].sudo().browse([int(kw['user_id'])]).is_customer
