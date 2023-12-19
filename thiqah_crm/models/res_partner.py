# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)



class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        # Override the build method to set id_customer to false if there is a parent_id representing the customer.
        if 'parent_id' in vals_list[0]:
            if vals_list[0]['parent_id']:
                partner_parent = self.env['res.partner'].sudo().browse(
                    [int(vals_list[0]['parent_id'])])
                if partner_parent.is_customer:
                    vals_list[0]['is_customer'] = False

        values = super().create(vals_list)

        for rec in values:
            if rec.is_account_manager:
                seq = self.env['ir.sequence'].next_by_code(
                    'account.manager.code')
            elif rec.is_sp_manager:
                seq = self.env['ir.sequence'].next_by_code('sp.manager.code')
            else:
                seq = self.env['ir.sequence'].next_by_code('customer.code')
            rec.code = seq

        return values

    code = fields.Char(string='Code', readonly=True)
    phone = fields.Char(string='Telephone')
    sector_type = fields.Selection([
        ('government', 'Government'),
        ('private', 'Private'),
    ], string='Sector Type', default='government', tracking=True)
    subordinate_to = fields.Selection([
        ('thiqah', 'Thiqah'),
        ('ahad', 'Ahad'),
    ], string='Subordinate To', default='ahad', tracking=True)
    cr_number = fields.Char(string='CR Number')
    cr_company_name = fields.Char(string='Company Name')
    authorized_person_info = fields.Char(string="Authorized Person info")
    stakeholder_name = fields.Char(string='Stakeholder Name')
    stakeholder_email = fields.Char(string='Stakeholder Email')
    project_name = fields.Char(string='Project Name')
    account_manager_id = fields.Many2one('res.partner', string="Account Manager",
                                         domain="[('is_account_manager','=',True)]")

    client_status_id = fields.Many2one('client.status', string='Client Status')
    category_portfolio_id = fields.Many2one(
        'category.portfolio', string='Portfolio')
    sp_manager_id = fields.Many2one(
        'res.partner', string="SP Manager", related='category_portfolio_id.sp_manager_id')
    deputy_id = fields.Many2one(
        'res.partner', string="Deputy", related='category_portfolio_id.deputy_id')
    chief_id = fields.Many2one(
        'res.partner', string="Chief Of SP", related='category_portfolio_id.chief_id')
    vb_account_id = fields.Many2one(
        related="category_portfolio_id.vb_account_id")
    is_business_developer = fields.Boolean(
        'IS Business developer', default=False)
    is_account_manager = fields.Boolean('IS Account developer', default=False)
    is_sp_manager = fields.Boolean('IS SP Manager', default=False)
    is_deputy = fields.Boolean('IS Deputy', default=False)
    is_chief = fields.Boolean('IS Chief', default=False)
    is_customer = fields.Boolean('IS Customer', default=False)
    shown_in_portal = fields.Boolean('Shown In Portal', default=False)
    team_id = fields.Many2one(
        'crm.team', string='Portfolio', ondelete="set null")
    level = fields.Selection([
        ('key_decision_maker', 'Key Decision Maker'),
        ('business_owner', 'Business Owner'),
        ('project_manager', 'Project Manager'),
    ], string='Level', tracking=True)

    is_vp = fields.Boolean(default=False)
    is_director_finance = fields.Boolean(default=False)
    

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_vp = fields.Boolean(related='partner_id.is_vp')
    user_outlook_user_code = fields.Char(string='Outlook User Code')
    user_outlook_code = fields.Char(string='Outlook Code')
    user_outlook_token = fields.Char(string='Outlook token')
    is_director_finance = fields.Boolean(
        related='partner_id.is_director_finance')


