# -*- encoding: utf-8 -*-

from odoo import http
from odoo.http import request
# from datetime import date, timedelta
from odoo.osv.expression import AND

from ...thiqah_portal.controllers.main import human_format


class ThiqahCrmController(http.Controller):

    def _build_paramter(self, record, fields, paramater_list):
        """."""
        start_date = None
        end_date = None
        # for field in fields:
        # if record == 'start_date':
        start_date = record.start_date.strftime(
            "%m/%d/%Y") if record.start_date else None
        # if field == 'end_date':
        end_date = record.end_date.strftime(
            "%m/%d/%Y") if record.end_date else None

        paramater_list.append(
            [record.name,
                record.client_id.name,
                record.project_id.name,
                record.responsible_id.name,
                start_date,
                end_date
             ]
        )
        return paramater_list

    @http.route('/render/legal/dashboard', type='json', website=True)
    def render_legal_dashboard(self):
        """
        :return {pre_end_count,end_count,contract_count}
        """
        values = {}
        thiqah_contracts = request.env['thiqah.contract'].sudo()
        # prepare domain(s)
        domain_running = [('state', '=', 'running')]
        domain_pre_end = [('state', '=', 'pre_end')]
        domain_end = [('state', '=', 'end')]

        # ORM
        running_records = thiqah_contracts.search(domain_running)
        pre_end_records = thiqah_contracts.search(domain_pre_end)
        end_records = thiqah_contracts.search(domain_end)

        values['running_count'] = len(running_records) if len(
            running_records) > 0 else 'N/A'

        values['pre_end_count'] = len(pre_end_records) if len(
            pre_end_records) > 0 else 'N/A'

        values['end_count'] = len(end_records) if len(
            end_records) > 0 else 'N/A'

        values['contracts_count'] = thiqah_contracts.search_count(
            []) if thiqah_contracts.search_count([]) else 'N/A'

        pre_end_list = []
        end_list = []
        runnig_list = []
        fields = ['name', 'client_id', 'project_id',
                  'responsible_id', 'start_date', 'end_date']

        # Outil for the before x day(s)
        # nbr_days_notif_contract = int(request.env['ir.config_parameter'].sudo(
        # ).get_param('nbr.days.notif.contract.responsible'))

        for thiqah_contract in thiqah_contracts.search([]):
            if thiqah_contract.state == 'pre_end':
                # build pre end value(s)
                pre_end_list = self._build_paramter(
                    thiqah_contract, fields, pre_end_list)

            if thiqah_contract.state == 'end':
                # build end value(s)
                end_list = self._build_paramter(
                    thiqah_contract, fields, end_list)

            # if date.today() == thiqah_contract.end_date - \
            #         timedelta(days=nbr_days_notif_contract):

            if thiqah_contract.state == 'running':
                # build runnig value(s)
                runnig_list = self._build_paramter(
                    thiqah_contract, fields, runnig_list)

        values['pre_end'] = pre_end_list
        values['end'] = end_list
        values['runnig'] = runnig_list

        return values

    @http.route('/bd/sales/dashboard', type='json', website=True)
    def render_bd_sales_dashboard(self):
        """."""
        values = {}
        crm_lead_sudo = request.env['crm.lead'].sudo()

        # Domain(s)
        domain = [('for_bd', '=', True), ('stage_id', '!=', False), ('is_wathiq', '=', False),
                  ('type', '=', 'opportunity')]
        domain_lost = [('for_bd', '=', True), ('is_wathiq',
                                               '=', False), ('active', '=', False)]

        # Shared Data
        bd_wining_opportunities = crm_lead_sudo.search(
            AND([domain, [
                ('stage_is_won', '=', True)
            ]])
        )

        lost_opportunities = crm_lead_sudo.search(domain_lost)

        # Total of opportunities
        values['total_opportunities'] = crm_lead_sudo.search_count(
            domain) + len(lost_opportunities)

        #  Total of won opportunities
        values['bd_winnig_opportunities'] = len(bd_wining_opportunities)

        # Total lost opportunities
        values['bd_lost_opportunities'] = len(lost_opportunities)

        # Revenue
        revenues_won_stage = sum([bd_opportunity.won_revenue
                                  for bd_opportunity in bd_wining_opportunities
                                  ])

        values['bd_revenue'] = human_format(revenues_won_stage)
        # lead Source
        xValues_lead_source = []
        yValues_lead_source = []
        products_amount = []
        for _source in request.env['lead.source'].sudo().search([]):
            xValues_lead_source.append(_source.name)

            crm_products_filter = request.env['crm.lead'].sudo().search(
                AND([domain, [('source_lead_id', '=', _source.id)]])
            )

            # get sumof  Won Proposal Amount(s)
            products_amount.append(
                str(human_format(sum(
                    [crm_product_filter.won_revenue for crm_product_filter in crm_products_filter])))
            )

            # get the number of opportunities
            yValues_lead_source.append(
                len(crm_products_filter)
            )

        values['lead_source_data'] = [
            xValues_lead_source, yValues_lead_source, products_amount]

        # Opportunities Values
        lost_amount = sum([
            lost_opportunity.won_revenue for lost_opportunity in lost_opportunities
        ])

        expected_revenue_all = sum(opportunity_stage.expected_revenue for opportunity_stage in request.env['crm.lead'].search(
            AND(
                [domain, [('stage_is_won', '=', False),
                          ('active', '=', True)]]
            )
        ))
        xValues_opportunities_values = ['Won', 'Lost', 'Expected Opps']
        yValues_opportunities_values = [
            revenues_won_stage,
            lost_amount,
            expected_revenue_all
        ]

        values['BdOpportunitiesValues'] = [
            xValues_opportunities_values, yValues_opportunities_values]

        request.env.cr.execute("""
                                select name,won_revenue
                                from crm_lead as lead_
                                where stage_is_won is true and active is true and is_wathiq is false and for_bd is true
                                order by won_revenue desc limit 10
                               """)

        results_awarded = request.env.cr.fetchall()

        projects_awarded = []
        for project_awarded in results_awarded:
            projects_awarded.append(
                (project_awarded[0], project_awarded[1] if project_awarded[1] else 0.00))

        # delete duplcated lead_.name
        mylist = list(dict.fromkeys(projects_awarded))

        values['projects_awarded_BD'] = projects_awarded

        return values
