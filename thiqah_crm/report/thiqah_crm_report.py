# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.osv.expression import AND


class ThqahCrmReport(models.TransientModel):
    _name = 'thiqah.crm.report'
    _description = 'Thiqah Crm Report'

    report_type = fields.Selection([('awarded_opportunity', 'Awarded Opportunities'),
                                    ('submitted_opportunity',
                                     'Submitted Opportunities'),
                                    ('potential_opportunities',
                                     'Potential Opportunities'),
                                    ], string="Report Type", default='awarded_project')

    # Report Name

    def _get_report_base_filename(self):
        return _("Opportunities Status")

    # Get report data according to report type choosed
    def get_thiqah_opportunities_proposal_data(self):
        # domain = [('type', '=', 'opportunity'), ('is_wathiq', '=',
        #                                          True), ('stage_id.is_proposal', '=', True)]

        domain = [('type', '=', 'opportunity'), ('active', '=', True)]

        crm_obj = self.env['crm.lead']
        res = {}
        if self.report_type == 'awarded_opportunity':
            # Customization :
            # Retrive Data only when the lead in stage(submitted) && status(draft or pending)

            # domain_award = domain+[('proposal_status', '=', 'awarded')]
            get_award_data = []
            awarded_total = 0
            # opp_awarded = crm_obj.search(domain_award)
            opp_awarded = crm_obj.search(
                AND([domain, [
                    ('stage_is_submitted', '=', True),
                    ('submission_status', '=', 'awarded'),
                ]])
            )
            for rec in opp_awarded:
                get_award_data.append({
                    'customer': rec.partner_id.name if rec.partner_id.id else '',
                    'opportunity_name': rec.name,
                    'account_manager': rec.account_manager_id.name if rec.account_manager_id else '',
                    'scoop_details': rec.scoop_details if rec.scoop_details else '',
                    'deadline': rec.project_date_deadline if rec.project_date_deadline else '',
                    'execution_time': rec.project_execution_time if rec.project_execution_time else '',
                    'total_revenue': rec.won_revenue if rec.won_revenue else '',
                    'revenue_2022': (rec.won_revenue / rec.project_execution_time) if rec.project_execution_time else '',
                })
                awarded_total += rec.won_revenue
            res.update({'awarded_data': get_award_data, 'count_awarded': len(
                opp_awarded.ids) if opp_awarded.ids else '', 'awarded_total': awarded_total if awarded_total > 0 else ''})

        if self.report_type == 'submitted_opportunity':
            # Customization :
            # Retrive Data only when the lead in stage(submitted) && status(draft or pending)

            # domain_submitted = domain + [('proposal_status', '=', 'submitted')]
            get_submitted_data = []
            submitted_total = 0
            # opp_submitted = crm_obj.search(domain_submitted)
            opp_submitted = crm_obj.search(
                AND([domain, [
                    ('stage_is_submitted', '=', True),
                    ('submission_status', '=', 'draft'),
                ]])
            )

            for rec in opp_submitted:
                get_submitted_data.append({
                    'customer': rec.partner_id.name if rec.partner_id.id else '',
                    'opportunity_name': rec.name,
                    'account_manager': rec.account_manager_id.name if rec.account_manager_id else '',
                    'scoop_details': rec.scoop_details if rec.scoop_details else '',
                    'deadline': rec.project_date_deadline if rec.project_date_deadline else '',
                    'execution_time': rec.project_execution_time if rec.project_execution_time else '',
                    'total_revenue': rec.won_revenue if rec.won_revenue else '',
                    'revenue_2022': (rec.won_revenue / rec.project_execution_time) if rec.project_execution_time else '',
                })
                submitted_total += rec.won_revenue

            res.update({'submitted_data': get_submitted_data, 'count_submitted': len(opp_submitted.ids)
                       if opp_submitted.ids else '', 'submitted_total': submitted_total if submitted_total > 0 else ''})

        if self.report_type == 'potential_opportunities':
            # Customization :
            # Retrive Data only when the lead in stage(proposal) && status(pending)

            # domain_potential = domain+[]
            get_potential_data = []
            potential_total = 0
            opp_potential = crm_obj.search(
                AND([domain, [
                    ('stage_is_proposal', '=', True),
                    ('proposal_status', '=', 'draft'),
                ]])
            )

            for rec in opp_potential:
                get_potential_data.append({
                    'customer': rec.partner_id.name if rec.partner_id.id else '',
                    'opportunity_name': rec.name,
                    'account_manager': rec.account_manager_id.name if rec.account_manager_id else '',
                    'scoop_details': rec.scoop_details if rec.scoop_details else '',
                    'deadline': rec.project_date_deadline if rec.project_date_deadline else '',
                    'execution_time': rec.project_execution_time if rec.project_execution_time else '',
                    'total_revenue': rec.won_revenue if rec.won_revenue else '',
                    'revenue_2022': (rec.won_revenue / rec.project_execution_time) if rec.project_execution_time else '',
                })
                potential_total += rec.won_revenue


            res.update({'potential_data': get_potential_data, 'count_potential': len(opp_potential.ids)
                       if opp_potential.ids else '', 'potential_total': potential_total if potential_total > 0 else ''})

        return res

    # Action print
    def action_report_print(self):
        return self.env.ref('thiqah_crm.thiqah_Opportunities_report').report_action(self)
