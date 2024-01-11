from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.http import request


class AuditlogHTTPRequestInherit(models.Model):
    _inherit = 'auditlog.log'

    # Purpose : User Analysis Report(s)
    # user_category_id = fields.Many2one(
    #     related='http_session_id.user_id.thiqah_category_id', store=True)

    # user_category_id = fields.Integer(
    #     compute='_compute_user_category_id', store=True)

    # @api.depends('http_session_id')
    # def _compute_user_category_id(self):
    #     for log in self:
    #         # get the user depending on the res_id attrubute.
    #         user_id = self.env['res_users'].browse([int(self.res_id)])
    #         # do_action
    #         log.user_category_id = user_id.thiqah_category_id.id
