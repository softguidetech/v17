# -*- coding: utf-8 -*-
"""
(1) https://docs.python.org/3/library/configparser.html : read configuratioin file.
"""
from odoo import models, fields, api


class ExternalAbstractModel(models.Model):
    _name = 'external.agent.abstract_model'
    _description = 'External Communication Abstract Model'

    name = fields.Char('Name', required=True)

    model_id = fields.Many2one('ir.model', string='Model')

    active = fields.Boolean(string='Active', default=True)
