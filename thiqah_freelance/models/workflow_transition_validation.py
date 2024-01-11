from odoo import models

class WorkflowTransitionValidation(models.Model):
    _inherit = 'workflow.transition.validation'

    def get_dedicated_users(self, record_id):
        if self.is_line_management:
            user_id = record_id.create_uid
            if user_id.employee_ids and user_id.employee_ids.parent_id and user_id.employee_ids.parent_id.user_id:
                return user_id.employee_ids.parent_id.user_id
            else:
                 return self.env['res.users'].sudo()
        elif self.creator:
                return record_id.create_uid
        else:
            return super().get_dedicated_users(record_id)