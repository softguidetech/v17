# -*- coding:utf-8 -*-
from odoo import fields, http, _, SUPERUSER_ID
from odoo.http import Response, request
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import AND, OR
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict
from operator import itemgetter
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.exceptions import AccessError, MissingError
from .main import ServiceRequest
import json
from datetime import date
from ...thiqah_base.models.tools import get_random_string

MODEL_NAME = 'thiqah.project.service.request'
MODEL_ATTACHMENT = 'ir.attachment'


class RequestCustomerPortal(CustomerPortal, ServiceRequest):
    _items_per_page = 10

    # def _prepare_portal_layout_values(self):
    #     """Override : inject process if the any internal user will do action from the frontofoiice side"""
    #     values = super()._prepare_portal_layout_values()
    #     if values.get('sales_user', False):
    #         values['title'] = _("Administrator or Deparmtment Employee")
    #     return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'request_count' in counters:
            values['request_count'] = (
                request.env[MODEL_NAME].search_count(
                    self._prepare_service_request_domain())
                if request.env[MODEL_NAME].check_access_rights('read', raise_exception=False)
                else 0
            )
        return values

    def _prepare_service_request_domain(self):
        return []

    def _get_searchbar_sortings(self):
        return {
            'date_desc': {'label': _('Newest'), 'order': 'create_date desc'},
            'date_asc': {'label': _('Oldest'), 'order': 'create_date asc'},
        }

    def _get_searchbar_filters(self, today, quarter_start, quarter_end, last_week, last_month, last_year):
        return {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date_from", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date_from', '>=', date_utils.start_of(today, "week")), ('date_from', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date_from', '>=', date_utils.start_of(today, 'month')), ('date_from', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date_from', '>=', date_utils.start_of(today, 'year')), ('date_from', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date_from', '>=', quarter_start), ('date_from', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date_from', '>=', date_utils.start_of(last_week, "week")), ('date_from', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date_from', '>=', date_utils.start_of(last_month, 'month')), ('date_from', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date_from', '>=', date_utils.start_of(last_year, 'year')), ('date_from', '<=', date_utils.end_of(last_year, 'year'))]},
        }

    def _get_searchbar_groupby(self):
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
            'department': {'input': 'department', 'label': _('Department')},
            'service_catalog': {'input': 'service_catalog', 'label': _('Service Catalog')},
            'state': {'input': 'state', 'label': _('Status')}
        }

        if request.env.user.has_group('project.group_project_manager'):
            searchbar_groupby['client'] = {
                'input': 'client', 'label': _('Client')}
        return searchbar_groupby

    def _get_searchbar_inputs(self):
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'request': {'input': 'request', 'label': _('Search in Requests')},
            'project': {'input': 'project', 'label': _('Search in Projects')},
            'department': {'input': 'department', 'label': _('Search in Departments')},
            'service_catalog': {'input': 'service_catalog', 'label': _('Search in Service Catalog(s)')},
            'state': {'input': 'state', 'label': _('Search in Status')},
        }
        if request.env.user.has_group('project.group_project_manager'):
            searchbar_inputs['client'] = {
                'input': 'client', 'label': _('Search in Client')}
        return searchbar_inputs

    def _get_search_domain(self, search_in, search):
        search = search.rstrip()
        search_domain = []

        if search_in in ('request', 'all'):
            search_domain = OR(
                [search_domain, [('sequence', 'ilike', search)]])

        if search_in in ('project', 'all'):
            search_domain = OR(
                [search_domain, [('project_id.name', 'ilike', search)]])

        if request.env.user.has_group('project.group_project_manager'):
            if search_in in ('client', 'all'):
                search_domain = OR(
                    [search_domain, [('client_id.name', 'ilike', search)]])

        if search_in in ('department', 'all'):
            search_domain = OR(
                [search_domain, [('department_id.name', 'ilike', search)]])

        if search_in in ('service_catalog', 'all'):
            search_domain = OR(
                [search_domain, [('catalog_id.name_en', 'ilike', search)]])

        if search_in in ('state', 'all'):
            search_domain = OR(
                [search_domain, [('state', 'ilike', search)]])

        return search_domain

    def _get_domain_by_criteria(self, criteria):
        if criteria == 'is_active':
            return [('is_done', '=', False)]
        elif criteria == 'is_late':
            return [('is_late', '=', True)]
        elif criteria == 'is_due_date':
            return [('sla_end_date', '=', date.today())]
        else:
            return []
        # return [(criteria, '=', True)]

    def _get_user_domain(self):
        # Only users with project manager group can see all data.
        current_partner = request.env.user.partner_id
        domain = [('client_id', '=', current_partner.id)]
        if request.env.user.has_group('project.group_project_manager'):
            domain = []
        return domain

    @http.route(['/my/requests', '/my/requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_request(self, page=1, sortby='date_desc', filterby='all', search=None, search_in='all', groupby='none', project_id=None, criteria=None, **kw):
        if not self.can_access_route('service_request'):
            return request.redirect('/access/access_denied')
        service_request_data = self._get_service_request_data()
        active_user = request.env.user
        # restrict the redirection from the dashboard user in case of inspection code source.
        if project_id == '0':
            return False
        domain = []
        ServiceRequest = request.env[MODEL_NAME]
        values = self._prepare_portal_layout_values()
        service_request_sudo = ServiceRequest.sudo()
        offset = (page - 1) * self._items_per_page
        searchbar_sortings = self._get_searchbar_sortings()
        searchbar_inputs = self._get_searchbar_inputs()
        searchbar_groupby = self._get_searchbar_groupby()
        order = searchbar_sortings[sortby]['order']
        domain = self._service_request_check_access(domain)
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)
        searchbar_filters = self._get_searchbar_filters(
            today, quarter_start, quarter_end, last_week, last_month, last_year)
        # Ensure the redirection from the dashboard user to the 'my requests'
        if project_id:
            domain = AND([domain, [('project_id', '=', int(project_id))]])
        if active_user.has_group('project.group_project_manager'):
            domain = []
            if search and search_in:
                domain += self._get_search_domain(search_in, search)
        # Add filter by criteria
        domain_criteria = self._get_domain_by_criteria(criteria)
        if criteria:
            domain = AND([domain, domain_criteria])
        if not active_user.partner_id.is_customer:
            domain += [('concerned_user_ids', 'in', active_user.ids)]
        # Approved Service Requests
        requests_hr = service_request_sudo
        requests_other = service_request_sudo
        domain_custom = []

        if search and search_in:
            domain_custom += self._get_search_domain(search_in, search)
        if active_user.has_group('thiqah_project.thiqah_hr_group'):
            domain_for_hr = [('is_approved', '=', True)]
            domain_for_hr = AND([domain_custom, domain_for_hr])
            requests_hr = service_request_sudo.search(domain_for_hr)
        else:
            domain_other = ['|', '&', ('traceability_actors_ids', 'in', active_user.id), ('is_approved', '=', True), '&', (
                'traceability_actors_ids', 'in', active_user.id), ('request_status', '=', 'rejected')]
            domain_for_other = AND([domain_custom, domain_other])
            requests_other = service_request_sudo.search(domain_for_other)
        domain = AND([domain, searchbar_filters[filterby]['domain']])
        requests_by_owner = service_request_sudo.search(
            [('create_uid', '=', active_user.id)])
        requests = service_request_sudo.search(domain)
        # transition._get_next_transition(transition.state_to)
        requests_ids = list(
            set(requests.ids + requests_hr.ids + requests_other.ids + requests_by_owner.ids))
        requests = service_request_sudo.search([('id', 'in', requests_ids)])
        all_requests = service_request_sudo.search(
            [('id', 'in', requests.ids + requests_hr.ids)])
        requests = service_request_sudo.search(
            [('id', 'in', requests.ids + requests_hr.ids)], order=order, limit=self._items_per_page, offset=offset)
        request.session['my_requests_history'] = requests.ids[:100]

        if groupby == 'project':
            grouped_requests = [service_request_sudo.concat(
                *g)for k, g in groupbyelem(requests, itemgetter('project_id'))]
        elif groupby == 'client':
            grouped_requests = [service_request_sudo.concat(
                *g)for k, g in groupbyelem(requests, itemgetter('partner_id'))]
        elif groupby == 'department':
            grouped_requests = [service_request_sudo.concat(
                *g)for k, g in groupbyelem(requests, itemgetter('department_id'))]
        elif groupby == 'service_catalog':
            grouped_requests = [service_request_sudo.concat(
                *g)for k, g in groupbyelem(requests, itemgetter('catalog_id'))]
        elif groupby == 'state':
            grouped_requests = [service_request_sudo.concat(
                *g)for k, g in groupbyelem(requests, itemgetter('state'))]
        else:
            grouped_requests = [requests]

        all_requests = all_requests.filtered(lambda r: r.client_id.id == active_user.partner_id.id
                                              and not r.create_uid.has_group('project.group_project_manager'))
        final_requests = service_request_sudo.search(
                    [('id', 'in', all_requests.ids)], order=order, limit=self._items_per_page, offset=offset)
        request_count = service_request_sudo.search_count([('id', 'in', all_requests.ids)])
        # pager
        pager = portal_pager(
            url="/my/requests",
            url_args={'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterby': filterby, 'groupby': groupby},
            total=request_count,
            page=page,
            step=self._items_per_page
        )

        values.update(service_request_data)
        values.update({
            'requests': final_requests,
            'final_requests': final_requests,
            'grouped_requests': grouped_requests,
            'page_name': 'service_requests',
            'default_url': '/my/requests',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("thiqah_portal.portal_my_requests", values)

    def _request_get_page_view_values(self, service_request, access_token, **kwargs):
        values = {
            'page_name': 'service_requests',
            'service_request': service_request,
        }
        return self._get_page_view_values(service_request, access_token, values, 'my_requests_history', False, **kwargs)

    def handle_states(self, model, values):
        """."""

        # get the cuurent states(Selection content) from the workflow engine
        model_object = request.env[model._name].sudo()
        result = model_object.check_active_id(model.id)
        workflow_id = request.env['workflow.workflow'].sudo().browse([
            int(result['workflow_id'])
        ])

        _pass = bool(result['result'])
        if _pass:
            # preparation of the states of each workflow.
            states = []
            technical_names = []
            for workflow in workflow_id:
                for action in workflow.action_ids:
                    states.append(action.state_id.name)
                    technical_names.append(action.state_id.technical_name)
                    if action.state_to.flow_end:
                        states.append(action.state_to.name)
                        technical_names.append(action.state_to.technical_name)

            states.append('Rejected')
            technical_names.append('rejected')
            model_ = model_object.browse([model.id])
            if model_.state == 'rejected':
                model_.write({'request_status': 'rejected'})

            if model_.state == technical_names[0]:
                model_.write({'request_status': 'submitted'})

            if model_.state == technical_names[-2]:
                model_.write({'is_done': True})

                if model_.state == 'rejected':
                    model_.write({'request_status': 'rejected'})
                else:
                    model_.write({'is_done': True,
                        'request_status': 'approved'})

            elif model_.state != technical_names[-2] and model_.state != technical_names[0]:
                model_.write({
                    # 'is_active': True,
                    'is_in_progress': True,
                    'is_done': False,
                    'request_status': 'pending',
                })

            else:
                model_.update({
                    'is_in_progress': False,
                    'is_done': False
                })

            if model_.state == 'reject':
                model_.write({'request_status': 'rejected'})

            active_state, active_state_technical = model.get_display_request_state()
            states = states[:-2]
            values.update({
                'active_state': active_state,
                'active_state_technical': active_state_technical,
                'states': states,
                'latest_status': technical_names[-1] if states else False,
                'has_states': True if states else False
            })

        return values

    def handle_actions(self, model, values):
        """."""
        # get the cuurent states(Selection content) from the workflow engine
        workflow_id = request.env[model._name].with_context(params={'model': model._name, 'id':model.id})._get_worflow_id()
        result = request.env[model._name].check_active_id(model.id)
        workflow_id = request.env['workflow.workflow'].sudo().browse([
            int(result['workflow_id'])
        ])

        _pass = bool(result['result'])
        if _pass:
            actions = []
            for workflow in workflow_id:
                for transition in workflow.transition_ids:
                    allowed_users = request.env['res.users']
                    # get the concerned users
                    if transition.transition_validation_ids:
                        for validation in transition.transition_validation_ids:
                            if validation.type == 'by_user': 
                                allowed_users += validation.get_dedicated_users(model)
                            else:
                                for group in validation.group_ids:
                                    allowed_users += group.users
                        actions.append((transition.action_id.name.upper(),
                            transition.action_id.button_key, transition.action_id.state_id.technical_name, allowed_users.ids, transition.action_id.state_to.is_approved,transition.action_id.state_to.name))
                    else:
                        actions.append((transition.action_id.name.upper(),
                            transition.action_id.button_key, transition.action_id.state_id.technical_name, request.env['res.users'].sudo().search([]).ids, transition.action_id.state_to.is_approved,transition.action_id.state_to.name))
            values.update({'actions': actions})
        return values

    def check_access(self, request_id, access_token, model=False):
        try:
            if model:
                model_name = model
            else:
                model_name = MODEL_NAME
            service_request_sudo = self._document_check_access(model_name, request_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return service_request_sudo

    @http.route([
        '/my/requests/<int:request_id>',
        '/my/requests/<int:request_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def service_requests_followup(self, request_id=None, access_token=None, **kw):
        """."""
        service_request_sudo = self.check_access(request_id, access_token)
        #Change Notification State to opened
        if isinstance(service_request_sudo, Response):
            return request.redirect('/access/access_denied')
        try:
            notif_id = int(kw.get('notif_id', '0'))
            if notif_id != 0:
                request.env['notification.system'].sudo().browse(notif_id).write({'is_open': True})
        except Exception:
            pass
        values = self._request_get_page_view_values(
            service_request_sudo, access_token, **kw)

        # get attachments with naive solution
        ir_attachment = request.env[MODEL_ATTACHMENT].sudo()
        # prepare data to send them to the frontend
        domain_attachment = [
            ('res_model', '=', service_request_sudo._name),
            ('res_id', '=', service_request_sudo.id),
        ]
        resource_attachments = ir_attachment.search(domain_attachment)
        values['document_ids'] = resource_attachments
        values['has_documents'] = True if len(
            resource_attachments) > 0 else False

        # get justifications
        justification_contents = [
            service_request_sudo.justification_text if service_request_sudo.justification_text else '']

        values['justifications'] = justification_contents
        values['has_justifications'] = True if justification_contents[0] else False
        # if not bool(justification_contents[0]) else False

        values['service_request'] = service_request_sudo

        # handle the case where the mode is 'edit'
        ordered_dict_params = request.params
        params = dict(ordered_dict_params)
        # handling the wizard checkout
        values = self.handle_states(service_request_sudo, values)
        # handling the service request acitons
        values = self.handle_actions(service_request_sudo, values)

        if params.get('mode', False):
            values['mode'] = params.get('mode', False)

            if params.get('mode', False) == 'edit':
                if service_request_sudo.request_status == 'submitted':
                    return 'This request has been received, it must not be editable by anyone.'
                # Request should not be edited by PM
                if request.env.user.id == service_request_sudo.project_manager_id.id:
                    values['mode_restrict'] = 'pm_restrict'
                    values['mode'] = 'view'
                else:
                    values.update(self._get_service_request_data())

            # restrict the access to the change status functionnality
            if params.get('mode', False) == 'change_status':
                if request.env.user.has_group('base.group_portal'):
                    vp_group_id = request.env.ref('thiqah_project.vp_group')
                    if not vp_group_id.id in request.env.user.get_external_group_ids() or not service_request_sudo.vp_id.id == request.env.user.id:
                        if request.env.user.partner_id.id == service_request_sudo.partner_id.id or service_request_sudo.user_id.id == request.env.user.id:
                            # TODO: Mode view to set.
                            values['mode'] = 'view'
                            return request.render("thiqah_portal.service_request_followup", values)
                        return "ACCESS DENIED: maybe you aren't mentioned as VP in the project linked to this request.Or,verify the is_vp in the partner checked or not!"

        return request.render("thiqah_portal.service_request_followup", values)

    @http.route([
        '/my/request/update', '/my/request/update/<int:request_id>'], type='json', auth='public')
    def update_request(self, request_id, partner_id, project_id,  description, department_id=None, catalog_id=None, access_token=None):
        """."""
        service_request_sudo = self.check_access(request_id, access_token)

        values = {
            'partner_id': int(partner_id) if partner_id else service_request_sudo.partner_id,
            'project_id': int(project_id) if project_id else service_request_sudo.project_id,
            # 'department_id': int(department_id),
            # 'catalog_id': int(catalog_id),
            'description': description if description else service_request_sudo.description,
        }

        service_request_sudo.write(values)
        return True

    @http.route([
        '/my/request/delete/<int:request_id>',
    ], type='json', auth="public", website=True)
    def delete_request(self, request_id, access_token=None, **kw):
        """."""
        service_request_sudo = self.check_access(request_id, access_token)

        if request.env.user.has_group('base.group_system'):
            result = service_request_sudo.unlink()
            return result

        # Restrict deleting a request when there are replies
        # string frozen , don't touch
        body = '<p>Attached files : </p>'
        if service_request_sudo:
            if not isinstance(service_request_sudo, Response):

                for message_id in service_request_sudo.message_ids:
                    if message_id.message_type == 'comment':
                        if message_id.body == body:
                            continue

                        return 'unauthorized'

                result = service_request_sudo.unlink()

                return result
            else:
                return 'refresh'

    @http.route('/my/request/page/<int:request_id>', type="http", auth='public', website=True)
    def portal_my_request_detail(self, request_id, access_token=None, report_type=None, download=None, **kw):
        """."""
        service_request_sudo = self.check_access(request_id, access_token)

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=service_request_sudo, report_type=report_type, report_ref='thiqah_project.service_requests', download=download)

        return http.request.render('thiqah_portal.portal_service_request_page', {
            'service_request': service_request_sudo,
        })

    # TODO:Combine all dashboards process(s) in one method.

    @http.route(['/my/dashboard'], type='http', auth="user", website=True)
    def my_dashboard(self, **kw):
        """."""
        domain = []
        if request.env.user.has_group('thiqah_project.group_portal_department') or request.env.user.has_group('base.group_portal'):
            return '404 Not Found'

        if request.env.user.has_group('thiqah_project.project_manager_group'):
            domain = []
            # get current user's all projects.
            project_ids = request.env['project.project'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ])
            domain = AND([
                domain, [('id', 'in', project_ids.ids)]
            ])

        project_sudo = request.env['project.project'].sudo().search(domain)
        values = self._prepare_portal_layout_values()

        all_projects_count = project_sudo.search_count(domain)
        values['all_projects_count'] = all_projects_count
        state_names = project_sudo._get_states()
        state_values = project_sudo._get_states_values()

        data = []
        for index in range(len(state_values)):
            count = project_sudo.search_count(
                AND([domain, [('state', '=', state_values[index])]])
            )
            data.append((state_values[index], state_names[index], count))

        # preparing dashboard data. ==> [('Base Line', 1), ('In progress', 1), ('Closing', 0)]
        values['states'] = data

        return request.render("thiqah_portal._portal_dashboard", values)

    @http.route(['/my/portal/dashboard'], type='http', auth="user", website=True)
    def my_helpdesk_home(self, **kw):
        """."""
        values = {}
        partner_id = request.env.user.partner_id

        all_projects = request.env['project.project'].sudo().search([
            ('partner_id', '=', partner_id.id)
        ])

        values.update({
            'all_projects': all_projects,
        })

        return request.render("thiqah_portal.dashboard_portal_user", values)

    def check_justification(self, service_request_sudo):
        # check if there is justification or not
        if service_request_sudo:
            if not isinstance(service_request_sudo, Response):
                message_types = []
                for message_id in service_request_sudo.message_ids:
                    message_types.append(message_id.message_type)

                if 'comment' not in message_types:
                    return False

    @http.route('/service/change/status', type="json", website=True)
    def change_status(self, access_token=None, **kwargs):
        request_id = request.env[MODEL_NAME].sudo().browse([
            int(kwargs['request_id'])
        ])
        service_request_sudo = self.check_access(
            request_id.id, access_token)

        user_portal_id = request.env['res.users'].sudo().browse([
            request.env.user.id
        ])

        service_request_sudo.write({
            'justification_text': kwargs['justification'] if 'justification' in kwargs else ''
        })

        try:
            request.env['workflow.engine'].sudo(
            ).abstract_button_execution(service_request_sudo, kwargs['button_key'], user_portal_id)

            return json.dumps({'error': 'false', 'message': ''})

        except Exception as exception:
            if isinstance(exception, AccessError):
                return json.dumps({'error': 'true', 'message': str(exception)})

    @http.route('/service/reject/status', type="json", website=True)
    def reject_request(self, access_token=None, **kwargs):
        """."""
        request_id = request.env[MODEL_NAME].sudo().browse([
            int(kwargs['request_id'])
        ])
        service_request_sudo = self.check_access(
            request_id.id, access_token)

        service_request_sudo.write({
            'justification_text': kwargs['justification'] if 'justification' in kwargs else '',
            'last_step_created_by': request.env.user.id
        })

        try:
            service_request_sudo.reject_request()
            # Notification
            notif_id = request.env['notification.system'].sudo().create({
                    'message_id': get_random_string(23),
                    'name': _('Service Request REJECTED'),
                    'description': _('This request was rejected: ' + str(service_request_sudo.sequence) + ' By ' + str(service_request_sudo.last_step_created_by.name)),
                    'user_id': service_request_sudo.create_uid.id,
                    'url_redirect': service_request_sudo.get_change_status_url(),
                    'model_id': service_request_sudo.id,
                    'model_name': 'thiqah.project.service.request',
                    'type': 'reject'
                })
            notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
            return True
        except Exception as exception:
            return 'AccessError'

    @http.route('/render/aahd/lead/', type="http", website=True)
    def render_page_generate_lead(slef):
        """."""
        values = {
            'page_title_lead_ar': request.env.company.page_title_lead_ar,
            'page_body_lead_ar': request.env.company.page_body_lead_ar,
            'page_title_lead_en': request.env.company.page_title_lead_en,
            'page_body_lead_en': request.env.company.page_body_lead_en
        }
        return request.render("thiqah_portal.aahd_generate_lead", values)

    @http.route('/generate/lead', method=['POST'], type="http", website=True)
    def generate_lead(self, **kw):
        """."""
        lead_ideas = request.env['crm.lead'].sudo()
        required_fields = {
            'name': kw['name'] if 'name' in kw else 'anonymous',
            'type': 'lead',
            'description': kw['description'] if 'description' in kw else None,
            'email_from': kw['email'] if 'email' in kw else None,
            'phone': kw['email'] if 'email' in kw else None,
            'for_bd': False,
            'for_aahd': False,
        }

        lead_ideas.create(required_fields)

        return request.redirect('/submission-succeed-lead')

    @http.route('/submission-succeed', type="http", website=True)
    def submission_succeed_view(self, **kw):

        values = {'st': 'done'}
        return request.render("thiqah_portal.submission_succeed", values)

    # For the service request

    @http.route('/upload_attachment', type='json', auth="public",
                method=['POST'], website=True)
    def upload_attachment(self, **kw):
        base64 = kw['attachments']
        request_id = kw['requestId']
        try:
            attach = base64.split(',')[1]
        except Exception:
            attach = base64
        request.env['ir.attachment'].sudo().create({
            'name': kw['attachment_name'],
            'type': 'binary',
            'datas': attach,
            'res_id': int(request_id),
            'res_model': 'thiqah.project.service.request'
        })

class MyController(http.Controller):
    
    @http.route(['/lead/<string:entity>/form'], auth='public', website=True, csrf=False)
    def candidate_form_render(self, entity, **kw):
        if entity == 'thiqah':
            return request.render("thiqah_portal.thiqah_candidate_form")
        elif entity == 'ahad':
            return request.render("thiqah_portal.ahad_candidate_form")
        else:
            #page not found
            return request.render("website.page_404")
    
    @http.route(['/lead/<string:entity>/submit'], auth='public', website=True, csrf=True)
    def candidate_form_submit(self, entity, **kw):
        if not kw.get('first_name', False) or not kw.get('last_name', False):
            return request.redirect('/lead/' + entity + '/form')
        vals = {
            'name': kw.get('first_name', ' ') + ' ' + kw.get('last_name', ' ') + ' Lead',
            'first_name': kw.get('first_name'),
            'last_name': kw.get('last_name'),
            'organization': kw.get('company'),
            'phone': kw.get('phone'),
            'email_from': kw.get('email'),
            'description': kw.get('note'),
            'type': 'lead',
        }
        if entity == 'thiqah':
            event_id = request.env['ir.config_parameter'].sudo().get_param('thiqah_crm.thiqah_envent_id')
        elif entity == 'ahad':
            event_id = request.env['ir.config_parameter'].sudo().get_param('thiqah_crm.ahad_envent_id')
        else:
            return request.render("website.page_404")
        source_id = request.env['lead.source'].sudo().search([('event_as_source', '=', True)], limit=1)
        vals.update({
            'source_lead_id': source_id.id if source_id else False,
            'event_id': int(event_id) if event_id else False
            })
        lead_id = request.env['crm.lead'].sudo().with_user(SUPERUSER_ID).create(vals)
        if entity == 'thiqah':
            return request.render("thiqah_portal.thiqah_submission_succeed")
        else:
            return request.render("thiqah_portal.ahad_submission_succeed")
