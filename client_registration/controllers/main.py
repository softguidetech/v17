# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
import json
import logging
import re

from odoo import http, _
from odoo.http import request
from odoo.exceptions import  AccessError, MissingError, UserError
from odoo.addons.portal.controllers.portal import pager as portal_pager
from ...thiqah_base.controllers import thiqah_portal


_logger = logging.getLogger(__name__)

class ThiqahClientRegistration(thiqah_portal.ThiqahPortal):
    _items_per_page = 10

    @http.route(['/my/client_payment','/my/client_payment/page/<int:page>'], type='http', auth="user", website=True)
    def client_payment_list(self, page=1, **kw):
        client_payment_obj = request.env['client.payment']
        client_registration_id = request.env['client.registration'].search(['|', ('create_uid','=', request.uid), ('concerned_user_ids', 'in', request.uid)])
        user_registration_id = request.env['client.registration'].search([('create_uid','=', request.uid)])
        countries = request.env['res.country'].sudo().search([])
        values = {}
        client_payment_count = client_payment_obj.search_count([])
        pager = portal_pager(
            url="/my/client_payment",
            total=client_payment_count,
            page=page,
            step=self._items_per_page
        )
        client_payment_list_ids = client_payment_obj.search(['|', ('create_uid','=', request.uid), 
                    ('concerned_user_ids', 'in', request.uid)], limit=self._items_per_page, 
                    offset=pager['offset'], order='create_date DESC')
        values.update({
            "client_payment_req": client_payment_list_ids,
            "countries": countries,
            "client_registration_id": client_registration_id,
            "user_registration_id": user_registration_id,
            "pager": pager
        })
        return request.render("client_registration.client_payment_list", values)

    @http.route(['/client_payment/create'],type="json", website=True)
    def create_client_payment(self, **kw):
        client_registration_id = request.env['client.registration'].search([('create_uid','=', request.uid)], limit=1)
        res = {'status': 'failed', 'message': 'Something went wrong!'}
        try:
            client_payment_id = request.env['client.payment'].create({
                        'legal_representative': kw.get('legal_representative', False),
                        'total_amount': kw.get('total_amount', False),
                        'client_registration_id': client_registration_id.id,
                        'client_product_id': client_registration_id.client_product_id.id if client_registration_id.client_product_id else False,
                        'mazad_number': kw.get('mazad_number'),
                        })
            for file in kw.get('client_payment_attachments', []):
                file_base64 = re.sub(r'^.*,', '', file['fileData'])
                if file_base64:
                    request.env['ir.attachment'].sudo().create({
                        'name': file['fileName'],
                        'datas': file_base64,
                        'res_model': 'client.payment',
                        'res_id': client_payment_id.id,
                    })
            res = {'status': 'success', 'message': 'Client Payment was added!'}
        except Exception as e:
            _logger.exception("Error when creating client payment in Odoo: %s" % e)
            res = {'status': 'failed', 'message': 'Something went wrong!',}
        return json.dumps(res)
    
    def handle_actions_states_cpayment(self, record):
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

    @http.route(['/my/client_payment/<model("client.payment"):client_payment_id>',], type='http', auth="user", website=True)
    def client_payment_details(self, client_payment_id=None,  **kw):
        """."""
        if not self.can_access_route('client_payment'):
            return request.redirect('/access/access_denied')

        try:
            notif_id = int(kw.get('notif_id', '0'))
            if notif_id != 0:
                request.env['notification.system'].sudo().browse(notif_id).write({'is_open': True})
        except Exception:
            pass

        client_payment_obj = request.env['client.payment'].browse([int(client_payment_id)])
        values= {"client_payment_obj":client_payment_obj}
        domain_attachment = [
            ('res_model', '=', 'client.payment'),
            ('res_id', '=', client_payment_id.id),
        ]
        ir_attachment = request.env['ir.attachment'].sudo()
        resource_attachments = ir_attachment.search(domain_attachment)
        values['document_ids'] = resource_attachments
        values['has_documents'] = True if len(
            resource_attachments) > 0 else False
        values.update(self.handle_actions_states_cpayment(client_payment_id))
        return request.render("client_registration.client_payment_details",values)

    @http.route('/client_payment/change/status', type="json", website=True)
    def cpayment_change_status(self, access_token=None, **kw):
        model_name = kw.get('model_name')
        request_id = request.env[model_name].sudo().browse([int(kw['request_id'])])
        request_id = self.check_access(request_id.id, access_token, model_name)
        try:
            action = request.env['workflow.action'].sudo().search([('button_key', '=', kw.get('button_key'))])
            action.with_user(request.env.user.id).transition_id.trigger_transition(active_record_id=request_id, active_model_name=model_name)
            return json.dumps({'status': 'success', 'message': 'Status was changed!'})
        except Exception as exception:
            if isinstance(exception, AccessError):
                return json.dumps({'status': 'failed', 'message': 'You don\'t have access to approve this request', 'error': str(exception)})
            else:
                return json.dumps({'status': 'failed', 'message': 'Something went wrong!', 'error': str(exception) })

    @http.route('/client_reg/attachment/remove', type='json', auth='public')
    def attachment_remove(self, attachment_id):
        
        try:
            attachment_sudo = request.env['ir.attachment'].sudo().browse(int(attachment_id))
            if request.env.uid != attachment_sudo.create_uid.id:
                raise UserError(_("You don't have permission to delete this file!"))
        except (AccessError, MissingError) as e:
            raise UserError(_("The attachment does not exist or you do not have the rights to access it."))

        return attachment_sudo.unlink()
    

    ##############################   Client Registration   ##############################
    
    @http.route(['/my/client_registration','/my/client_registration/page/<int:page>'], type='http', auth="user", website=True)
    def client_registration_list(self, page=1, **kw):
        client_registration_ids = request.env['client.registration'].search([('concerned_user_ids', 'in', request.uid), ('create_uid', '!=', request.uid)])
        user_registration_id = request.env['client.registration'].search([('create_uid','=', request.uid)])
        countries = request.env['res.country'].sudo().search([])
        values = {}
        pager = portal_pager(
            url="/my/client_registration",
            total=len(client_registration_ids),
            page=page,
            step=self._items_per_page
        )
        values.update({
            "countries": countries,
            "client_registration_ids": client_registration_ids,
            "user_registration_id": user_registration_id,
            "pager": pager
        })
        return request.render("client_registration.client_registration_list", values)
        
    @http.route(['/my/client_registration/<model("client.registration"):client_reg_id>',], type='http', auth="user", website=True)
    def client_registration_details(self, client_reg_id=None,  **kw):
        """."""
        if not self.can_access_route('client_registration'):
            return request.redirect('/access/access_denied')

        try:
            notif_id = int(kw.get('notif_id', '0'))
            if notif_id != 0:
                request.env['notification.system'].sudo().browse(notif_id).write({'is_open': True})
        except Exception:
            pass
        values = {'client_reg_id': client_reg_id}
        domain_attachment = [
            ('res_model', '=', 'client.registration'),
            ('res_id', '=', client_reg_id.id),
        ]
        ir_attachment = request.env['ir.attachment'].sudo()
        resource_attachments = ir_attachment.search(domain_attachment)
        values['document_ids'] = resource_attachments
        values['has_documents'] = True if len(
            resource_attachments) > 0 else False
        return request.render("client_registration.client_registration_details",values)

    def get_supplier_data_payload(self, client_name):
        data = {
                "Supplier": client_name,
                "AlternateName":"New Supplier",
                "sites":[
                    {
                        "SupplierSite": client_name[0:15],
                        "ProcurementBU":"Thiqah Business Services Co.",
                        "AlternateSiteName":"New Site"
                    }
                ],
                "addresses":[
                    {
                        "AddressName":"Main Office",
                        "Country":"Saudi Arabia",
                        "CountryCode":"SA"
                    }
                ]
                }
        return data
        
    @http.route(['/client_registration/create'],type="json", website=True)
    def create_client_registration(self, **kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        # client_registration_id = request.env['client.registration'].search([('create_uid','=', request.uid)], limit=1)
        client_product_id = request.env['client.product'].search([('code','=',kw.get('client_payment_category', False))], limit=1)
        res = {'status': 'failed', 'message': 'Something went wrong!'}
        try:
            client_name = kw.get('client_name', '')
            if client_product_id and client_product_id.code in ['saso', 'emazad_company']:
                url = oracle_config_id.url + oracle_config_id.create_supplier_endpoint
                data = self.get_supplier_data_payload(client_name)
            #TODO: please edit else condition to be "elif client_product_id.code == 'emazad_individual' 
            # else: return exception(No client_product)
            else:
                url = oracle_config_id.url + oracle_config_id.freelance_endpoint
                data = {
                    "BusinessUnit": "Thiqah Business Services Co.",
                    "FreelancerName":client_name[0:15],
                    "ExtraInfo":  client_name
                }
            response = requests.post(url, auth=auth, json=data)
            if response.status_code in range(200,300):
                try:
                    client_registration_id = request.env['client.registration'].create({
                        'client_name': client_name,
                        'site_name': client_name[0:15],
                        'client_product_id': client_product_id.id if client_product_id else False,
                        'legal_representative': kw.get('legal_representative',False),
                        'id_number': kw.get('id_number',False),
                        'phone_number': kw.get('phone_number',False),
                        'email': kw.get('email',False),
                        'supplier_oracle_id': str(json.loads(response.text).get('SupplierId')),
                        })
                    for file in kw.get('client_register_attachments', []):
                        file_base64 = re.sub(r'^.*,', '', file['fileData'])
                        if file_base64:
                            request.env['ir.attachment'].sudo().create({
                                'name': file['fileName'],
                                'datas': file_base64,
                                'res_model': 'client.registration',
                                'res_id': client_registration_id.id,
                            })
                    res = {'status': 'success', 'message': 'Client registration was added!', 'client_registration_id': client_registration_id.id}
                    return res
                except Exception as e:
                    _logger.exception("Error when creating client payment in Odoo: %s" % e)
                    res = {'status': 'failed', 'message': 'Something went wrong!', 'client_registration_id': False}
            else:
                error_msg = json.loads(response.text).get('detail')
                _logger.error("Error Creating Supplier/Freelance on Oracle ERP --->: %s" % error_msg)
                res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or 'Something went wrong!', 'client_registration_id': False}
        except Exception as e:
            _logger.exception("Error when creating client payment: %s" % e)
            res = {'status': 'failed', 'message': 'Something went wrong!',}
        return json.dumps(res)
    
    @http.route(['/client_registration/update'],type="json", website=True)
    def update_client_registration(self, **kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        client_registration_id = request.env['client.registration'].search([('create_uid','=', request.uid)], limit=1)
        client_product_id = request.env['client.product'].search([('code','=',kw.get('client_payment_category', False))], limit=1)
        res = {'status': 'failed', 'message': 'Something went wrong!'}
        try:
            if client_registration_id.client_product_id.code in ['saso', 'emazad_company']:
                client_name = kw.get('client_name', '')
                if client_name and client_registration_id.client_name != client_name:
                    url = oracle_config_id.url + oracle_config_id.update_supplier_endpoint + str(client_registration_id.supplier_oracle_id)
                    data = {
                        "SupplireName": client_name,
                    }
                    response = requests.patch(url, auth=auth, json=data)
                    if response.status_code in range(200,300):
                        try:
                            client_registration_id.write({
                                    'client_name': client_name,
                                    'legal_representative': kw.get('legal_representative',False),
                                    'id_number': kw.get('id_number',False),
                                    'phone_number': kw.get('phone_number',False),
                                    'email': kw.get('email',False),
                                })
                            for file in kw.get('client_register_attachments', []):
                                file_base64 = re.sub(r'^.*,', '', file['fileData'])
                                if file_base64:
                                    request.env['ir.attachment'].sudo().create({
                                        'name': file['fileName'],
                                        'datas': file_base64,
                                        'res_model': 'client.registration',
                                        'res_id': client_registration_id.id,
                                    })
                            res = {'status': 'success', 'message': 'Client registration was updated!'}
                        except Exception as e:
                            _logger.exception("Error when creating client payment in Odoo: %s" % e)
                            res = {'status': 'failed', 'message': 'Something went wrong!', 'client_registration_id': False}
                    else:
                        error_msg = json.loads(response.text).get('detail')
                        _logger.error("Error Creating Supplier/Freelance on Oracle ERP --->: %s" % error_msg)
                        res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or 'Something went wrong!'}
                else:
                    client_registration_id.write({
                                'legal_representative': kw.get('legal_representative',False),
                                'id_number': kw.get('id_number',False),
                                'phone_number': kw.get('phone_number',False),
                                'email': kw.get('email',False),
                            })
            else:
                res = {'status': 'failed', 'message': 'Unknown client product!'}
        except Exception as e:
            _logger.exception("Error when creating client payment: %s" % e)
            res = {'status': 'failed', 'message': 'Something went wrong!',}
        return json.dumps(res)
    
    def add_bank_details(self, kw, client_reg_id):
        try:
            bank_details = {
                'bank_country': kw.get('bank_country',False),
                'bank_name': kw.get('bank_name',False),
                'branch_name': kw.get('branch_name',False),
                'bank_id': kw.get('bank',False),
                'branch_id': kw.get('branch',False),
                'account': kw.get('account',False),
                'account_holder_name':kw.get('account_holder_name',False),
                'iban': kw.get('iban',False),
                'is_bank_added': True,
            }
            if client_reg_id.client_product_id.code in ['emazad_individual', 'emazad_company']:
                bank_details.update({
                    'state': 'business_operation',
                    'concerned_user_ids': request.env.ref('client_registration.group_business_operation_approval_creg').users.ids,
                })
            elif client_reg_id.client_product_id.code == 'saso':
                bank_details.update({
                    'state': 'product_manager',
                    'concerned_user_ids': request.env.ref('client_registration.group_product_manager_creg').users.ids,
                })
            return client_reg_id.write(bank_details)
        except Exception as e:
            _logger.exception("Error when creating client payment in Odoo: %s" % e)
            return False

    @http.route(['/client_registration/create_bank'],type="json", website=True)
    def route_cp_create_bank(self, **kw):
        oracle_config_id = request.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        res = {'status': 'failed', 'message': 'Something went wrong!'}
        try:
            client_reg_id = request.env['client.registration'].search([('create_uid','=', request.uid)], limit=1)
            bank_country_id = request.env['res.country'].browse(int(kw.get('bank_country')))
            if client_reg_id.client_product_id.code == 'emazad_individual':
                url = oracle_config_id.url + oracle_config_id.create_banks_endpoint
                data = {
                    "FreelancerName": client_reg_id.client_name,
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
                    self.add_bank_details(kw, client_reg_id)
                    res = {'status': 'success', 'message': 'Bank Details added!'}
                else:
                    error_msg = json.loads(response.text).get('detail')
                    res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or 'Something went wrong!'}
                    _logger.exception("ORACLE API: Error when adding bank details: %s" % response.text)
            elif client_reg_id.client_product_id.code in ['emazad_company', 'saso']:
                url = oracle_config_id.url + oracle_config_id.create_supplier_bank_endpoint
                data = {
                            "SupplireName":client_reg_id.client_name,
                            "SiteName": client_reg_id.site_name,
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
                    self.add_bank_details(kw, client_reg_id)
                    res = {'status': 'success', 'message': 'Bank Details added!'}
                else:
                    error_msg = json.loads(response.text).get('detail')
                    res = {'status': 'failed', 'message':  len(error_msg) < 200 and error_msg or 'Something went wrong!'}
                    _logger.exception("ORACLE API: Error when adding bank details: %s" % response.text)
            else:
                res = {'status': 'failed', 'message': 'Unknown client product!'}
        except Exception as e:
            _logger.exception("Error when adding bank details: %s" % e)
            res = {'status': 'failed', 'message': 'Something went wrong!'}
        return json.dumps(res)

    @http.route(['/client_registration/change/status'],type="json", website=True)
    def client_registration_change_state(self, **kw):
        try:
            record_id = request.env['client.registration'].browse(int(kw.get('creg_id')))
            direction = kw.get('direction')
            res = {'status': 'success', 'message': _('Status was changed!')}
            if record_id.state == 'draft' and direction == 'next' and record_id.create_uid.id == request.env.uid:
                if record_id.client_product_id.code in ['emazad_individual', 'emazad_company']:
                    record_id.write({
                        'state': 'business_operation',
                        'concerned_user_ids': request.env.ref('client_registration.group_business_operation_approval_creg').users.ids,
                        })
                elif record_id.client_product_id.code == 'saso':
                    record_id.write({
                        'state': 'product_manager',
                        'concerned_user_ids': request.env.ref('client_registration.group_product_manager_creg').users.ids,
                        })
            elif record_id.state in ['product_manager', 'business_operation'] and direction == 'next' and request.env.uid in record_id.concerned_user_ids.ids:
                record_id.write({
                    'state': 'approved',
                    'concerned_user_ids': [(6, 0, [])],
                    })
            elif record_id.state in ['product_manager', 'business_operation'] and direction == 'previous' and request.env.uid in record_id.concerned_user_ids.ids:
                record_id.write({
                    'state': 'draft',
                    'concerned_user_ids': record_id.create_uid.ids,
                    })
            else:
                res = {'status': 'failed', 'message': _('You don\'t have access to approve this request')}
        except Exception as e:
            _logger.error("Error when changing client registration state: %s" % e)
            res = {'status': 'failed', 'message': _('Something went wrong!')}
        return json.dumps(res)