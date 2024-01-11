# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class CategoryPortfolio(models.Model):
    _name = "category.portfolio"
    _rec_name = "complete_name"
    _description = "Category Portfolio"

    name = fields.Char()
    parent_id = fields.Many2one('category.portfolio', 'Parent Category')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True, store=True)

    vb_account_id = fields.Many2one('res.partner', 'VB')
    level = fields.Selection([('level_b', 'Level B'),
                              ('level_c', 'Level C'),
                              ], string="Level")
    sp_manager_id = fields.Many2one('res.partner', string="SP Manager", )
    deputy_id = fields.Many2one('res.partner', string="Deputy", )
    chief_id = fields.Many2one('res.partner', string="Chief of SP", )

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for portfolio in self:
            if portfolio.parent_id:
                portfolio.complete_name = '%s / %s' % (
                    portfolio.parent_id.complete_name, portfolio.name)
            else:
                portfolio.complete_name = portfolio.name

    #  add function get contact of portfolio
    @api.model
    def get_contacts(self, id):
        list_contact_ids = {}
        if id:
            contact_ids = self.env['res.partner'].sudo().search(
                [('category_portfolio_id', '=', int(id))])
            list_contact_ids = [{'name': contact.name,
                                 'id': contact.id} for contact in contact_ids]

        return list_contact_ids

    # add function get portfolio info
    @api.model
    def get_portfolio_info(self, id):
        result = {}
        if id:
            portfolio_id = self.env['category.portfolio'].sudo().search([
                ('id', '=', int(id))])
            if portfolio_id:
                user_id = False
                if portfolio_id.sp_manager_id:
                    user_id = self.env['res.users'].sudo().sudo().search(
                        [('partner_id', '=', portfolio_id.sp_manager_id.id)])
                    if user_id:
                        user_id = user_id.id

                result = {'name': portfolio_id.name, 'sp_manager_name': portfolio_id.sp_manager_id.name,
                          'sp_manager_id': portfolio_id.sp_manager_id.id, 'user_id': user_id,
                          'email': portfolio_id.sp_manager_id.email, 'mobile': portfolio_id.sp_manager_id.mobile,
                          'phone': portfolio_id.sp_manager_id.phone, 'chief_id': portfolio_id.chief_id.name,
                          'email_chief': portfolio_id.chief_id.email,
                          'phone_chief': portfolio_id.chief_id.phone, }

        return result
