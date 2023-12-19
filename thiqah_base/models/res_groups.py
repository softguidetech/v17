# -*- coding: utf-8 -*-

from odoo import models, fields


""""
    Main purpose : + The idea is to extend the users model to add a boolean describing any additional group for the user portal.
    <> External means public or portal user.
"""


class ResGroupsInherit(models.Model):
    _inherit = 'res.groups'

    external_user_id = fields.Many2one('res.users')
