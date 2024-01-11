from odoo import models


class userServiceAccess(models.Model):
    _inherit = 'user.service.access'

    def update_service_access_right(self, operation, access):
        """Update the service access right for the given operation"""
        for rec in self.filtered(lambda r: r.service in ['inquiry_request', 'inquiry_dashboard']):
            if operation == 'read' and not rec.access_read and access:
                rec.env.ref('thiqah_inquiry.group_inquiry_user').write({'users': [(4, rec.user_id.id)]})
            elif operation == 'read' and rec.access_read and not access:
                rec.env.ref('thiqah_inquiry.group_inquiry_user').write({'users': [(3, rec.user_id.id)]})
        return super(userServiceAccess, self).update_service_access_right(operation, access)
