from odoo import models

class WorkflowTransitionValidation(models.Model):
    _inherit = 'workflow.transition.validation'

    def get_dedicated_users(self, record_id):
        if record_id._name == 'inquiry.request' and self.is_stakeholder:
            return record_id.department_id.irequest_user_id or self.env['res.users']
        else:
            return super().get_dedicated_users(record_id)