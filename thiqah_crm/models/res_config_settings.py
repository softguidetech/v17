# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    activate_notif_salesperson = fields.Boolean(
        'Activate Notification SalesPerson', default=False, config_parameter='activate.notif.salesperson')

    activate_notif_contract = fields.Boolean(
        'Activate the notification to the contract responsible', default=False, config_parameter='activate.notif.contract.responsible')

    activate_overdue_criteria = fields.Boolean(
        'Activate the overdue criteria', default=False, config_parameter='activate.overdue.criteria')

    nbr_days_notif_salesperson = fields.Integer('Number of days to notify SalesPerson',
                                                config_parameter='nbr.days.notif.salesperson')

    nbr_days_to_overdue = fields.Integer('Number of days to setting the overdue status.',
                                         config_parameter='nbr.days.overdue')

    email_template_id_salesperson = fields.Many2one('mail.template', 'Email Template', domain="[('model','=','crm.lead')]",
                                                    config_parameter='email_template.notif.salesperson')
    activate_notif_salesteam_manager = fields.Boolean(
        'Activate Notification Sales Team Manager', default=False, config_parameter='activate.notif.salesteam_manager')

    nbr_days_notif_salesteam_manager = fields.Integer('Number of days to notify Sales Team Manager',
                                                      config_parameter='nbr.days.notif.salesteam_manager')

    nbr_days_notif_contract_responsible = fields.Integer('Number of days to notify the contract responsible',
                                                         config_parameter='nbr.days.notif.contract.responsible')

    email_template_id_salesteam_manager = fields.Many2one(
        'mail.template', 'Email Template', domain="[('model','=','crm.lead')]",
        config_parameter='email_template.notif.salesteam_manager')

    email_template_id_contract_responsible = fields.Many2one(
        'mail.template', 'Email Template',  domain="[('model','=','thiqah.contract')]", config_parameter='email_template.notif.contract_responsible')

    work_area_value_max = fields.Integer( related='company_id.work_area_value_max', readonly=False)
    
    
    
    
    passing_score_lead_evaluation = fields.Integer(string='Passing Score (Max Is : 20 )',default=20,  max=20, config_parameter='thiqah_crm.passing_score_lead_evaluation')
    
    
    budget_and_margin_value_max = fields.Integer( related='company_id.budget_and_margin_value_max', readonly=False)
    duration_value_max = fields.Integer(
        related='company_id.duration_value_max', readonly=False)
    partner_value_max = fields.Integer(
        related='company_id.partner_value_max', readonly=False)
    project_risk_value_max = fields.Integer(
        related='company_id.project_risk_value_max', readonly=False)
    carrying_capacity_value_max = fields.Integer(
        related='company_id.carrying_capacity_value_max', readonly=False)
    strategic_recommendations_value_max = fields.Integer(
        related='company_id.strategic_recommendations_value_max', readonly=False)
    final_result_max = fields.Integer(
        related='company_id.final_result_max', readonly=False)
    growth_goal = fields.Float(
        related='company_id.growth_goal', readonly=False)
    growth_goal_wathiq = fields.Float(
        related='company_id.growth_goal_wathiq', readonly=False)
    margin_min = fields.Float(related='company_id.margin_min', readonly=False)
    margin_max = fields.Float(related='company_id.margin_max', readonly=False)

    page_title_lead_ar = fields.Char(
        related='company_id.page_title_lead_ar', readonly=False)
    page_body_lead_ar = fields.Text(
        related='company_id.page_body_lead_ar', readonly=False)

    page_title_lead_en = fields.Char(
        related='company_id.page_title_lead_en', readonly=False)
    page_body_lead_en = fields.Text(
        related='company_id.page_body_lead_en', readonly=False)
    
    thiqah_envent_id = fields.Many2one(comodel_name='crm.lead.event', string='Thiqah Default Event')
    ahad_envent_id = fields.Many2one(comodel_name='crm.lead.event', string='Ahad Default Event')
    
    @api.constrains('passing_score_lead_evaluation')
    def _check_passing_score_lead_evaluation(self):
        for settings in self:
            if settings.passing_score_lead_evaluation > 20:
                raise ValidationError('The passing score cannot exceed 20.')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['thiqah_envent_id'] = int(self.env['ir.config_parameter'].sudo().get_param('thiqah_crm.thiqah_envent_id'))
        res['ahad_envent_id'] = int(self.env['ir.config_parameter'].sudo().get_param('thiqah_crm.ahad_envent_id'))
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param("thiqah_crm.thiqah_envent_id", self.thiqah_envent_id.id or False)
        self.env['ir.config_parameter'].set_param("thiqah_crm.ahad_envent_id", self.ahad_envent_id.id or False)