# -*- coding: utf-8 -*-

from odoo import models, fields


class ContractType(models.Model):
    _name = 'thiqah.project.contract.type'
    _inherit = 'thiqah_project.base_type'
    _description = 'Thiqah Project Contract Type'
    _rec_name = 'name_en'

    def name_get(self):
        res = []
        for contract in self:
            name = contract.name_en
            res += [(contract.id, name)]
        return res
