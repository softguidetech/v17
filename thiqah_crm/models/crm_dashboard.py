# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup
from odoo.http import request
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
import math

_logger = logging.getLogger(__name__)


class DashboardLead(models.Model):
    _inherit = "crm.lead"

    # fetch all data
    @api.model
    def get_opp_dashboard_data(self, partner_id=False, product_id=False, account_manager_id=False):
        domain = [('type', '=', 'opportunity')]
        crm_obj = self.env['crm.lead']

        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        all_opportunities = crm_obj.search(
            domain+['|', ('for_aahd', '=', True), ('for_bd', '=', True)])
        all_opportunities_bd = crm_obj.search(domain+[('for_bd', '=', True)])
        all_opportunities_aahd = crm_obj.search(
            domain+[('for_aahd', '=', True)])
        # LOST
        all_opportunities_lost = crm_obj.with_context(active_test=False).search(
            domain+[('probability', '=', 0), '|', ('for_aahd', '=', True), ('for_bd', '=', True)])
        all_opportunities_lost_bd = crm_obj.with_context(active_test=False).search(
            domain+[('probability', '=', 0), ('for_bd', '=', True)])
        all_opportunities_lost_aahd = crm_obj.with_context(active_test=False).search(
            domain+[('probability', '=', 0), ('for_aahd', '=', True)])
        # WON
        all_opportunities_won = crm_obj.search(
            domain+[('stage_id.is_won', '=', True), '|', ('for_aahd', '=', True), ('for_bd', '=', True)])
        all_opportunities_won_bd = crm_obj.search(
            domain+[('stage_id.is_won', '=', True), ('for_bd', '=', True)])
        all_opportunities_won_aahd = crm_obj.search(
            domain+[('stage_id.is_won', '=', True), ('for_aahd', '=', True)])

        list_partners = []
        list_products = []
        list_users = []

        for prod in self.env['product.template'].search([('detailed_type', '=', 'service')]):
            list_products.append([prod.id, prod.name])

        for user in self.env['res.users'].search([]):
            list_users.append([user.id, user.name])

        for partner in self.env['res.partner'].search([]):
            list_partners.append([partner.id, partner.name])

        res = {
            'all_opportunities': len(all_opportunities.ids), 'all_opportunities_bd': len(all_opportunities_bd.ids), 'total_opp_expected_revenue': sum([opp.expected_revenue for opp in all_opportunities.filtered(lambda opp: not opp.stage_id.is_won)]) if all_opportunities else 0,
            'all_opportunities_aahd': len(all_opportunities_aahd.ids), 'total_opp_revenue': sum([opp.won_revenue for opp in all_opportunities]) if all_opportunities else 0,
            # LOST
            'all_opportunities_lost': len(all_opportunities_lost.ids), 'all_opportunities_lost_bd': len(all_opportunities_lost_bd.ids),
            'all_opportunities_lost_aahd': len(all_opportunities_lost_aahd.ids), 'total_lost_revenue': sum([opp.won_revenue for opp in all_opportunities_lost]) if all_opportunities_lost else 0,
            # WON
            'all_opportunities_won': len(all_opportunities_won.ids), 'all_opportunities_won_bd': len(all_opportunities_won_bd.ids),
            'all_opportunities_won_aahd': len(all_opportunities_won_aahd.ids), 'total_won_revenue': sum([opp.won_revenue for opp in all_opportunities_won]) if all_opportunities_won else 0,
            'list_partners': list_partners,
            'list_account_managers': list_users,
            'list_products': list_products,
            'growth_goal': self.env.user.company_id.growth_goal,
            'currency': request.env.company.currency_id.name,

        }
        return res

    # Function get get all inputs data for won Opportunities

    @api.model
    def get_dashboard_data(self, partner_id=False, product_id=False, account_manager_id=False):
        """ Return dashboard cards Data"""
        # domain = [('type', '=', 'opportunity'), ('stage_id.is_won', '=',
        #                                          True), ('is_wathiq', '=', True), ('for_aahd', '=', True)]
        domain = [('type', '=', 'opportunity'),
                  ('is_wathiq', '=', True), ('for_aahd', '=', True)]

        crm_obj = self.env['crm.lead']

        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        opportunities = crm_obj.read_group(
            domain=domain+[('partner_id', '!=', False)],
            fields=['won_revenue'], groupby=['partner_id']
        )
        total_revenue = 0
        get_total_top_ten_clients_revenue = 0
        get_top_ten_clients = []
        list_partners = []
        list_products = []
        list_account_managers = []
        for group in opportunities:
            partner = self.env['res.partner'].browse(group['partner_id'][0])
            list_partners.append([partner.id, partner.name])
            if partner.account_manager_id:
                list_account_managers.append(
                    [partner.account_manager_id.id, partner.account_manager_id.name])
            won_revenue = group['won_revenue'] if group['won_revenue'] else 0
            total_revenue += won_revenue
            if len(get_top_ten_clients) < 10:
                get_total_top_ten_clients_revenue += won_revenue
                get_top_ten_clients.append(
                    [partner.name, won_revenue, partner.id])
        for prod in self.env['product.template'].search([('detailed_type', '=', 'service')]):
            list_products.append([prod.id, prod.name])
        growth = self.env.user.company_id.growth_goal_wathiq if self.env.user.company_id.growth_goal_wathiq else ''
        total_revenue = sum(
            [rec.won_revenue for rec in crm_obj.search(domain)])

        res = {}
        goal_status = None
        if growth:
            # Customization: define the difference in growth compared to 100%.
            # percent_growth = str("{:.2f}".format(
            #     math.exp(total_revenue/growth)))+'%'

            percent_growth_ = (total_revenue / growth) * 100
            # Outils for the up dow icon visibility
            # True ==> sort_up
            # False ==> sort_down
            
            difference = percent_growth_ - 100

            if difference < 0:
                goal_status = 'false'
            elif difference > 0:
                goal_status = 'true'
            elif percent_growth_ == 100.0:
                goal_status = 'no_status'

            percent_growth = str(
                "{:.1f}".format(difference)) + '%' if isinstance(growth, float) else ''
        else:
            percent_growth = ''

        # percent_growth = str(percent_growth-100) + '%'

        res = {
            'total_opports_wathiq': crm_obj.search_count(domain),
            'total_opports_enterprise': crm_obj.search_count([('service_type', '=', 'enterprise')]+domain),
            'total_opports_basic': crm_obj.search_count([('service_type', '=', 'basic')]+domain),
            'total_opports_batch': crm_obj.search_count([('service_type', '=', 'batch')]+domain),
            'total_opprts': crm_obj.search_count(domain),
            'total_revenue': total_revenue,
            'get_top_ten_clients_1': get_top_ten_clients[5:10],
            'get_top_ten_clients_2': get_top_ten_clients[:5],
            'get_total_top_ten_clients_revenue': get_total_top_ten_clients_revenue,
            'list_partners': list_partners,
            'list_account_managers': list_account_managers,
            'list_products': list_products,
            'growth_goal': growth,
            'percent_growth': percent_growth,
            'goal_status': goal_status,
            'currency': request.env.company.currency_id.name,
        }

        return res

    # Function to get Labels and values for won Opportunities according to different Service type batch/enterprise/basic
    @api.model
    def get_wathiq_basic_enterprise_bar_chart(self, partner_id=False, product_id=False, account_manager_id=False):
        crm_obj = self.env['crm.lead']
        # domain = [('type', '=', 'opportunity'), ('is_wathiq',
        #                                          '=', True), ('stage_id.is_won', '=', True)]
        domain = [('type', '=', 'opportunity'), ('is_wathiq', '=', True)]

        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        total_opports_wathiq_batch = crm_obj.search_count(
            domain+[('service_type', '=', 'batch')])
        total_opports_enterprise = crm_obj.search_count(
            domain+[('service_type', '=', 'enterprise')])
        total_opports_basic = crm_obj.search_count(
            domain+[('service_type', '=', 'basic')])
        values = [total_opports_wathiq_batch,
                  total_opports_enterprise, total_opports_basic]

        labels = [_('Batch'), _('Wathiq Enterprise'), _('Wathiq Basic')]

        res = [labels, values, sum(values)]

        return res

    # Function to get Labels and values for Opportunities according to different stages
    @api.model
    def get_wathiq_enterprise_by_stages_bar_chart(self, partner_id=False, product_id=False, account_manager_id=False):
        """Leads by Stage Pie"""
        crm_obj = self.env['crm.lead']
        domain = [('is_wathiq', '=', True), ('service_type',
                                             '=', 'enterprise'), ('for_aahd', '=', True)]
        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        first_stage_id = self.env['crm.stage'].search(
            [('for_aahd', '=', True)], order='sequence', limit=1)

        stages_name = ["Pending lead", "Pending Opp",
                       "Lost Opp", "Won Prop", "Pending Prop", "Lost Prop"]

        pending_lead_count = crm_obj.search_count(
            [('type', '=', 'lead')]+domain)

        pending_opp_count = crm_obj.search_count(
            [('type', '=', 'opportunity'), ('stage_id', '=', first_stage_id.id)]+domain)

        lost_opp_count = crm_obj.search_count(
            [('type', '=', 'opportunity'), ('probability', '=', 0), ('active', '=', False)]+domain)

        won_pro_count = crm_obj.search_count(
            [('type', '=', 'opportunity'), ('submission_status', '=', 'awarded')]+domain)

        pending_prop_count = crm_obj.search_count([('type', '=', 'opportunity'), (
            'stage_is_proposal', '=', True), ('proposal_status', '=', 'draft')]+domain)

        lost_prop_count = crm_obj.search_count([('type', '=', 'opportunity'), (
            'stage_is_submitted', '=', True), ('submission_status', '=', 'rejected')]+domain)

        stages_count = [pending_lead_count, pending_opp_count,
                        lost_opp_count, won_pro_count, pending_prop_count, lost_prop_count]

        return [stages_count, stages_name, sum(stages_count)]

    # Function to get Labels and values for Opportunities according to different stages
    @api.model
    def get_wathiq_batch_by_stages_bar_chart(self, partner_id=False, product_id=False, account_manager_id=False):
        """Leads by Stage Pie"""
        crm_obj = self.env['crm.lead']
        domain = [('is_wathiq', '=', True), ('service_type',
                                             '=', 'batch'), ('for_aahd', '=', True)]
        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        # first_stage_id = self.env['crm.stage'].search(
        #     [('team_id', '=', False)], order='sequence', limit=1)

        first_stage_id = self.env['crm.stage'].search(
            [('for_aahd', '=', True)], order='sequence', limit=1)

        stages_name = ["Pending lead", "Pending Opp",
                       "Lost Opp", "Won Prop", "Pending Prop", "Lost Prop"]

        pending_lead_count = crm_obj.search_count(
            [('type', '=', 'lead')]+domain)

        pending_opp_count = crm_obj.search_count(
            [('type', '=', 'opportunity'), ('stage_id', '=', first_stage_id.id)]+domain)

        lost_opp_count = crm_obj.search_count(
            [('type', '=', 'opportunity'), ('probability', '=', 0), ('active', '=', False)]+domain)

        won_pro_count = crm_obj.search_count(
            [('type', '=', 'opportunity'), ('submission_status', '=', 'awarded')]+domain)

        pending_prop_count = crm_obj.search_count([('type', '=', 'opportunity'), (
            'stage_is_proposal', '=', True), ('proposal_status', '=', 'draft')]+domain)

        lost_prop_count = crm_obj.search_count([('type', '=', 'opportunity'), (
            'stage_is_proposal', '=', True), ('submission_status', '=', 'rejected')]+domain)

        stages_count = [pending_lead_count, pending_opp_count,
                        lost_opp_count, won_pro_count, pending_prop_count, lost_prop_count]

        return [stages_count, stages_name, sum(stages_count)]

    # Function to get Labels and values for won Opportunities according to won revenue by month
    @api.model
    def get_opportunities_month_chart(self, partner_id=False, product_id=False, account_manager_id=False):
        """ chart"""
        domain = [('type', '=', 'opportunity'), ('is_wathiq', '=', True),
                  ('stage_id.is_won', '=', True), ('service_type', '=', 'basic')]
        # domain = [('type', '=', 'opportunity'), ('is_wathiq',
        #                                          '=', True), ('service_type', '=', 'basic')]
        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        opportunity_data = self.env['crm.lead'].read_group(
            domain=domain,
            fields=['expected_revenue', 'won_revenue'], groupby=['create_date:month']
        )

        month_names = []
        won_revenue_val = []
        expected_revenue_val = []
        for oppor in opportunity_data:
            month_names.append(oppor.get('create_date:month', ''))
            won_revenue_val.append(
                oppor.get('won_revenue', 0) if oppor.get('won_revenue') else 0)

        month = [month_names, expected_revenue_val, won_revenue_val]
        return month

    # Function to get Labels and values for won Opportunities according to won revenue by year
    @api.model
    def get_the_annual_target(self, partner_id=False, product_id=False, account_manager_id=False):
        domain = [('type', '=', 'opportunity'), ('is_wathiq', '=', True),
                  ('stage_id.is_won', '=', True), ('service_type', '=', 'batch')]

        # domain = [('type', '=', 'opportunity'), ('is_wathiq',
        #                                          '=', True), ('service_type', '=', 'batch')]
        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]

        if account_manager_id:
            domain += [('partner_id.account_manager_id',
                        '=', int(account_manager_id))]

        if product_id:
            domain += [('product_ids', 'in', [int(product_id)])]

        opportunity_data = self.env['crm.lead'].read_group(
            domain=domain,
            fields=['won_revenue'], groupby=['create_date:year']
        )
        year_names = []
        won_revenue_val = []
        for oppor in opportunity_data:
            year_names.append(oppor.get('create_date:year', ''))
            won_revenue_val.append(
                oppor.get('won_revenue', 0) if oppor.get('won_revenue') else 0)
        return [year_names, won_revenue_val, sum(won_revenue_val)]

    # Action print
    def action_dashboard_report_print(self):
        res_ids = self.search([])
        return {'res_ids': res_ids.ids}
        # return self.env.ref('thiqah_crm.thiqah_dashboard_reports').report_action(res_ids)
