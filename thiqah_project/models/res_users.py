# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    thiqah_projects_ids = fields.One2many(
        'project.project', 'user_rule_id', compute='_compute_thiqah_projects_ids')

    request_id = fields.Many2one('thiqah.project.service.request')
    request_actor_id = fields.Many2one('thiqah.project.service.request')

    def _compute_thiqah_projects_ids(self):
        for user in self:
            # get all
            projects_ids = self.env['project.project'].sudo().search([
                ('user_id', '=', self.env.user.id)
            ]).ids
            user.update({
                'thiqah_projects_ids': [(6, 0, projects_ids)]
            })

    @api.model_create_multi
    def create(self, vals_list):
        """
        +Considering portal users as employees having the following groups.
        ++set share to True.
        -->technically, we can link a portal user with an emplyee.

        """

        result = super().create(vals_list)
        result.share = False
        return result
