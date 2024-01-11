# -*- coding:utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AuditlogLogin(models.Model):
    _name = 'auditlog.login'

    user_id = fields.Many2one('res.users')

    user_category_id = fields.Integer()

    # @api.depends('user_id')
    # def _compute_user_category_id(self):
    #     for record in self:
    #         if record.user_id.thiqah_category_id.id:
    #             record.user_category_id = record.user_id.thiqah_category_id.id
    #         else:
    #             record.user_category_id = None

    redirect_to = fields.Char()

    # create_date == login_date
