from odoo import models


class userServiceAccess(models.Model):
    _inherit = 'user.service.access'

    def update_service_access_right(self, operation, access):
        """Update the service access right for the given operation"""
        for rec in self.filtered(lambda r: r.service in ['freelance_request', 'freelance_workorder']):
            if rec.service == 'freelance_request':
                if operation == 'read' and not rec.access_read and access:
                    rec.env.ref('thiqah_freelance.group_freelance_officer').write({'users': [(4, rec.user_id.id)]})
                elif operation == 'read' and rec.access_read and not access and not rec.user_id.check_service_access('freelance_workorder'):
                    rec.env.ref('thiqah_freelance.group_freelance_officer').write({'users': [(3, rec.user_id.id)]})
            else: # freelance_workorder
                if operation == 'read' and not rec.access_read and access:
                    rec.env.ref('thiqah_freelance.group_freelance_officer').write({'users': [(4, rec.user_id.id)]})
                    rec.env.ref('thiqah_freelance.group_freelance_workorder').write({'users': [(4, rec.user_id.id)]})
                elif operation == 'read' and rec.access_read and not access:
                    rec.env.ref('thiqah_freelance.group_freelance_workorder').write({'users': [(3, rec.user_id.id)]})
                    if not rec.user_id.check_service_access('freelance_request'):
                        rec.env.ref('thiqah_freelance.group_freelance_officer').write({'users': [(3, rec.user_id.id)]})
        return super(userServiceAccess, self).update_service_access_right(operation, access)
