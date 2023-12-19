# -*- coding: utf-8 -*-

from odoo import models, fields


class RiskType(models.Model):
    _name = 'thiqah.project.risk.type'
    _inherit = 'thiqah_project.base_type'
    _description = 'Thiqah Project Risk Type'

    def name_get(self):
        res = []
        for risk in self:
            name = risk.name_en
            res += [(risk.id, name)]
        return res
