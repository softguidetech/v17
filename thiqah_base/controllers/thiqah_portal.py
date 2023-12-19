# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.osv.expression import AND
from odoo.http import request


class ThiqahPortal(http.Controller):

    def can_access_route(self, service, record_id=False):
        """
        List of services:
        home_dashboard, fin_dashboard,
        service_request, project_management, task_dashboard, customer_centricity
        inquiry_request, freelance_request, freelance_workorder, utilization_report
        client_payment, client_registration
        """
        user_id = request.env.user
        has_access = True
        if service == 'fin_dashboard':
            if not user_id.check_service_access('fin_dashboard') or user_id.has_group('thiqah_project.group_portal_department'):
                has_access = False
        elif service == 'inquiry_request':
            if (not user_id.check_service_access('inquiry_request') and (not record_id or record_id.sudo().user_id.id != user_id.id)):
                has_access = False
        else:
            has_access = user_id.check_service_access(service)
        return has_access

    def _get_manager_projects(self):
        return request.env['project.project'].sudo().search([
            ('active', '=', True), ('user_id', '=', request.env.user.id)
        ])

    def render_domain_request_owner(self):
        """
        this method is used to assign for each request the corresponding user domain.
        there are 3 types of users:
            + Project Manager
            + Department Employee.
            + Client.

        :return : list containing the correspond domain.
        """
        domain = []
        # for the department employees, render only the data related to their departments.
        if request.env.user.has_group('thiqah_project.group_portal_department'):
            # Add Deparmtent constraint
            if request.env.user.employee_id:
                domain = AND([domain,
                              [
                                  ('department_id', '=',
                                   request.env.user.employee_id.department_id.id)
                              ]
                              ])
            else:
                raise AccessError(
                    _('There is no employee related to the current user!'))
        # for the project manager group
        elif request.env.user.has_group('thiqah_project.project_manager_group'):
            project_ids = self._get_manager_projects()
            domain = AND([
                domain, [('project_id', 'in', project_ids.ids)]
            ])
        elif request.env.user.has_group('base.group_portal'):
            domain = AND([
                domain, [('client_id', 'in', request.env.user.partner_id.id)]
            ])

        return domain
    
    def external_users_permission(self):
        if request.env.user.has_group('base.group_portal'):
            # check the groups dedicated to the external users (Portal or Public)
            quality_assurance_group_id = request.env.ref(
                'thiqah_project.quality_assurance_group')

            if quality_assurance_group_id.id in request.env.user.get_external_group_ids():
                domain = AND([domain, domain])
            else:
                return '404 Not found'
