# -*- coding: utf-8 -*-
import resource
from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils
from odoo.exceptions import AccessDenied, AccessError, MissingError
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import AND, OR
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.project.controllers.portal import ProjectCustomerPortal
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter
from collections import OrderedDict
from .main import ProjectCustom
from odoo.exceptions import ValidationError
from ...thiqah_base.controllers.thiqah_portal import ThiqahPortal


MODEL_NAME = 'project.project'


class ThiqahProjectPortal(ProjectCustomerPortal, ProjectCustom):
    _items_per_page = 10

    # def _prepare_home_portal_values(self, counters)

    def _project_get_searchbar_sortings(self):
        return {
            'date_desc': {'label': _('Newest'), 'order': 'create_date desc'},
            'date_asc': {'label': _('Oldest'), 'order': 'create_date asc'},

        }

    def _project_get_searchbar_filters(self, today, quarter_start, quarter_end, last_week, last_month, last_year):
        return {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date_start", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date_start', '>=', date_utils.start_of(today, "week")), ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date_start', '>=', date_utils.start_of(today, 'month')), ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date_start', '>=', date_utils.start_of(today, 'year')), ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date_start', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date_start', '>=', date_utils.start_of(last_week, "week")), ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date_start', '>=', date_utils.start_of(last_month, 'month')), ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date_start', '>=', date_utils.start_of(last_year, 'year')), ('date', '<=', date_utils.end_of(last_year, 'year'))]},
        }

    def _project_get_searchbar_groupby(self):
        return {
            'none': {'input': 'none', 'label': _('None')},
            'client': {'input': 'client', 'label': _('Client')},
            'state': {'input': 'state', 'label': _('Status')}
        }

    def _project_get_searchbar_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Search in All')},
            'state': {'input': 'state', 'label': _('Search in Status')},
        }

    def _project_get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('project', 'all'):
            search_domain = OR(
                [search_domain, [('name', 'ilike', search)]])

        if search_in in ('state', 'all'):
            search_domain = OR(
                [search_domain, [('state', 'ilike', search)]])

        return search_domain

    def _get_user_project_domain(self, criteria):
        # Only users with project manager group can see all data.
        current_partner = request.env.user.partner_id
        domain = [(criteria, '=', current_partner.id)]
        if request.env.user.has_group('project.group_project_manager'):
            domain = []
        return domain

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
        """."""
        if not self.can_access_route('project_management'):
            return request.redirect('/access/access_denied')
        values = self._prepare_portal_layout_values()
        ProjectProject = request.env[MODEL_NAME]
        domain = ProjectProject.project_get_portal_domain()

        if request.env.user.has_group('thiqah_project.project_manager_group'):
            domain = []
            # get current user's all projects.
            project_ids = request.env['project.project'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ])
            domain = AND([
                domain, [('id', 'in', project_ids.ids)]
            ])

        # After getting the domain , grant sudo privileges to the ProjectProject
        project_project_sudo = ProjectProject.sudo()

        project_searchbar_sortings = self._project_get_searchbar_sortings()
        project_searchbar_inputs = self._project_get_searchbar_inputs()
        project_searchbar_groupby = self._project_get_searchbar_groupby()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        project_searchbar_filters = self._project_get_searchbar_filters(
            today, quarter_start, quarter_end, last_week, last_month, last_year)

        # default sort by value
        if not sortby:
            sortby = 'date_desc'
        order = project_searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'

        domain = AND([domain, project_searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain += self._project_get_search_domain(search_in, search)

        # if request.env.user.has_group('base.group_portal'):
        #     current_partner = request.env.user.partner_id
        #     domain = [('partner_id', '=', current_partner.id)]
        #     domain = AND([domain, domain])

        if request.env.user.has_group('base.group_portal'):
            # check the groups dedicated to the external users (Portal or Public)
            quality_assurance_group_id = request.env.ref(
                'thiqah_project.quality_assurance_group')

            vp_group_id = request.env.ref(
                'thiqah_project.vp_group')

            if quality_assurance_group_id.id in request.env.user.get_external_group_ids() or vp_group_id.id in request.env.user.get_external_group_ids():

                if not request.env.user.partner_id.is_customer:
                    domain = AND([domain, domain])
                # if vp_group_id.id in request.env.user.get_external_group_ids():
                #     domain = AND([domain,
                #                   [
                #                       ('vp', '=',
                #                        request.env.user.id)
                #                   ]
                #                   ])
                else:
                    # return "You're considered as a customer. Contact the administrator of the contacts management in the backend."
                    # Then , therefore any user is considered a customer.
                    domain = self._get_user_project_domain('partner_id')

        # ThiqahPortal.external_users_permission()

        # projects count
        project_count = project_project_sudo.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/projects",
            url_args={'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterby': filterby, 'groupby': groupby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        projects = project_project_sudo.search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_projects_history'] = projects.ids[:100]

        if groupby == 'client':
            grouped_projects = [project_project_sudo.concat(
                *g)for k, g in groupbyelem(projects, itemgetter('partner_id'))]
        else:
            grouped_projects = [projects]

        values.update({
            'projects': projects,
            'grouped_projects': grouped_projects,
            'page_name': 'project',
            'default_url': '/my/projects',
            'pager': pager,
            'searchbar_sortings': project_searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': project_searchbar_inputs,
            'searchbar_groupby': project_searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(project_searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("project.portal_my_projects", values)

    def check_access(self, project_id, access_token, model=False):
        try:
            if model:
                model_name = model
            else:
                model_name = MODEL_NAME
            project_sudo = self._document_check_access(model_name, project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return project_sudo

    def _project_get_page_view_values(self, project_project, access_token, **kwargs):
        values = {
            'page_name': 'project',
            'project_project': project_project,
        }
        return self._get_page_view_values(project_project, access_token, values, 'my_projects_history', False, **kwargs)

    def _handle_states(self, model, values):
        """."""
        states = model._get_states()
        values.update({
            'active_state': model.get_display_project_state(),
            'states': states,
            'latest_status': states[-1] if states else False,
            'has_states': True if states else False
        })

        return values

    def _handle_actions(self, model, values):
        """."""
        # format == 'actions = [('Action Name','Action Identifier','Visiblity condition as status')]'
        # preparing the acitons data as static
        actions = [
            ('pending', 'Pending', 'Closing'),
            ('base_line', 'Base Line', 'Pending'),
            ('in_progress', 'In Progress', 'Base Line'),
            ('closing', 'Closing', 'In Progress')
        ]
        values.update({
            'actions': actions,
        })
        return values

    @http.route([
        '/my/projects/<int:project_id>',
        '/my/projects/<int:project_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def projects_followup(self, project_id=None, access_token=None, **kw):
        """."""
        project_sudo = request.env[MODEL_NAME].sudo().browse([int(project_id)])

        values = self._project_get_page_view_values(
            project_sudo, access_token, **kw)

        values['project_project'] = project_sudo

        # Handle the case where the mode is 'edit'
        ordered_dict_params = request.params
        params = dict(ordered_dict_params)

        if params.get('mode', False):
            values['mode'] = params.get('mode', False)
            if params.get('mode', False) == 'edit':
                values.update(self._get_project_project_data())
                # handling the risks count.
                risks = [str(risk_id.id) for risk_id in project_sudo.risk_ids]
                values['risks'] = ','.join(risks)

                return request.render("thiqah_project.risks_issues_update", values)

        # Handling the wizard checkout
        values = self._handle_states(project_sudo, values)

        # Handling actions
        values = self._handle_actions(project_sudo, values)

        # handling documents
        document_ids = request.env['documents.document'].sudo().search([
            ('res_id', '=', project_sudo.id)
        ])

        document_ids = [document for document in document_ids.attachment_id]

        values['document_ids'] = document_ids

        return request.render("thiqah_project.project_followup", values)

    @http.route('/my/project/update/<int:project_id>', auth='user', website=True)
    def render_update_form(self, project_id, **kw):
        """."""
        values = self._get_project_project_data()
        project_project = request.env[MODEL_NAME].sudo().browse(
            [int(project_id)])

        # User can set any id of project , so to avoid calling the XML exception system (processing not necessary).
        if not project_project.exists().id:
            raise ValidationError(
                "This project does not exists.")

        risks = [str(risk_id.id) for risk_id in project_project.risk_ids]
        values['risks'] = ','.join(risks)

        resources = [str(resource_id.id)
                     for resource_id in project_project.resource_ids]
        values['resources'] = ','.join(resources)

        values['project_project'] = project_project
        return http.request.render('thiqah_project.project_followup_update', values)

    @http.route('/project/change/status', type="json", auth="user", website=True)
    def project_change_status(self, project_id, button_key):
        """
        This method allows to change the status of any project from the portal(frontend).
        """

        if not request.env.user.has_group('project.group_project_manager'):
            return 'AccessDenied'

        if not (project_id and button_key):
            return 'NullPointerError'

        # get the concerned project
        project_id = request.env[MODEL_NAME].sudo().browse([
            int(project_id)
        ])

        # do the action
        func = getattr(project_id, "_set_%s" % button_key)

        return func()
