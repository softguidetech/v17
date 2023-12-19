# -*- coding: utf-8 -*-

from odoo import models, fields

# 'primary_color': '#123456',
# 'secondary_color': '#789101',

_selection_content = [
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('success', 'Success'),
    ('danger', 'Danger'),
    ('warning', 'Warning'),
]

class ActionType(models.Model):
    _name = 'thiqah_project.action_type'
    _inherit = 'thiqah_project.base_type'
    _description = 'Thiqah Project Action Type'

    _rec_name = 'name_en'


    color = fields.Selection(_selection_content, default='primary')

    def name_get(self):
        res = []
        for action_type in self:
            name = action_type.name_en
            res += [(action_type.id, name)]
        return res
