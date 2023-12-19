from datetime import date
from odoo import models, _
from ...thiqah_base.models.tools import get_random_string


class WorkflowTransition(models.Model):
    _inherit = 'workflow.transition'

    def trigger_transition(self, active_record_id=None, active_model_name=None):
        self.ensure_one()
        if active_model_name and active_record_id and active_model_name == 'freelance.request':
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
                record_id.write({'is_approved': True, 'concerned_user_ids': [(5, 0, 0)]})
                user_to_notify = record_id.create_uid
                # Dynamic Formatting Message && Url Redirect
                message_approve = _('This freelance request was approved: %s', record_id.sequence)
                url_redirect = str(record_id.get_change_status_url())
                notif_id = self.env['notification.system'].sudo().create({
                        'message_id': get_random_string(23),
                        'name': _('Freelance Request APPROVED'),
                        'description': message_approve,
                        'user_id': user_to_notify.id,
                        'url_redirect': url_redirect,
                        'model_id': record_id.id,
                        'model_name': 'freelance.request',
                        'type': 'confirm'
                    })
                notif_id.write({'url_redirect': notif_id.url_redirect + '&notif_id='+ str(notif_id.id)})
        else:
            return super().trigger_transition(active_record_id, active_model_name)