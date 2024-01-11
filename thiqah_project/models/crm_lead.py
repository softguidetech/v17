# -*- coding : utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from ...thiqah_base.models.tools import get_random_string
            
class CRMInherit(models.Model):
    _inherit = 'crm.lead'

    is_won = fields.Boolean(related='stage_id.is_won')
    is_converted = fields.Boolean(default=False)
    expected_revenue = fields.Float('Expected Revenue')
    
    def _handle_error(self):
        raise ValidationError(
            "Please verify your configuration.There is no assignment.")

    # Outil for Notificatin System
    def _get_url_project(self, project_id):
        return self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + '/my/projects/' + project_id + '?mode=view'

    def mapping_lead_project(self):
        project_project = self.env['project.project'].sudo()
        opportunity_owned = project_project.search([
            ('name', 'ilike', self.name)
        ])
        if not opportunity_owned.lead_id:
            opportunity_owned.write(
                {
                    'lead_id': self.id
                }
            )
    
    def convert_to_project(self):
        self.ensure_one()
        if self.legal_state == 'waiting_approval_legal':
            raise ValidationError(
                "Until now , there is no action from the legal team.")
        if not self.legal_state == 'no_need_contract':
            if self.message_attachment_count == 0:
                raise ValidationError("There is no contract attached.")

        # prepare project data.
        project_project = self.env['project.project'].sudo()

        # additional test besides the test in xml
        if self.is_converted:
            raise ValidationError(
                "This opportunity has already been converted to a project.")

        # Depending on the type of the service (Digital or Non digital)
        assign_to_id = None
        if self.product_for_filter_id.is_digital_aahd:
            # Welcome Digital Solution
            # get the concerend user from the settings
            assign_to_id = self.env.user.company_id.digital_solution__id
            if not assign_to_id:
                self._handle_error()

        elif self.product_for_filter_id.is_non_digital_aahd:
            # Welcome Advisor Team
            # get the concerend user from the settings
            assign_to_id = self.env.user.company_id.assignment_advisor_id
            if not assign_to_id:
                self._handle_error()
        else:
            raise ValidationError(
                "Please specify the product linked (digital or no digital).")

        result = project_project.create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'state': 'pending',
            'assing_to_id': assign_to_id.id,
            'lead_id': self.id
        })

        if result:
            self.is_converted = True
            self.env['notification.system'].sudo().create({
                'message_id': get_random_string(23),
                'name': _('Project assignment'),
                'description': _('You have been assigned to this project: ' + result.name),
                'user_id': assign_to_id.id,
                'url_redirect': result.get_portal_url_preview(),
                'model_id': result.id,
                'model_name': 'project.project'
            })
            if assign_to_id.email:
                template = self.env.ref(
                    'thiqah_mail_templates.assignment_project_conversion', raise_if_not_found=False)
                if template:
                    template.sudo().send_mail(result.id, force_send=True)
            else:
                raise ValidationError(
                    "The designated person doesn't have an email.")

                # return {
                #     'type': "ir.actions.act_window",
                #     'name': "Projects",
                #     'res_model': "project.project",
                #     'xml_id': "project.edit_project",
                #     'target': "main",
                #     'res_id': result.id,
                #     'view_mode': "form",
                #     'domain': [('is_internal_project', '=', False)]
                # }
