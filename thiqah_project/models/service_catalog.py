# -*- coding: utf-8 -*-

from odoo import models, fields


class ServiceCatalog(models.Model):
    _name = 'thiqah_project.service_catalog'
    _inherit = ['mail.thread', 'mail.activity.mixin',
                'thiqah_project.base_type']
    _description = 'Thiqah Service catalog'
    _rec_name = 'name_en'

    order = fields.Char()
    service_type = fields.Many2one(
        'thiqah_project.service_type', help='List of Services types.')
    department_id = fields.Many2one(
        'hr.department', required=True, help='List contains all departments.')
    partner_id = fields.Many2one('res.partner')
    sla = fields.Integer()
    description = fields.Text()
    description_ar = fields.Text()
    active = fields.Boolean('Active', default=True)

    def name_get(self):
        res = []
        for catalog in self:
            name = catalog.name_en
            res += [(catalog.id, name)]
        return res
