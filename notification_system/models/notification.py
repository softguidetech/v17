# -*- coding: utf-8 -*-
from odoo import models, fields


class notificationsystem(models.Model):
    _name = 'notification.system'
    _description = 'Notification System'

    message_id = fields.Char()
    name = fields.Char(help="Title")
    description = fields.Text("Description")
    user_id = fields.Many2one('res.users')
    url_redirect = fields.Char()
    model_id = fields.Integer()
    model_name = fields.Char()
    # Outil for the portal.
    is_open = fields.Boolean(default=False)
    type = fields.Selection([('reject', 'Reject'), ('confirm', 'confirm'), ('opportunity', 'opportunity'), ('lead', 'lead')])

    # Cron Job : Delete any notification linked with a non existent record.
    def cron_delete_notifications(self):
        """"""
        for rec in self:
            if not rec.model_name == 'res.users':
                record = self.env[rec.model_name].sudo().browse([rec.model_id])
                if not record:
                    rec.unlink()
