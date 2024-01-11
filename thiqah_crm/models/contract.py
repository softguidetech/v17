# -*- encoding: utf-8 -*-
from odoo import models, fields
from datetime import date, timedelta


class ThiqahContract(models.Model):
    _name = 'thiqah.contract'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin']

    _description = 'Thiqah Contract'

    name = fields.Char(required=True)

    client_id = fields.Many2one('res.partner')
    project_id = fields.Many2one('project.project')
    project_name = fields.Char(
        related='project_id.name', string='Project Name')

    responsible_id = fields.Many2one('res.users')

    start_date = fields.Date()
    end_date = fields.Date()

    state = fields.Selection([
        ('running', 'Runnig'),
        ('pre_end', 'Pre End'),
        ('end', 'End'),
    ], default='running')

    # Outil for email template
    nbr_days_notif = fields.Integer()

    # State Actions
    def set_to_running(self):
        for rec in self:
            rec.write({
                'state': 'running'
            })

    def set_to_pre_end(self):
        for rec in self:
            rec.write({
                'state': 'pre_end'
            })

    def set_to_end(self):
        for rec in self:
            rec.write({
                'state': 'end'
            })

    def is_notification_day(self, date_notifcation):
        """"""

    def cron_notify_contract_responsible(self):
        """
        Notify the responsible of the contract before x days(setting dynamically in the settings)
        """
        concerned_users = []
        # get the configuration parameters
        activate_notif_contract = self.env['ir.config_parameter'].sudo(
        ).get_param('activate.notif.contract.responsible')
        domain = []
        if activate_notif_contract:
            # Preproccesing of the number of days
            nbr_days_notif_contract = int(self.env['ir.config_parameter'].sudo(
            ).get_param('nbr.days.notif.contract.responsible'))

            # get the eamil template id from the settings
            email_template_id_contract_responsible = self.env['ir.config_parameter'].sudo(
            ).get_param('email_template.notif.contract_responsible') or False

            # get only the contract having pre end state.
            domain = [
                ('state', '=', 'pre_end')]

            for rec in self.search(domain):
                date_notif_contract = rec.end_date - \
                    timedelta(days=int(nbr_days_notif_contract))

                if date.today() == date_notif_contract:
                    # DO ACTION
                    rec.write({
                        'nbr_days_notif': nbr_days_notif_contract
                    })
                    if email_template_id_contract_responsible:
                        # Gathering concerned users
                        concerned_users = [rec.responsible_id]
                        for user_ in self.env['res.users'].sudo().search([]):
                            if user_.has_group('thiqah_crm.legal_team_group_'):
                                concerned_users.append(user_)

            for concerned_user in concerned_users:
                self.env['mail.template'].browse(
                    int(email_template_id_contract_responsible)).send_mail(rec.id, force_send=True, email_values={'email_to': concerned_user.email})
