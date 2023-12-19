# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ThqahCrmReport(models.TransientModel):
    _name = 'thiqah.ontime.report'
    _description = 'Thiqah Ontime Report'

    customer_ids = fields.Many2many('res.partner', string="Customers")

    # Report Name
    def _get_report_base_filename(self):
        return _("On Time Report")

    # Get report data according to report type choosed
    def get_thiqah_tickets_on_time_report_data(self):
        domain = []
        helpdesk_obj = self.env['helpdesk.ticket']

        if self.customer_ids:
            domain = domain+[('partner_id', 'in', self.customer_ids.ids)]
        data = []
        res = {}
        sla_policies = []
        tickets = helpdesk_obj.search(domain)
        total_on_time_tickets = 0
        for rec in tickets:
            sla_policies = []
            for sla_status in rec.sla_status_ids:
                if sla_status.status == 'reached':
                    total_on_time_tickets += 1
                    status = _('On time')
                elif sla_status.status == 'failed':
                    status = _('Not on time')
                else:
                    status = _('Not Yet')
                sla_policies.append(
                    {'sla_name': sla_status.sla_id.name, 'sla_status': status})

            data.append({
                'customer': rec.partner_id.name if rec.partner_id.id else '',
                'name': rec.name,
                'sla_policies': sla_policies,
                'ticket_stage': rec.stage_id.name,
            })
        res.update({'data': data, 'total_tickets': len(tickets.ids),
                   'total_ontime_tickets': total_on_time_tickets})

        return res

    # Action print
    def action_report_print(self):
        return self.env.ref('thiqah_crm.thiqah_on_time_tickets_report').report_action(self)
