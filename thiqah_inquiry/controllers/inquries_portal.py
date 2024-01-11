# -*- coding: utf-8 -*-

import json
from datetime import datetime

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError
from ...thiqah_base.controllers import thiqah_portal
from ...thiqah_base.models.tools import get_random_string


class ThiqahInquiriesController(thiqah_portal.ThiqahPortal):

    _items_per_page = 10

    def _get_status_statistic(self):
        states_data = []
        inquiry_requests = request.env['inquiry.request'].sudo()
        ir_model = request.env['ir.model'].sudo()
        model_id = ir_model.search([('model', '=', 'inquiry.request')])
        states_keys = []
        for workflow in request.env['workflow.workflow'].search([('model_id', '=', model_id.id)]):
            states = request.env['workflow.engine']._get_state_items(workflow,exclude_approved_rejected=True)
            for state in states:
                domain = [('state', '=', state[0])]
                if state[0] not in states_keys:
                    states_data.append((inquiry_requests.search_count(domain), state[1]))
                    states_keys.append(state[0])
                else:
                    index = states_keys.index(state[0])
                    states_data[index] = (states_data[index][0] + inquiry_requests.search_count(domain), states_data[index][1])
        states_data.sort(key=lambda pair: pair[0],reverse=True)
        return  [[item[1], item[0]] for item in states_data]   
    
    def handle_actions_states_irequests(self, record):
        """."""
        # get the current states(Selection content) from the workflow engine
        workflow_id = request.env[record._name].with_context(params={'model': record._name, 'id':record.id})._get_worflow_id()
        actions = []
        states = []
        technical_names = []
        for workflow in workflow_id:
            for transition in workflow.transition_ids:
                allowed_users = request.env['res.users']
                # get the concerned users
                if transition.transition_validation_ids:
                    for validation in transition.transition_validation_ids:
                        if validation.type == 'by_user':
                            allowed_users += validation.get_dedicated_users(record)
                        else:
                            for group in validation.group_ids:
                                allowed_users += group.users
                        actions.append((transition.action_id.name.upper(),
                            transition.action_id.button_key, transition.action_id.state_id.technical_name, 
                            allowed_users.ids, transition.action_id.state_to.is_approved,transition.action_id.state_to.name))
                else:
                    actions.append((transition.action_id.name.upper(),
                        transition.action_id.button_key, transition.action_id.state_id.technical_name, 
                        request.env['res.users'].sudo().search([]).ids, transition.action_id.state_to.is_approved,transition.action_id.state_to.name))
            for action in workflow.action_ids:
                states.append(action.state_id.name)
                technical_names.append(action.state_id.technical_name)
                if action.state_to.flow_end:
                    states.append(action.state_to.name)
                    technical_names.append(action.state_to.technical_name)
        states.append('Rejected')
        technical_names.append('rejected')
        active_state, active_state_technical = record.get_display_request_state()
        states = states[:-2]
        res = {
            'actions': actions,
            'active_state': active_state,
            'active_state_technical': active_state_technical,
            'states': states,
            'latest_status': technical_names[-1] if states else False,
        }
        return res
    
    @http.route(['/my/inquiries', '/my/inquiries/page/<int:page>'], type='http', auth="user", website=True)
    def inquiries_list(self, page=1, filterby='all', **kw):
        if not self.can_access_route('inquiry_request'):
            return request.redirect('/access/access_denied')
        partner_portfolio = request.env['category.portfolio'].search([])
        partners = request.env['res.partner'].search([('is_customer', '=', True)])
        departments = request.env['hr.department'].search([])
        
        date_now = datetime.now()
        today_from = datetime.combine(date_now, datetime.min.time())
        today_to = datetime.combine(date_now, datetime.max.time())
        if filterby == 'is_active':
            domain = [('close_date', '=', False), ('sla_due_date', '>', date_now)]
        elif filterby == 'is_late':
            domain = [('close_date', '=', False), ('sla_due_date', '<=', date_now)]
        elif filterby == 'is_due_today':
            domain = [('close_date', '=', False), ('sla_due_date', '>=', today_from), ('sla_due_date', '<=', today_to)]
        elif filterby == 'is_on_time':
            request.env.cr.execute('select id from inquiry_request where close_date <= sla_due_date;')
            inquiry_ids = request.env.cr.fetchall()
            inquiry_ids = [r[0] for r in inquiry_ids]
            domain = [('id', 'in', inquiry_ids)]
        else:
            domain = []
        values={}
        inquiries_req_obj = request.env['inquiry.request']
        inquiries_req_count = inquiries_req_obj.search_count(domain)

        pager = portal_pager(
            url="/my/inquiries",
            url_args={},
            total=inquiries_req_count,
            page=page,
            step=self._items_per_page
        )
        inquiries_list = inquiries_req_obj.search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'inquiries':inquiries_list,
            'pager': pager,
            'partner_portfolio':partner_portfolio,
            'partners':partners,
            'departments':departments
            })
        return request.render("thiqah_inquiry.portal_inquiries_list", values)

    @http.route(['/my/inquiries/<model("inquiry.request"):inquiry_id>',
    ], type='http', auth="user", website=True)
    def inquiry_details(self, inquiry_id=None,  **kw):
        """."""
        if not self.can_access_route('inquiry_request', inquiry_id):
            return request.redirect('/access/access_denied')
        try:
            notif_id = int(kw.get('notif_id', '0'))
            if notif_id != 0:
                request.env['notification.system'].sudo().browse(notif_id).write({'is_open': True})
        except Exception:
            pass
        inquiry_obj = request.env['inquiry.request'].browse([int(inquiry_id)])
        values= {"inquiry_obj":inquiry_obj}
        domain_attachment = [
            ('res_model', '=', 'inquiry.request'),
            ('res_id', '=', inquiry_id.id),
        ]
        users = request.env['res.users'].search([('entity', '=', request.env.user.entity)])
        values['users'] = users
        ir_attachment = request.env['ir.attachment'].sudo()
        resource_attachments = ir_attachment.search(domain_attachment)
        values['document_ids'] = resource_attachments
        values['has_documents'] = True if len(
            resource_attachments) > 0 else False
        values.update(self.handle_actions_states_irequests(inquiry_id))
        return request.render("thiqah_inquiry.inquiry_details",values)

    @http.route(['/my/inquiries/dashboard'], type='http', auth="user", website=True)
    def inquiries_dashboard(self, **kw):
        """."""
        inquiry_obj = request.env['inquiry.request']
        if not self.can_access_route('inquiry_dashboard'):
            return request.redirect('/access/access_denied')
        values = {}
        # SLA
        date_now = datetime.now()
        today_from = datetime.combine(date_now, datetime.min.time())
        today_to = datetime.combine(date_now, datetime.max.time())
        values['active_requests_count'] = inquiry_obj.search_count([('close_date', '=', False), ('sla_due_date', '>', date_now)])
        values['late_requests_count'] = inquiry_obj.search_count([('close_date', '=', False), ('sla_due_date', '<=', date_now)])
        values['requests_due_today'] = inquiry_obj.search_count([('close_date', '=', False), ('sla_due_date', '>=', today_from), ('sla_due_date', '<=', today_to)])
        request.env.cr.execute('select count(*) from inquiry_request where close_date <= sla_due_date;')
        values['sla_requests_count'] = request.env.cr.fetchone()[0]
        return request.render("thiqah_inquiry.inquiries_dashboard",values)


    @http.route('/get/inquiries/details', type="http", methods=['GET'], website=True)
    def render_inquiries_details(self):
        """
        :return list(lists)
        """
        # inquiry_ref,inquiry_description,inquiry_department
        response = {}

        inquiries = request.env['inquiry.request'].sudo().search([])

        inquiries_details_data = []
        for inquiry in inquiries:
            inquiries_details_data.append(
                [
                    inquiry.sequence,
                    inquiry.description,
                    inquiry.department_id.name,
                ]
            )

        response.update({
            'inquiries_details_data': inquiries_details_data
        })

        try:
            return json.dumps(response)
        except Exception as exception:
            return str(exception)

    @http.route('/inquiry/change/status', type="json", website=True)
    def inquiry_change_status(self, access_token=None, **kw):
        model_name = kw.get('model_name')
        request_id = request.env[model_name].sudo().browse([int(kw['request_id'])])
        inquiry_request = self.check_access(request_id.id, access_token, model_name)
        try:
            action = request.env['workflow.action'].sudo().search([('button_key', '=', kw.get('button_key'))])
            action.with_user(request.env.user.id).transition_id.trigger_transition(active_record_id=inquiry_request, active_model_name=model_name)
            return json.dumps({'status': 'success', 'message': 'Satus was changed!'})
        except Exception as exception:
            if isinstance(exception, AccessError):
                return json.dumps({'status': 'failed', 'message': 'You don\'t have access to approve this request', 'error': str(exception)})
            else:
                return json.dumps({'status': 'failed', 'message': 'Something went wrong!', 'error': str(exception) })

    def notify_user_assignment(self, user_id, record_id):
        message = _('You are assigned to inquiry request number: %s', record_id.sequence)
        url_redirect = str(record_id.get_change_status_url())
        notif_id = request.env['notification.system'].sudo().create({
                'message_id': get_random_string(23),
                'name': _('Inquiry Request ASSIGNMENT'),
                'description': message,
                'user_id': user_id,
                'url_redirect': url_redirect,
                'model_id': record_id.id,
                'model_name': 'inquiry.request',
                'type': 'confirm'
            })
        notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})

    @http.route('/inquiry/assignUser', type="json", website=True)
    def inquiry_assign_user(self, access_token=None, **kw):
        model_name = 'inquiry.request'
        try:
            request_id = request.env[model_name].sudo().browse([int(kw['request_id'])])
            user_id = int(kw['user_id'])
            note = (kw.get('note'))
            inquiry_request = self.check_access(request_id.id, access_token, model_name)
            self.notify_user_assignment(user_id, inquiry_request)
            inquiry_request.message_post(body=note, message_type='comment', author_id=request.env.user.partner_id.id)
            inquiry_request.write({'user_id': user_id})
            return json.dumps({'status': 'success', 'message': 'User Assigned successfully!'})
        except Exception as exception:
            if isinstance(exception, AccessError):
                return json.dumps({'status': 'failed', 'message': 'You don\'t have access to approve this request', 'error': str(exception)})
            else:
                return json.dumps({'status': 'failed', 'message': 'Something went wrong!', 'error': str(exception) })

    @http.route('/render/inquiries/dashboard/data', type='json', auth='user', website=True)
    def inquiries_chart_dashboard_data(self, **kw):
        """
        .
        """
        values = {}

        by_date_query = """
        select count(*), date_trunc('day',create_date) cr_date from inquiry_request group by cr_date; 
        """
        request.env.cr.execute(by_date_query)
        res = request.env.cr.fetchall()
        values['by_creation_date'] = [{"x":r[1].date(),"y":r[0]} for r in res]

        by_request_type_query = """
        select count(*), request_type from inquiry_request group by request_type;
        """
        request.env.cr.execute(by_request_type_query)
        res = request.env.cr.fetchall()
        values['by_request_type'] = [[r[1],r[0]] for r in res]

        by_partner_query = """
        select count(*), res_partner.name from res_partner join inquiry_request on res_partner.id = inquiry_request.partner_id group by res_partner.name;
        """
        request.env.cr.execute(by_partner_query)
        res = request.env.cr.fetchall()
        values['by_partner'] = [[r[1],r[0]] for r in res]

        by_department_query = """
        select count(*), hr_department.name from hr_department join inquiry_request on hr_department.id = inquiry_request.department_id group by hr_department.name
        """
        request.env.cr.execute(by_department_query)
        res = request.env.cr.fetchall()
        values['by_department'] = [[r[1],r[0]] for r in res]

        # By Status
        values['by_status'] = self._get_status_statistic()

        # SLA
        date_now = datetime.now()
        inquiry_obj = request.env['inquiry.request']
        by_sla = []
        # Late Requests
        by_sla.append(inquiry_obj.search_count([('close_date', '=', False), ('sla_due_date', '<=', date_now)]))
        # SLA Requests
        request.env.cr.execute('select count(*) from inquiry_request where close_date <= sla_due_date;')
        by_sla.append(request.env.cr.fetchone()[0])
        # Active requests
        by_sla.append(inquiry_obj.search_count([('close_date', '=', False), ('sla_due_date', '>', date_now)]))
        values['by_sla'] = by_sla

        return values
