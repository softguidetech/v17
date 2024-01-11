# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TransitionValidation(models.Model):
    _name = 'workflow.transition.validation'
    _description = 'Workflow Transition Validation'

    name = fields.Char(required=True)

    type = fields.Selection([
        ('by_user', 'By User(s)'),
        ('by_group', 'By Group(s)')
    ], default='by_user', required=True)

    user_for_hr = fields.Selection([
        ('none', 'None'),
        ('ahad_advisory', 'Ahad Advisory'),
        ('director_finance', 'Director Finance'),
    ], default='none')

    user_ids = fields.Many2many('res.users', string='Users')
    partner_ids = fields.Many2many('res.partner', string='Partners')
    group_ids = fields.Many2many('res.groups', string='Groups', domain = lambda self: [('category_id.id', '=', self.env.ref('thiqah_base.thiqah_workflow_category').id)])

    is_project_manager = fields.Boolean(default=False)
    is_project_accoutant = fields.Boolean(default=False)
    is_line_management = fields.Boolean(default=False, string='Is Line Manager')
    is_hrbp = fields.Boolean(default=False, string='Is HR Business Partner')
    creator = fields.Boolean(default=False, string='Creator')
    is_stakeholder = fields.Boolean(default=False, string='Stakeholder')

    def _get_projects_managers(self, check_employees=False):
        project_manager_ids = []
        manager_parent_ids = []
        project_user_ids = self.env['project.project'].sudo().search([]).mapped('user_id')
        for user in project_user_ids:
            project_manager_ids.append(user.id)
            if check_employees:
                if not user.employee_ids:
                    raise ValidationError("The project manager " + user.name + " is not linked to an employee!")
                elif not user.employee_ids.parent_id:
                    raise ValidationError("The employee " + user.name + " have not a line manager!")
                elif not user.employee_ids.parent_id.user_id.id:
                    raise ValidationError("The employee " + user.employee_ids.parent_id.name + " should have a related user!")
                manager_parent_ids.append(user.employee_ids.parent_id.user_id.id)
        return list(set(project_manager_ids)), manager_parent_ids
    
    def _get_business_partner_users(self):
        project_hrbp_ids = self.env['project.project'].sudo().search([]).mapped('hr_business_partner_id')
        return list(set(project_hrbp_ids.ids))

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'by_user':
            self.group_ids = False
        elif self.type == 'by_group':
            self.user_ids = False

    @api.onchange("is_project_manager")
    def _onchange_is_project_manager(self):
        if self.is_project_manager:
            project_manager_ids, _ = self._get_projects_managers()
            self.update({
                    'user_ids': [(6, 0, self.env['res.users'].search(
                        [('id', 'in', project_manager_ids)]).ids)],
                    'is_project_accoutant': False,
                    'is_line_management': False,
                    'is_hrbp': False,
                    'creator': False,
                    'is_stakeholder': False,
                })

    @api.onchange("is_hrbp")
    def _onchange_is_hrbp(self):
        if self.is_hrbp:
            project_hrbp_ids = self._get_business_partner_users()
            self.update({
                    'user_ids': [(6, 0, self.env['res.users'].search(
                        [('id', 'in', project_hrbp_ids)]).ids)],
                    'is_project_manager': False,
                    'is_project_accoutant': False,
                    'is_line_management': False,
                    'creator': False,
                    'is_stakeholder': False,
                })
    
    @api.onchange("creator")
    def _onchange_creator(self):
        if self.creator:
            project_hrbp_ids = self._get_business_partner_users()
            self.update({
                    'user_ids': [(6, 0, [])],
                    'is_project_manager': False,
                    'is_project_accoutant': False,
                    'is_line_management': False,
                    'is_hrbp': False,
                    'is_stakeholder': False,
                })

    @api.onchange("is_project_accoutant")
    def _onchange_is_project_accoutant(self):
        if self.is_project_accoutant:
            project_accountant_ids = list(set(self.env['project.project'].sudo().search([]).mapped('project_accountant_id.id')))
            self.update({
                    'user_ids': [(6, 0, project_accountant_ids)],
                    'is_project_manager': False,
                    'is_line_management': False,
                    'is_hrbp': False,
                    'creator': False,
                    'is_stakeholder': False,
                })

    @api.onchange("is_line_management")
    def _onchange_is_line_management(self):
        if self.is_line_management:
            # _, manager_parent_ids = self._get_projects_managers(self.is_line_management)
            self.update({
                    'user_ids': [(6, 0, [])],
                    'is_project_manager': False,
                    'is_project_accoutant': False,
                    'is_hrbp': False,
                    'creator': False,
                    'is_stakeholder': False,
                })

    @api.onchange("is_stakeholder")
    def _onchange_is_stakeholder(self):
        if self.is_stakeholder:
            self.update({
                    'user_ids': [(6, 0, [])],
                    'is_project_manager': False,
                    'is_project_accoutant': False,
                    'is_hrbp': False,
                    'creator': False,
                    'is_line_management': False,
                })

    transition_id = fields.Many2one('workflow.transition', string='Matching Transition')

    def get_groups(self):
        for validation in self:
            # get XML externel identifier from the 'ir.model.data'.
            if validation.group_ids:
                domain = [('model', '=', 'res.groups'),
                          ('res_id', 'in', validation.group_ids.ids)]

                groups_model_data = self.env['ir.model.data'].search(domain)

                groups_xml_ids = ["%s.%s" % (
                    model_data.module, model_data.name) for model_data in groups_model_data]

                return groups_xml_ids

    def get_dedicated_users(self, record_id):
        if record_id._name == 'thiqah.project.service.request':
            project_id = record_id.project_id
            if self.is_hrbp:
                user_id = project_id.hr_business_partner_id
                return user_id if user_id else self.env['res.users'].sudo()
            elif self.is_project_manager:
                user_id = project_id.user_id
                return user_id if user_id else self.env['res.users'].sudo()
            elif self.is_project_accoutant:
                user_id = project_id.project_accountant_id
                return user_id if user_id else self.env['res.users'].sudo()
        return self.user_ids
