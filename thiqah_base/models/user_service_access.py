from odoo import api, fields, models, _

SERVICES = [
            ('home_dashboard', 'Home Dashboard'), ('fin_dashboard', 'Finance Dashboard'),
            ('utilization_report', 'Utilization Report'), ('service_request', 'Service Request'),
            ('project_management', 'Project Management'), ('task_dashboard', 'Task Dashboard'),
            ('customer_centricity', 'Customer Centricity'), ('inquiry_request', 'Inquiry Request'), 
            ('inquiry_dashboard', 'Inquiry Dashboard'), ('freelance_request', 'Freelance Request'),
            ('freelance_workorder', 'Freelance Workorder'), ('client_payment', 'Client Payment'),
            ('client_registration', 'Client Registration'),   
           ]



class userServiceAccess(models.Model):
    _name = 'user.service.access'
    _description = 'User Service Access'

    service = fields.Selection(SERVICES, string='Service', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    access_read = fields.Boolean(string='Read Access', default=False)
    access_create = fields.Boolean(string='Create Access', default=False)

    @api.onchange('access_create', 'access_read')
    def onchange_access_create(self):
        if self.access_create:
            self.access_read = True

    def update_service_access_right(self, operation, access):
        """
        Update the service access right for the given operation
        To be implemented in the inherited models
        """
        return True

    def write(self, values):
        """ADD/REMOVE Access to some groups based on given access to service"""
        for rec in self:
            if 'access_read' in values:
                rec.update_service_access_right('read', values['access_read'])
            # I don't need this for now
            # if 'access_create' in values:
            #     rec.update_service_access_right('create', values['access_create'])
        res = super(userServiceAccess, self).write(values)
        return res
    