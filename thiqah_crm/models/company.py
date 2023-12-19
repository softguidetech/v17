# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    @api.depends('work_area_value_max', 'budget_and_margin_value_max', 'duration_value_max',
                 'partner_value_max', 'project_risk_value_max', 'carrying_capacity_value_max', 'strategic_recommendations_value_max',)
    def compute_final_result_max(self):
        for rec in self:
            rec.final_result_max = rec.work_area_value_max + rec.budget_and_margin_value_max + rec.duration_value_max + \
                rec.partner_value_max + rec.project_risk_value_max + \
                rec.carrying_capacity_value_max + rec.strategic_recommendations_value_max

    work_area_value_max = fields.Integer("Max Scoop Of Work")
    budget_and_margin_value_max = fields.Integer("Max Budget And margin")
    duration_value_max = fields.Integer("Max Duration")
    partner_value_max = fields.Integer("Max Client")
    project_risk_value_max = fields.Integer("Max Project Risk")
    carrying_capacity_value_max = fields.Integer("Max Carrying Capacity")
    strategic_recommendations_value_max = fields.Integer(
        "Max strategic Recommendations")
    final_result_max = fields.Integer(
        "Max Final Result", compute="compute_final_result_max")
    growth_goal = fields.Float("Goal Growth(ON Million)")
    growth_goal_wathiq = fields.Float("Goal Growth(For Wathiq)")
    margin_min = fields.Float("Margin Min")
    margin_max = fields.Float("Margin Max")

    page_title_lead_ar = fields.Char()
    page_body_lead_ar = fields.Text()

    page_title_lead_en = fields.Char()
    page_body_lead_en = fields.Text()
    
    passing_score_lead_evaluation = fields.Integer(string="Passing Score",max=20 , default="20")
