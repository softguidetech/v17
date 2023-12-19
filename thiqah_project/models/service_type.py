# -*- coding: utf-8 -*-

from odoo import models, fields


class ServiceType(models.Model):
    _name = 'thiqah_project.service_type'
    _inherit = 'thiqah_project.base_type'
    _description = 'Thiqah Service Type'

    def name_get(self):
        res = []
        for service_type in self:
            name = service_type.name_en
            res += [(service_type.id, name)]
        return res
