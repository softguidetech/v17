# -*- coding: utf-8 -*-

from odoo import models, fields

""""
    Main purpose : + The idea is to extend the users model to add a boolean describing any additional group for the user portal(the same for the public also if there is need).
    <> External means public or portal user.
"""


class ExternalUser(models.Model):
    _name = 'external.user'
    _description = 'External User'

    group_id = fields.Many2one(
        'res.groups', string='Group', ondelete='restrict', index=True)

    user_id = fields.Many2one('res.users')
