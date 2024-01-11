# -*- coding: utf-8 -*-

from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    requiring_action_id = fields.Many2one('thiqah.portal.requiring.action')



    