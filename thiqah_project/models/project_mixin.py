# -*- coding : utf-8 -*-

from odoo import models, fields, api


class ProjectMixin(models.AbstractModel):
    _name = 'thiqah.project.mixin'
    _description = 'Mixin For Thiqah Project'

    # Allows this 'Model' to be used in the forms.

    def allows_model_in_forms(self):
        ir_model = self.env['ir.model'].sudo()
        service_request_model = ir_model.search([('model', '=', self._name)])
        if not service_request_model.website_form_access:
            service_request_model.write({'website_form_access': True })
            return True
