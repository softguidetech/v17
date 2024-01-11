# -*- coding: utf-8 -*-

from odoo import models, fields


class RequestStage(models.Model):
    _name = 'thiqah_project.request_stage'
    _order = 'sequence, id'
    _description = 'Thiqah Project Request Stage'

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    catalog_ids = fields.Many2many('thiqah_project.service_catalog',
                                   'catalog_request_stage_rel', 'request_stage_id', 'calatog_id', string='Catalogs')
