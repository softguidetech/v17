from odoo import models


class userServiceAccess(models.Model):
    _inherit = 'user.service.access'

    def update_service_access_right(self, operation, access):
        """Update the service access right for the given operation"""
        for rec in self.filtered(lambda r: r.service in ['client_registration', 'client_payment']):
            if operation == 'read' and not rec.access_read and access:
                rec.env.ref('client_registration.group_client_registration_officer').write({'users': [(4, rec.user_id.id)]})
            elif operation == 'read' and rec.access_read and not access and not rec.user_id.check_service_access('client_payment'):
                rec.env.ref('client_registration.group_client_registration_officer').write({'users': [(3, rec.user_id.id)]})
        return super(userServiceAccess, self).update_service_access_right(operation, access)
