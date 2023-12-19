# -*- coding: utf-8 -*-
from datetime import date
import json
import logging
import re
import requests
from requests.auth import HTTPBasicAuth

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, UserError
from odoo.osv.expression import AND
from ...thiqah_base.models.tools import get_random_string

_logger = logging.getLogger(__name__)


class ThiqahFreelanceController(CustomerPortal):
    _items_per_page = 10


     # Freelance Requests
    @http.route(['/my/freelance', '/my/freelance/page/<int:page>'], type='http', auth="user", website=True)
    def freelance_list(self, page=1,date_begin=None, date_end=None, sortby=None,**kw):
        user_id = request.env.user
        if not self.can_access_route('freelance_request'):
            return request.redirect('/access/access_denied')
        values={}
        freelance_req_list = request.env['freelance.request']
        domain = [('entity_code', '=', user_id.entity)]
        searchbar_sortings = {
            'date': {'label': _('Request Date'), 'order': 'request_date desc'},
            'name': {'label': _('Reference'), 'order': 'sequence'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        freelance_req_count = request.env['freelance.request'].search_count(domain)

        pager = portal_pager(
            url="/my/freelance",
            total=freelance_req_count,
            page=page,
            step=self._items_per_page
        )
        freelance_list = freelance_req_list.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'freelance_req':freelance_list,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
            })
        return request.render("thiqah_freelance.portal_freelance_list", values)

    def handle_actions_states_frequests(self, record):
        """."""
        # get the cuurent states(Selection content) from the workflow engine
        workflow_id = request.env[record._name].with_context(params={'model': record._name, 'id':record.id})._get_worflow_id()
        # result = request.env[record._name].check_active_id(record.id)
        # workflow_id = request.env['workflow.workflow'].sudo().browse([int(result['workflow_id'])])
        res = {}
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
        res.update({
            'actions': actions,
            'active_state': active_state,
            'active_state_technical': active_state_technical,
            'states': states,
            'latest_status': technical_names[-1] if states else False,
            # 'has_states': True if states else False
        })
        return res
    
    @http.route('/my/freelance/<model("freelance.request"):freelance_req>', type='http', auth="user", website=True)
    def freelance_details(self, freelance_req, id=False,**kw):
        user_id = request.env.user
        if not self.can_access_route('freelance_request') or user_id.entity != freelance_req.entity_id.code:
            return request.redirect('/access/access_denied')
        values = {}
        incompleted_application = request.env['freelance.application'].search([
            ('create_uid', '=', user_id.id), ('request_id', '=', freelance_req.id),
            ('is_bank_added', '=', False)], limit=1)
        completed_application_ids = request.env['freelance.application'].search([('request_id', '=', freelance_req.id),
            ('is_bank_added', '=', True)])
        try:
            notif_id = int(kw.get('notif_id', '0'))
            if notif_id != 0:
                request.env['notification.system'].sudo().browse(notif_id).write({'is_open': True})
        except Exception:
            pass
        countries = request.env['res.country'].sudo().search([])
        values.update(self.handle_actions_states_frequests(freelance_req))
        values.update({
            'freelance_req': freelance_req,
            'countries': countries,
            'incompleted_application': incompleted_application,
            'completed_application_ids': completed_application_ids,
            'freelance_document_ids': request.env['ir.attachment'].sudo().search([('res_id', '=', freelance_req.id), ('res_model', '=', 'freelance.request')]),
            })
        if freelance_req.entity_code == 'thiqah':
            #If Freelance request for Thiqah we ensure that we show only one application 
            completed_application_id = completed_application_ids[0] if len(completed_application_ids) > 1 else completed_application_ids
            attachments = request.env['ir.attachment'].search([('res_id','=',completed_application_id.id), ('res_model', '=', 'freelance.application')])
            values.update({
                'completed_application_ids': completed_application_id,
                'attachments': [att for att in attachments if att.name],
            })
            return request.render("thiqah_freelance.portal_freelance_request_details", values)
        else:
            return request.render("thiqah_freelance.portal_freelancers_form_ahad",values)
    
    # Freelance request form 
    @http.route('/freelance/form', auth="user", website=True)
    def freelance_form(self, **kw):
        if not self.can_access_route('freelance_request', 'read') or not self.can_access_route('freelance_request', 'create'):
            return request.redirect('/access/access_denied')
        values={}
        department_obj = request.env["hr.department"].sudo().search([])
        entities_obj = request.env["res.entity"].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        user_obj = request.env.user
        values['request_date'] = date.today()
        values['department_obj'] = department_obj
        values['entities_obj'] = entities_obj
        values['countries'] = countries
        values['user_obj'] = user_obj
        if user_obj.entity == "thiqah":
            entity = request.env.ref("thiqah_freelance.thiqah_entity")
            values['user_entity'] = entity
            return request.render("thiqah_freelance.portal_freelance_form",values)
        elif user_obj.entity == "ahad":
            entity = request.env.ref("thiqah_freelance.ahad_entity")
            values['user_entity'] = entity
            return request.render("thiqah_freelance.portal_freelance_form_ahad",values)
        else:
            return (_('<h5>Access Denied. Please contact your administrator!</h5>'))

    @http.route('/freelance/form/add', auth='user',type='http', website=True,csrf=False)
    def add_freelance(self, **kw):
        """."""
        freelance_obj = request.env['freelance.request'].sudo()
        freelance_data = {}
        user_obj = request.env.user
       
        if user_obj.entity == 'thiqah':  
            implication_ids=[]
            for i in range(0, int(kw.get('implication_ids'))):
                implication_ids.append((0,0,{"department_id":int(kw.get('unit_%s' % str(i+1))),"operation":kw.get('operation_%s' % str(i+1))}))     
            try:
                freelance_data.update({
                    'request_date':date.today(),
                    'request_duration': int(kw.get('request_duration',False)),
                    'expected_total_cost': int(kw.get('expected_total_cost',False)),
                    'entity_id': kw.get('entity_id',False),
                    'sector': kw.get('sector',False),
                    'department_id': int(kw.get('department_id',False)),
                    'section': kw.get('section',False),
                    'request_type': kw.get('request_type',False),
                    'request_description': kw.get('request_description',False),
                    'project_name': kw.get('project_name',False),
                    'project_start_date': kw.get('project_start_date') if kw.get('project_start_date') else False,
                    'project_end_date':kw.get('project_end_date') if kw.get('project_end_date') else False,
                    'company_strategy_justif': kw.get('company_strategy_justif',False),
                    'sector_goal_justif': kw.get('sector_goal_justif',False),
                    'request_achievement': kw.get('request_achievement',False),
                    'current_manpower_limit': kw.get('current_manpower_limit',False),
                    'current_manpower_weakness': kw.get('current_manpower_weakness',False),
                    'function': kw.get('function',False),
                    'unit_kpi': kw.get('unit_kpi',False),
                    'deliverable': kw.get('deliverable',False),
                    'deliverable_outcome': kw.get('deliverable_outcome',False),
                    'impacted_unit_ids': implication_ids,
                })
                freelance_id = freelance_obj.create(freelance_data)

                return json.dumps({"status":"success","Message":freelance_id.id})
            except Exception as exception:
                _logger.exception(
                    "Error when adding project: %s" % exception)
                return json.dumps({"status":"failed","Message":"Somthing went wrong"})
        elif user_obj.entity == 'ahad':  
            try:
                freelance_data.update({
                    'request_description': kw.get('request_description',False),
                    'entity_id': kw.get('entity_id',False),
                    'ahad_client_name': kw.get('ahad_client_name',False),
                    'ahad_project_number': kw.get('ahad_project_number',False),
                    'ahad_project_name': kw.get('ahad_project_name',False),
                })
                freelance_id = freelance_obj.create(freelance_data)
                return json.dumps({"status":"success","Message":freelance_id.id})
            except Exception as exception:
                _logger.exception(
                    "Error when adding project: %s" % exception)
                return json.dumps({"status":"failed","Message":"Somthing went wrong"})

    @http.route('/freelance/change/status', type="json", website=True)
    def freelance_change_status(self, access_token=None, **kw):
        model_name = kw.get('model_name')
        request_id = request.env[model_name].sudo().browse([int(kw['request_id'])])
        freelance_request = self.check_access(request_id.id, access_token, model_name)
        try:
            vals = {'justification_text': kw.get('justification', '')}
            if kw.get('state') == 'od_approval' and kw.get('od_recommendation'):
                vals.update({'od_recommendation': kw['od_recommendation'],'od_duration': int(kw['od_duration']),'od_cost': int(kw['od_cost'])})
            elif kw.get('state') == 'hr_ops_approval':
                for file in kw.get('attachment', []):
                    file_base64 = re.sub(r'^.*,', '', file['fileData'])
                    if file_base64:
                        request.env['ir.attachment'].sudo().create({
                            'name': file['fileName'],
                            'datas': file_base64,
                            'res_model': 'freelance.request',
                            'res_id': freelance_request.id,
                        })
            freelance_request.write(vals)
            action = request.env['workflow.action'].sudo().search([('button_key', '=', kw.get('button_key'))])
            action.transition_id.trigger_transition(active_record_id=freelance_request, active_model_name='freelance.request')
            return json.dumps({'error': 'false', 'message': ''})
        except Exception as exception:
            if isinstance(exception, AccessError):
                return json.dumps({'error': 'true', 'message': str(exception)})
            else:
                return json.dumps({'error': 'true', 'message': _('Something went wrong!')})

    @http.route('/freelance/reject', type="json", website=True)
    def freelance_reject_request(self, access_token=None, **kw):
        model_name = kw['model_name']
        request_id = request.env[model_name].sudo().browse([int(kw['frequest_id'])])
        freelance_request = self.check_access(request_id.id, access_token, model_name)
        freelance_request.write({
            'justification_text': kw.get('justification'),
            'last_step_created_by': request.env.user.id
            })
        try:
            freelance_request.reject_request()
            # Notification
            notif_id = request.env['notification.system'].sudo().create({
                    'message_id': get_random_string(23),
                    'name': _('Freelance Request REJECTED'),
                    'description': _('This  freelance request was rejected: ' + str(freelance_request.sequence) + ' By ' + str(freelance_request.last_step_created_by.name)),
                    'user_id': freelance_request.create_uid.id,
                    'url_redirect': freelance_request.get_change_status_url(),
                    'model_id': freelance_request.id,
                    'model_name': 'freelance.request',
                    'type': 'reject'
                })
            notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
            return True
        except Exception:
            return 'AccessError'

    @http.route(['/my/freelance_workorder', '/my/freelance_workorder/page/<int:page>'], type='http', auth="user", website=True)
    def freelance_order_list(self, page=1,date_begin=None, date_end=None, sortby=None,filterby=None,**kw):
        if not self.can_access_route('freelance_workorder'):
            return request.redirect('/access/access_denied')
        freelance_workorder = request.env['freelance.workorder']
        user_id = request.env.user
        domain = []
        searchbar_sortings = {
            'date': {'label': _('Due Date'), 'order': 'due_date desc'},
            'name': {'label': _('Reference'), 'order': 'sequence'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('entity_code', '=', user_id.entity)]},
            'draft': {'label': _('Draft'), 'domain': AND([[('entity_code', '=', user_id.entity)], [("state", "=", "draft")]])},
            'confirmed': {'label': _('Confirmed'), 'domain': AND([[('entity_code', '=', user_id.entity)], [("state", "=", "confirmed")]])},
            'paid': {'label': _('Paid'), 'domain': AND([[('entity_code', '=', user_id.entity)], [("state", "=", "paid")]])},
        }
        
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        freelance_workorder_count = request.env['freelance.workorder'].search_count(domain)
        freelance_workorder_all = request.env['freelance.workorder'].search_count(searchbar_filters['all']['domain'])
        freelance_workorder_draft = request.env['freelance.workorder'].search_count(searchbar_filters['draft']['domain'])
        freelance_workorder_confirmed = request.env['freelance.workorder'].search_count(searchbar_filters['confirmed']['domain'])
        freelance_workorder_paid = request.env['freelance.workorder'].search_count(searchbar_filters['paid']['domain'])

        pager = portal_pager(
            url="/my/freelance_workorder",
            total=freelance_workorder_count,
            page=page,
            step=30
        )
        freelance_order = freelance_workorder.search(domain, order=order, limit=30, offset=pager['offset'])
        
        values = {
            'date': date_begin,
            'default_url':'/my/freelance_workorder',
            'date_end': date_end,
            'freelance_order':freelance_order,
            'pager': pager,
            'filterby': filterby,
            'searchbar_sortings': searchbar_sortings,
            'freelance_workorder_all':freelance_workorder_all,
            'freelance_workorder_confirmed':freelance_workorder_confirmed,
            'freelance_workorder_draft':freelance_workorder_draft,
            'sortby': sortby,
            'freelance_workorder_paid':freelance_workorder_paid
            }
        return request.render("thiqah_freelance.portal_freelance_workorder", values)

    @http.route(['/freelance/create_invoice'],type="json",auth="user", website=True)
    def route_create_freelancer_invoice(self,**kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        url = oracle_config_id.url + oracle_config_id.create_invoice_endpoint
        res = {'status': 'failed', 'message': _('Something went wrong!'), 'freelancer_id': False}
        try:
            fworkorder_ids = request.env['freelance.workorder'].browse(kw.get('orderIDs'))
            success_req = []
            failed_req = []
            error_msg = False
            for work in fworkorder_ids:
                if work.frequest_id.entity_id.code == 'thiqah':
                    distribution_combination = "11-10053-6110601-20302-00000-00000-000-000-000"
                else:
                    distribution_combination = "22-10053-6110601-20302-00000-00000-000-000-000"
                data = {
                        "BusinessUnit": work.frequest_id.entity_id.full_name,
                        "FreelancerName": work.freelancer_id.api_freelancer_name, 
                        "InvoiceNumber": work.sequence, 
                        "InvoiceAmount": work.amount,
                        "InvoiceDate": work.due_date.__str__(), #'2023-08-31',
                        "InvoiceCurrency": 'SAR', #work.freelancer_id.bank_country.currency_id.name,
                        "DistributionCombination": distribution_combination,
                        "Description": "",
                        }
                response = requests.post(url, auth=auth, json=data)
                if response.status_code in range(200,300):
                    work.write({"state":"confirmed"})
                    request.env.cr.commit()
                    success_req.append(work)
                    response = response.json()
                else:
                    failed_req.append(work)
                    error_msg = f'Request {work.sequence}: ' +  str(json.loads(response.text).get('detail'))
                    res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or _('Something went wrong!')}
            if success_req and not failed_req:
                res = {'status': 'success', 'message': 'Workorder confirmed',}
            elif failed_req and success_req:
                res = {'status': 'mixed', 'message':  len(error_msg) < 200 and error_msg or _('Something went wrong!'),
                'success_req':[r.sequence for r in success_req],
                'failed_req':[r.sequence for r in failed_req]}

        except Exception as e:
            _logger.exception("Error when confirming workorder: %s" % e)
            res = {'status': 'failed', 'message': _('Something went wrong!')}
        return json.dumps(res)

    @http.route(['/freelance/validate_invoice'],type="json",auth="user", website=True)
    def route_pay_freelancer_invoice(self,**kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        url = oracle_config_id.url + oracle_config_id.validate_invoice_endpoint
        res = {'status': 'failed', 'message': _('Something went wrong!'),}
        try:
            fworkorder_ids = request.env['freelance.workorder'].browse(kw.get('orderIDs'))
            success_req = []
            failed_req = []
            error_msg = False
            for work in fworkorder_ids:
                data = {
                        "BusinessUnit": work.frequest_id.entity_id.full_name, 
                        "InvoiceNumber": work.sequence, 
                        }
                response = requests.post(url, auth=auth, json=data)
                if response.status_code in range(200,300):
                    work.write({"state":"paid"})
                    request.env.cr.commit()
                    success_req.append(work)
                    response = response.json()
                else:
                    failed_req.append(work)
                    error_msg = f'Request {work.sequence}: ' +  str(json.loads(response.text).get('detail'))
                    res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or _('Something went wrong!'),}
            if success_req and not failed_req:
                res = {'status': 'success', 'message': 'Workorder confirmed',}
            elif failed_req and success_req:
                res = {'status': 'mixed', 'message': 'Failed and Successed request!!!',
                'success_req':[r.sequence for r in success_req],
                'failed_req':[r.sequence for r in failed_req]}

        except Exception as e:
            _logger.exception("Error when confirming workorder: %s" % e)
            res = {'status': 'failed', 'message': _('Something went wrong!')}
        return json.dumps(res)

    @http.route('/freelance_workorder/adjust/amount', type="json", auth="user")
    def freelance_adjust_amount(self, **kw):
        model_name = kw.get('model_name')
        try:
            workorder_id = request.env[model_name].sudo().browse([int(kw['workorderID'])])
            vals = {'justification': kw.get('adjust_justif', ''),'amount': kw.get('amount', '')}
            if workorder_id.state == 'draft':
                workorder_id.write(vals)
            return json.dumps({'status': 'success', 'message': 'Amount adjusted successfully'})
        except Exception as exception:
            return json.dumps({'status': 'failed', 'message': _('Something went wrong!')})

    @http.route(['/freelance/get_banks_branches'],type="json", website=True)
    def get_banks_branches(self,**kw):
        banks = []
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        bank_country =kw.get('country_code')
        country_obj =request.env['res.country'].browse(int(bank_country))
        country_code = country_obj.code
        url = oracle_config_id.url + oracle_config_id.list_banks_endpoint
        if country_code:
            url = url+country_code 
            try:
                res = requests.get(url, auth=auth).json()
                return res
            except:
                return "error"
        else:
            json.dumps({"banks":banks})

    def create_freelancer_record(self, kw, frequest_id):
        withholding_tax = kw.get('withholding_tax_val',False)
        try:
            freelancer_data = {
                'first_name':kw.get('first_name',False),
                'last_name':kw.get('last_name',False),
                'id_number': kw.get('id_number',False),
                'mobile_number': kw.get('mobile_number',False),
                'email': kw.get('email',False),
                'id_type': kw.get('id_type',False),
                'nationality_id': int(kw.get('nationality_id',False)),
                'address': kw.get('address',False),

                'salary': kw.get('salary',False),
               'withholding_tax': kw.get('withholding_tax',False),
                'withholding_tax_comment': kw.get('withholding_tax_comment',False),
                'start_date': kw.get('start_date',False),
                'end_date': kw.get('end_date',False),
                'request_id': frequest_id.id
            }
            return request.env['freelance.application'].create(freelancer_data)
        except Exception as e:
            _logger.exception("Error when creating Freelancer in Odoo: %s" % e)
            return False

    @http.route(['/freelance/create_freelancer'],type="json", website=True)
    def route_create_freelancer(self,**kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        url = oracle_config_id.url + oracle_config_id.freelance_endpoint
        res = {'status': 'failed', 'message': _('Something went wrong!'), 'freelancer_id': False}
        try:
            api_freelancer_name = kw.get('first_name','') + ' ' + kw.get('last_name', '')
            if len(api_freelancer_name) > 15:
                api_freelancer_name = api_freelancer_name[0:15]
            frequest_id = request.env['freelance.request'].browse(int(kw.get('frequest')))
            country_id = request.env['res.country'].browse(int(kw.get('nationality_id')))
            extra_info = [country_id.code, kw.get('id_type',''), kw.get('id_number', '')]
            data = {
                "BusinessUnit": frequest_id.entity_id.full_name,
                "FreelancerName":api_freelancer_name,
                "ExtraInfo":  '-'.join(extra_info)
            }
            response = requests.post(url, auth=auth, json=data)
            if response.status_code in range(200,300):
                freelancer_id = self.create_freelancer_record(kw, frequest_id)
                response = response.json()
                freelancer_id.write({
                    'api_supplier_site_id': response.get('SupplierSiteId'),
                    'api_freelancer_name': api_freelancer_name,
                    })
                res = {'status': 'success', 'message': 'Freelancer was added!', 'freelancer_id': freelancer_id.id}
            else:
                error_msg = json.loads(response.text).get('detail')
                res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or _('Something went wrong!'), 'freelancer_id': False}
        except Exception as e:
            _logger.exception("Error when creating Freelancer: %s" % e)
            res = {'status': 'failed', 'message': _('Something went wrong!'), 'freelancer_id': False}
        return json.dumps(res)

    def add_bank_details(self, kw, freelancer_id):
        try:
            bank_details = {
                'bank_country': kw.get('bank_country',False),
                'bank_name': kw.get('bank_name',False),
                'branch_name': kw.get('branch_name',False),
                'bank_id': kw.get('bank',False),
                'branch_id': kw.get('branch',False),
                'account': kw.get('account',False),
                'beneficiary_name':kw.get('beneficiary_name',False),
                'iban': kw.get('iban',False),
            }
            return freelancer_id.write(bank_details)
        except Exception as e:
            _logger.exception("Error when creating Freelancer in Odoo: %s" % e)
            return False

    @http.route(['/freelance/create_bank'],type="json", website=True)
    def route_create_bank(self,**kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        url = oracle_config_id.url + oracle_config_id.create_banks_endpoint
        res = {'status': 'failed', 'message': _('Something went wrong!')}
        try:
            frequest_id = request.env['freelance.request'].browse(int(kw.get('frequest')))
            freelancer_id = request.env['freelance.application'].browse(int(kw.get('freelancer_id')))
            bank_country_id = request.env['res.country'].browse(int(kw.get('bank_country')))
            data = {
                    "FreelancerName": freelancer_id.api_freelancer_name,
                    "CurrencyCode": bank_country_id.currency_id.name,
                    "CountryCode": bank_country_id.code,
                    "BankIdentifier": kw.get('bank'),
                    "BankBranchIdentifier": kw.get('branch'),
                    "BankAccountNumber": kw.get('account'),
                    "BankAccountName": kw.get('beneficiary_name'),
                    "IBAN": kw.get('iban'),
                }
            response = requests.post(url, auth=auth, json=data)
            if response.status_code in range(200,300):
                self.add_bank_details(kw, freelancer_id)
                for file in kw.get('attachments', []):
                    file_base64 = re.sub(r'^.*,', '', file['fileData'])
                    if file_base64:
                        request.env['ir.attachment'].create({
                            'name': file['fileName'],
                            'datas': file_base64,
                            'res_model': 'freelance.application',
                            'res_id': freelancer_id.id,
                        })
                freelancer_id.is_bank_added = True
                res = {'status': 'success', 'message': 'Bank Details added!'}
            else:
                error_msg = json.loads(response.text).get('detail')
                res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or _('Something went wrong!')}
                _logger.exception("ORACLE API: Error when adding bank details: %s" % response.text)
        except Exception as e:
            _logger.exception("Error when adding bank details: %s" % e)
            res = {'status': 'failed', 'message': _('Something went wrong!')}
        return json.dumps(res)


    @http.route(['/freelance/print_contract/<model("freelance.application"):freelancer_id>'],type='http', auth="user", website=True)
    def print_contract(self, freelancer_id,**kw):
        return self._show_report(model=freelancer_id, report_type='pdf', report_ref='thiqah_freelance.agreement_report_pdf', download=True)
