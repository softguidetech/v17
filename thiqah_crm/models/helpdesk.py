# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # is_close = fields.Boolean(related="stage_id.is_close")
    is_close = fields.Boolean("is_close")
    category_portfolio_id = fields.Many2one('category.portfolio', string='Portfolio Category')
    vb_account_id = fields.Many2one(related="category_portfolio_id.vb_account_id")
    sp_manager_id = fields.Many2one(related="partner_id.sp_manager_id")
    activate_notification = fields.Boolean(string='Activate Notification')

# #     add function onchange stage
    @api.onchange('stage_id')
    def onchange_stage_id(self):
        if self.stage_id:
            self.date_last_stage_update = fields.Datetime.now()
            self.activate_notification = False

#     add function cron ticket progress
    @api.model
    def cron_ticket_progress(self):
        tickets = self.search([('activate_notification', '=', True)])
        for ticket in tickets:
            if ticket.activate_notification:
                if not ticket.date_last_stage_update:
                    date_last_stage_update = ticket.create_date
                    now = datetime.now()
                    delta = now - date_last_stage_update
                    if delta.days >= 3:
                        template_id.email_to = ticket.category_portfolio_id.chief_id and ticket.category_portfolio_id.chief_id.id
                        template_id = self.env.ref('thiqah_crm.email_template_ticket_Chief_reminder')
                        if template_id:
                            template_id.send_mail(ticket.id, force_send=True)
                    if delta.days >= 2:
                        template_id.email_to = ticket.category_portfolio_id.debuty_id and ticket.category_portfolio_id.debuty_id.id
                        template_id = self.env.ref('thiqah_crm.email_template_ticket_debuty_reminder')
                        if template_id:
                            template_id.send_mail(ticket.id, force_send=True)
                    if delta.days >= 1:
                        template_id = self.env.ref('thiqah_crm.email_template_ticket_sp_manager_reminder')
                        if template_id:
                            template_id.email_to = ticket.category_portfolio_id.sp_manager_id and ticket.category_portfolio_id.sp_manager_id.id
                            template_id.send_mail(ticket.id, force_send=True)



class HelpdeskSLA(models.Model):
    _inherit = "helpdesk.sla"

    notification_level = fields.Selection([('level1', 'To Sp Manager'),
                                           ('level2', 'To Vb Manager')
                                           ], string="Notify Level", default='level1')
    activate_notification = fields.Boolean('Activate Notification', default=False)
    nbr_minutes_notif = fields.Integer('Before Number of Minutes to notify')
    email_template_id = fields.Many2one('mail.template', 'Email Template', domain="[('model','=','helpdesk.ticket')]")

    # Fct to notify Sp Or Vb Manager before x hours of sla deadline
    @api.model
    def _cron_notification_before_sla_deadline(self):
        sla_active = self.search([('activate_notification', '=', True)])
        format = "%Y-%m-%d %H:%M"
        for rec in sla_active:
            user_tz = self.env.user.tz or self.env.context.get('tz')
            user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
            date_now = (datetime.now().astimezone(user_pytz).replace(tzinfo=None)).strftime(format)
            _logger.info('date_now %s', date_now)
            sla_ticket_ids = self.env['helpdesk.sla.status'].search(
                [('sla_id', '=', rec.id), ('status', '=', 'ongoing')])
            for tick in sla_ticket_ids:  # .filtered(lambda tick:  tick.deadline - timedelta(seconds=self.nbr_seconds_notif) == date_now):
                _logger.info('tick.deadline %s', tick.deadline)
                tick_deadline = (tick.deadline.astimezone(user_pytz).replace(tzinfo=None))
                _logger.info('tick.deadline af %s', tick.deadline)
                tick_notif = (tick_deadline - timedelta(minutes=rec.nbr_minutes_notif)).strftime(format)
                _logger.info('tick_notif %s', tick_notif)
                _logger.info('date_now %s', date_now)
                if tick_notif == date_now:
                    _logger.info('yesss  tick id %s', tick)
                    partner_id = tick.ticket_id.sp_manager_id if rec.notification_level == 'level1' else tick.ticket_id.vb_account_id
                    _logger.info('partner_id %s', partner_id)
                    if rec.email_template_id and partner_id:
                        email_values = {'email_to': partner_id.email, 'partner_ids': partner_id.ids}
                        res = rec.email_template_id.send_mail(tick.ticket_id.id, force_send=True,
                                                              email_values=email_values)

        return True


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    show_in_dashbaord = fields.Boolean("Show This Stage On Dashboard", default=True)

    # fetch all data
    @api.model
    def get_tickets_dashboard_data(self, partner_id=False):

        domain_helpdesk = []
        domain_sla_helpdesk = []
        list_stages = []
        list_slas = []
        helpdesk_obj = self.env['helpdesk.ticket']

        if partner_id:
            domain_helpdesk += [('partner_id', '=', int(partner_id))]
            domain_sla_helpdesk += [('partner_ids', 'in', [int(partner_id)])]
        # Tickets
        all_tickets = helpdesk_obj.search(domain_helpdesk)

        stage_ids = self.env['helpdesk.stage'].search([('show_in_dashbaord', '=', True)])
        sla_ids = self.env['helpdesk.sla'].search(domain_sla_helpdesk)

        for stage in stage_ids:
            stage_count = helpdesk_obj.search_count(domain_helpdesk + [('stage_id', '=', stage.id)])
            list_stages.append([stage.id, stage.name, stage_count])

        for sla in sla_ids:
            success_sla = len(all_tickets.filtered(lambda tick: tick.sla_success and sla.id in tick.sla_ids.ids).ids)
            failed_sla = len(all_tickets.filtered(lambda tick: tick.sla_fail and sla.id in tick.sla_ids.ids).ids)
            list_slas.append([sla.id, sla.name, success_sla, failed_sla])

        res = {'all_tickets': len(all_tickets.ids), 'stages_tickets': list_stages, 'all_sla': list_slas,
               'total_sla': len(list_slas)}
        return res
