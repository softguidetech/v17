# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import ast
import base64
import json
from ...thiqah_base.controllers import thiqah_portal

import logging

_logger = logging.getLogger(__name__)

MODEL_NAME = 'project.project'


class ProjectCustom(thiqah_portal.ThiqahPortal):

    def _get_domain(self, criteria):
        # Only users with sp manager group can see all data.
        current_partner = request.env.user.partner_id
        domain = [(criteria, '=', current_partner.id)]
        if request.env.user.has_group('project.group_project_manager'):
            domain = []
        return domain

    def _get_project_project_data(self):
        values = {}

        # Clients
        values['customers'] = request.env['res.partner'].sudo().search(
            [
                ('is_customer', '=', True),
                ('shown_in_portal', '=', True)
            ])

        # Contract types
        values['contract_types'] = request.env['thiqah.project.contract.type'].sudo().search([
        ])

        # Project Status

        # Project Managers

        values['project_managers'] = request.env['res.users'].sudo().search([
            ('share', '=', False)
        ])

        if request.env.user.has_group('thiqah_project.project_manager_group'):
            current_partner = request.env.user.partner_id
            domain = [('id', '=', current_partner.id)]
            values['project_managers'] = request.env['res.users'].sudo().search([
                ('share', '=', False), ('id', '=', request.env.user.id)
            ])

        # HR Department
        values['departments'] = request.env['hr.department'].sudo().search(
            [('active', '=', True)])

        # Project Risk Types
        values['risk_types'] = request.env['thiqah.project.risk.type'].sudo().search([
        ])

        # Project Risk Types
        values['document_types'] = request.env['document.type'].sudo().search([
        ])

        values['currency'] = request.env.ref(
            'base.main_company').currency_id.name

        return values

    @http.route('/project/form', auth='user', website=True)
    def render_form(self, **kw):
        if not self.can_access_route('project_management', 'read') or not self.can_access_route('project_management', 'create'):
            return request.redirect('/access/access_denied')
        values = self._get_project_project_data()
        return http.request.render('thiqah_project.project_add_template', values)

    @http.route('/project/update/action', type='json', website=True)
    def update_project(self, **kw):
        """
        This method ensures the updating of a project in question
        depending from the new data sending from frontend.
        """
        # Gathering Data
        project_id = kw['project_id'] if 'project_id' in kw else 0,

        values = {
            'name': kw['name'] if 'name' in kw else 0,
            'name_arabic': kw['name_arabic'] if 'name_arabic' in kw else 0,
            'contract_type_id': kw['contract_type_id'] if 'contract_type_id' in kw else 0,
            'date_start': kw['date_start'] if 'date_start' in kw else 0,
            'date': kw['date'] if 'date' in kw else 0,
            'project_value': kw['project_value'] if 'project_value' in kw else 0,
            'user_id': int(kw['user_id']) if 'user_id' in kw else 0
        }

        try:
            return request.env[MODEL_NAME].sudo().browse(
                [int(project_id[0])]).write(values)
        except Exception as exception:
            print(str(exception))

    @http.route('/project/subelement/unlink', auth='user', website=True)
    def unlink_subelemt(self, model_name, record_id):
        """."""
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        result = request.env[model_name].sudo().browse(
            [int(record_id)]).unlink()

        return str(result) if result else str(False)

    @http.route('/project/form/add', auth='user',type='http', website=True,csrf=False)
    def add_project(self, **kw):
        """."""
        project_project = request.env[MODEL_NAME].sudo()
        project_data = {}

        # --------------------------------------------------
        # Basic Data
        # --------------------------------------------------
        try:
            # for the basic data , there is no need to add another test on the value itself, because every things will be controlled from the inputs.
            # These fields are required.
            project_data.update({
                'thqiah_project_number': kw['project_number'],
                'name': kw['name'],
                'name_arabic': kw['name_arabic'],
                'date_start': kw['date_start'],
                'partner_id': int(kw['partner_id']),
                'date': kw['basic_date'],
                'project_value': kw['project_value'],
                # 'state': kw['state'],
                'contract_type_id': int(kw['contract_type_id']),
                'user_id': int(kw['user_id'])
            })

            # --------------------------------------------------
            # Project Overall Summary
            # --------------------------------------------------

            # handling date(s)
            if 'financial_report_date' in kw:
                if kw['financial_report_date']:
                    project_data.update({
                        'financial_report_date': kw['financial_report_date']
                    })

            if 'remaining_balance_date' in kw:
                if kw['remaining_balance_date']:
                    project_data.update({
                        'remaining_balance_date': kw['remaining_balance_date']
                    })

            # Extension
            project_data.update({
                'duration': kw['duration'] if 'duration' in kw else False,
                'vat': kw['vat'] if 'vat' in kw else False,
                'rev_plan_na': kw['rev_plan_na'] if 'rev_plan_na' in kw else False,
                'total_commitments': kw['total_commitments'] if 'total_commitments' in kw else False,
                'commitments_pos': kw['commitments_pos'] if 'commitments_pos' in kw else False,
                'cost_spending_limit': kw['cost_spending_limit'] if 'cost_spending_limit' in kw else False,
                'commitments_miscellaneous': kw['commitments_miscellaneous'] if 'commitments_miscellaneous' in kw else False,
            })

            project_data.update({
                # MP Actual Cost
                'number_headcount': kw['number_headcount'] if 'number_headcount' in kw else False,

                # change from total_manpower_cost to total_cost_mp
                'total_cost_mp': kw['total_cost_mp'] if 'total_cost_mp' in kw else False,
                # change from forecasted_cost to total_cost_mp && Extension
                'commitments_mp': kw['commitments_mp']if 'commitments_mp' in kw else False,

                # Project and Supply Actual Cost
                'number_of_pos': kw['number_of_pos'] if 'number_of_pos' in kw else False,
                'total_actual_cost': kw['total_actual_cost'] if 'total_actual_cost' in kw else False,
                # change from open_po_amount to cost_spending_limit
                'cost_spending_limit': kw['cost_spending_limit'] if 'cost_spending_limit' in kw else False,
                # change from po_forecasted_cost to actual_cost_pos
                'actual_cost_pos': kw['actual_cost_pos'] if 'actual_cost_pos' in kw else False,

                #  Miscellaneous Actual Cost
                # change from total_miscellaneous to actual_total_miscellaneous
                'actual_total_miscellaneous': kw['actual_total_miscellaneous'] if 'actual_total_miscellaneous' in kw else False,
                # 'miscellaneous_forecasted_cost': kw['miscellaneous_forecasted_cost'] if 'miscellaneous_forecasted_cost' in kw else False,

                # Total utilization and Remaining balance
                # 'total_margin_vat': kw['total_margin_vat'] if 'total_margin_vat' in kw else False,
                'remaining_balance': kw['remaining_balance'] if 'remaining_balance' in kw else False,


                # Total utilization and project expectations with remaining budget
                'total_utilization_expectations': kw['total_utilization_expectations'] if 'total_utilization_expectations' in kw else False,
                # change from available_budget to balance_after_commitment
                'available_budget': kw['available_budget'] if 'available_budget' in kw else False,

                # Invoices
                # change total_amount_billed to billed_amount
                'billed_amount': kw['billed_amount'] if 'billed_amount' in kw else False,

                # change total_amount_received to collected_amount
                'collected_amount': kw['collected_amount'] if 'collected_amount' in kw else False,

                # 'outstanding_amount': kw['outstanding_amount'] if 'outstanding_amount' in kw else False,

                # Extension
                'billed_amount_no_vat': kw['billed_amount_no_vat'] if 'billed_amount_no_vat' in kw else False,
                # Extension
                'contract_unbilled_revenues': kw['contract_unbilled_revenues'] if 'contract_unbilled_revenues' in kw else False,
                # Extension
                'due_amount': kw['due_amount'] if 'due_amount' in kw else False,
                # 'cash_position': kw['cash_position'] if 'cash_position' in kw else False,

                # Acutal Cost
                'margin_percent': kw['margin_percent'] if 'margin_percent' in kw else False,
                'actual_cost': kw['actual_cost'] if 'actual_cost' in kw else False,
                'actual_margin_amount': kw['actual_margin_amount'] if 'actual_margin_amount' in kw else False,
                'actual_revenue': kw['actual_revenue'] if 'actual_revenue' in kw else False,
                # 'actual_margin_percent': kw['actual_margin_percent'] if 'actual_margin_percent' in kw else False,
                'requester_id': request.env.user.id
            })

            # --------------------------------------------------
            # Project Resources
            # --------------------------------------------------
            resource_ids = ast.literal_eval(kw['resource_ids'])
            if resource_ids != 0:
                project_data.update({
                    'resource_ids': resource_ids
                })

            # --------------------------------------------------
            # Risk and issues
            # --------------------------------------------------
            risk_ids = ast.literal_eval(kw['risk_ids'])
            if risk_ids != 0:
                project_data.update({
                    'risk_ids': risk_ids
                })

            # --------------------------------------------------
            # Revenue Plans
            # --------------------------------------------------
            revenue_plan_ids = ast.literal_eval(kw['revenue_plan_ids'])
            if revenue_plan_ids != 0:
                project_data.update({
                    'revenue_plan_ids': revenue_plan_ids
                })

            # --------------------------------------------------
            # Deliverables
            # --------------------------------------------------
            deliverable_ids = ast.literal_eval(kw['deliverable_ids'])
            if deliverable_ids != 0:
                project_data.update({
                    'deliverable_ids': deliverable_ids
                })

            # --------------------------------------------------
            # Utilizations
            # --------------------------------------------------
            utilization_ids = ast.literal_eval(kw['utilization_ids'])
            if utilization_ids != 0:
                project_data.update({
                    'utilization_ids': utilization_ids
                })

            # do_action
            project_id = project_project.create(project_data)

            # --------------------------------------------------
            # Documents
            # --------------------------------------------------
            document_ids = ast.literal_eval(kw['documents_ids'])
            if isinstance(document_ids,list) and len(document_ids)>0 and len(document_ids[0])>2:
                project_documents = request.env['documents.document'].sudo().browse(
                    document_ids[0][2])
                for project_document in project_documents:
                    project_document.update({
                        'res_id': project_id.id
                    })
            return json.dumps({"status":"success","Message":project_id.name})

        except Exception as exception:
            _logger.exception(
                "Error when adding project: %s" % exception)
            return json.dumps({"status":"failed","Message":"Somthing went wrong"})

    @http.route('/project/risk/new', type='json', website=True)
    def add_risks_new(self, **kwargs):
        """."""

        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        risks_new = []
        if 'risks_new' in kwargs and 'project_id' in kwargs:
            risks_new = ast.literal_eval(kwargs['risks_new'])
            project_id = int(kwargs['project_id'])

            if risks_new and project_id:
                for risk_new in risks_new:
                    result = request.env['thiqah.project.risk'].browse([
                        int(risk_new)
                    ]).sudo().write({
                        'project_id': int(project_id)
                    })
                if result:
                    return result
                else:
                    return False

    @http.route('/project/resource/new', type='json', website=True)
    def add_resources_new(self, **kwargs):
        """."""

        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        resources_new = []
        if 'resources_new' in kwargs and 'project_id' in kwargs:
            resources_new = ast.literal_eval(kwargs['resources_new'])
            project_id = int(kwargs['project_id'])

            if resources_new and project_id:
                for resource_new in resources_new:
                    result = request.env['thiqah.project.resource'].browse([
                        int(resource_new)
                    ]).sudo().write({
                        'project_id': int(project_id)
                    })
                if result:
                    return result
                else:
                    return False

    @http.route('/project/revenue/new', type='json', website=True)
    def add_revenues_new(self, **kwargs):
        """."""

        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        revenues_new = []
        if 'revenues_new' in kwargs and 'project_id' in kwargs:
            revenues_new = ast.literal_eval(kwargs['revenues_new'])
            project_id = int(kwargs['project_id'])

            if revenues_new and project_id:
                for revenue_new in revenues_new:
                    result = request.env['thiqah.revenue.plan'].browse([
                        int(revenue_new)
                    ]).sudo().write({
                        'project_id': int(project_id)
                    })
                if result:
                    return result
                else:
                    return False

    @http.route('/project/resource/update', type='json', website=True)
    def update_resource(self, **kwargs):
        """."""
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        parameters = {
            'department_id': kwargs['department_id_update'] if 'department_id_update' in kwargs else None,
            'user_id': kwargs['user_id_update'] if 'user_id_update' in kwargs else None,
            'other_resource': kwargs['other_update'] if 'other_update' in kwargs else None,
        }

        # do the action
        if 'resource_id' in kwargs:
            if kwargs['resource_id']:

                result = request.env['thiqah.project.resource'].browse([
                    int(kwargs['resource_id'])
                ]).sudo().write(parameters)
                if result:
                    return result
                else:
                    return False

    @http.route('/project/revenue/update', type='json', website=True)
    def update_revenue(self, **kwargs):
        """."""
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        parameters = {
            'invoice_date': kwargs['invoice_date_update'] if 'invoice_date_update' in kwargs else None,
            'payment_date': kwargs['payment_date_update'] if 'payment_date_update' in kwargs else None,
            'amount_billed': kwargs['amount_billed_update'] if 'amount_billed_update' in kwargs else None,
            'amount_received': kwargs['amount_received_update'] if 'amount_received_update' in kwargs else None,
            'amount_due': kwargs['revenue_status_update'] if 'revenue_status_update' in kwargs else None,
            'status': kwargs['amount_received_update'] if 'amount_received_update' in kwargs else None,
        }

        # do the action
        if 'revenue_id' in kwargs:
            if kwargs['revenue_id']:

                result = request.env['thiqah.revenue.plan'].browse([
                    int(kwargs['revenue_id'])
                ]).sudo().write(parameters)
                if result:
                    return result
                else:
                    return False

    @http.route('/project/risk/update', type='json', website=True)
    def update_risk_issue(self, **kwargs):
        """."""
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        parameters = {
            'name': kwargs['name_risk_update'] if 'name_risk_update' in kwargs else None,
            'description': kwargs['description_risk_update'].strip() if 'description_risk_update' in kwargs else None,
            'owner': kwargs['owner_risk_update'] if 'owner_risk_update' in kwargs else None,
            'corrective_action': kwargs['corrective_action_update'].strip() if 'corrective_action_update' in kwargs else None,
            'level_impact': kwargs['level_impact_update'] if 'level_impact_update' in kwargs else None,
            'risk_status': kwargs['risk_status_update'] if 'risk_status_update' in kwargs else None,
            'risk_type_id': int(kwargs['risk_type_id_update']) if 'risk_type_id_update' in kwargs else None,
        }
        # do the action
        if 'risk_id' in kwargs:
            if kwargs['risk_id']:

                result = request.env['thiqah.project.risk'].browse([
                    int(kwargs['risk_id'])
                ]).sudo().write(parameters)
                if result:
                    return result
                else:
                    return False

    @http.route([
        '/my/project/delete/<int:project_id>',
    ], type='json', auth="public", website=True)
    def delete_project(self, project_id, access_token=None, **kw):
        """."""
        service_request_sudo = self.check_access(project_id, access_token)
        project_sudo = request.env[MODEL_NAME].sudo().browse([int(project_id)])

        if request.env.user.has_group('base.group_project_user'):
            result = project_sudo.unlink()
            return result

        # Restrict deleting

        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        if project_sudo:
            result = project_sudo.unlink()
            if not result:
                return False
        return True

    @http.route([
        '/my/risk/delete/<int:risk_id>',
    ], type='json', auth="public", website=True)
    def delete_risk(self, risk_id, access_token=None, **kw):
        """."""
        # Restrict deleting
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        risk_sudo = request.env['thiqah.project.risk'].sudo().browse([
            int(risk_id)])

        if risk_sudo:
            result = risk_sudo.unlink()
            if not result:
                return False
        return True

    @http.route([
        '/my/resource/delete/<int:resource_id>',
    ], type='json', auth="public", website=True)
    def delete_resource_project(self, resource_id, access_token=None, **kw):
        """."""
        # Restrict deleting
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        resource_sudo = request.env['thiqah.project.resource'].sudo().browse([
            int(resource_id)])

        if resource_sudo:
            result = resource_sudo.unlink()
            if not result:
                return False
        return True

    @http.route('/project/document/add', type='http', auth='public', methods=['POST'], website=True)
    def add_project_document(self, name, file, res_id=None, res_model=None, access_token=None, **kwargs):
        """
        .
        """
        if not request.env.user.has_group('project.group_project_user'):
            return 'unauthorized'

        # create attachment.
        attachment = request.env['ir.attachment'].create({
            'name': name,
            'datas': base64.b64encode(file.read()),
            'res_model': 'project.project',
            'res_id': 0,
            'access_token': access_token,
        })

        # link the previous attachment with a new document.
        document = request.env['documents.document'].sudo().create({
            'name': 'Document-' + str(name),
            'type': 'binary',
            'res_model': 'project.project',
            'res_id': 0,
            'folder_id': 1,
            'attachment_id': attachment.id if attachment else False
        })
        return request.make_response(
            data=json.dumps(document.read(
                ['id', 'name', 'mimetype', 'file_size'])[0]),
            headers=[('Content-Type', 'application/json')]
        )
