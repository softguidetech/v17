from datetime import date
import requests
from requests.auth import HTTPBasicAuth
from odoo import fields, models, _
from ...thiqah_base.models.tools import get_random_string


class WorkflowTransition(models.Model):
    _inherit = 'workflow.transition'

    def oracle_create_invoice(self, record_id):
        oracle_config_id = self.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        thiqah_entity_id = self.env['res.entity'].search([('code', '=', 'thiqah')], limit=1)
        if record_id.client_product_id.code in ['saso', 'emazad_company']:
            url = oracle_config_id.url + oracle_config_id.create_supplier_invoice_endpoint
            data = {
                        "BusinessUnit": thiqah_entity_id.full_name,
                        "SupplierName": record_id.client_name,
                        "SupplierSiteName": record_id.site_name,
                        "InvoiceNumber": record_id.sequence,
                        "InvoiceAmount": record_id.total_amount,
                        "InvoiceDate": date.today().__str__(),
                        "InvoiceCurrency":"SAR",
                        "DistributionCombination":"22-10053-1220103-20302-00000-00000-000-000-000",
                        "Description":""
                    }
        elif record_id.client_product_id.code in ['emazad_individual']:
            url = oracle_config_id.url + oracle_config_id.create_invoice_endpoint
            data = {
                    "BusinessUnit": thiqah_entity_id.full_name,
                    "FreelancerName": record_id.client_registration_id.client_name,
                    "InvoiceNumber": record_id.sequence,
                    "InvoiceAmount": record_id.total_amount,
                    "InvoiceDate": date.today().__str__(),
                    "InvoiceCurrency": 'SAR', #record_id.client_registration_id.bank_country.currency_id.name,
                    "Description": ""
                    }
        else:
            self._cr.rollback()
            raise Exception('Client Product is not defined')

        response = requests.post(url, auth=auth, json=data)
        if not response.status_code in range(200,300):
            self._cr.rollback()
            raise Exception(response.text)
        record_id.write({'invoice_created': True})
        return True

    def oracle_validate_invoice(self, record_id):
        oracle_config_id = self.env['oracle.config'].search([], limit=1)
        auth = HTTPBasicAuth(oracle_config_id.user_name, oracle_config_id.password)
        url = oracle_config_id.url + oracle_config_id.validate_invoice_endpoint
        thiqah_entity_id = self.env['res.entity'].search([('code', '=', 'thiqah')], limit=1)
        data = {
                "BusinessUnit": thiqah_entity_id.full_name, 
                "InvoiceNumber": record_id.sequence, 
                }
        response = requests.post(url, auth=auth, json=data)
        if not response.status_code in range(200,300):
            self._cr.rollback()
            raise Exception(response.text)
        record_id.write({'invoice_validated': True})
        return True

    def trigger_transition(self, active_record_id=None, active_model_name=None):
        self.ensure_one()
        if active_model_name and active_record_id and active_model_name == 'client.payment':
            current_user = self.env.user
            record_id = active_record_id
            self._check_validation(record_id)
            next_transition = self._get_next_transition(self.state_to)
            # do_action && internal notification
            if record_id.state == self.state_from.technical_name:
                record_id.state = self.state_to.technical_name
            #If Next Transition
            if next_transition:
                allowed_users_next_transition = next_transition.get_transition_allowed_users(record_id)
                record_id.write({
                        'last_step_created_by': current_user.id,
                        'last_step_created_at': date.today()
                    })
                if allowed_users_next_transition:
                    self.notify_helper(record_id, next_transition, allowed_users_next_transition)
                    record_id.write({'concerned_user_ids':  [(6, 0, allowed_users_next_transition.ids)]})
                else:
                    record_id.concerned_user_ids = [(5, 0, 0)]
            # If this is the last transition
            elif self.state_to.is_approved:
                if not record_id.invoice_created:
                    self.oracle_create_invoice(record_id)
                    # self.oracle_validate_invoice(record_id)
                record_id.write({'is_approved': True, 'concerned_user_ids': [(5, 0, 0)]})
                user_to_notify = record_id.create_uid
                # Dynamic Formatting Message && Url Redirect
                message_approve = _('This client payment request was approved: %s', record_id.sequence)
                url_redirect = str(record_id.get_change_status_url())
                notif_id = self.env['notification.system'].sudo().create({
                        'message_id': get_random_string(23),
                        'name': _('Client Payment APPROVED'),
                        'description': message_approve,
                        'user_id': user_to_notify.id,
                        'url_redirect': url_redirect,
                        'model_id': record_id.id,
                        'model_name': 'client.payment',
                        'type': 'confirm'
                    })
                notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
        else:
            return super().trigger_transition(active_record_id, active_model_name)