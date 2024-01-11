# -*- coding: utf-8 -*-
"""
(1) https://docs.python.org/3/library/configparser.html : read configuratioin file.
"""
from odoo import models, fields, api


class ExternalQueryParams(models.Model):
    _name = 'external.query.params'
    _description = 'External Query Parameters'

    name = fields.Char()
    key = fields.Char()
    value = fields.Char()

    agent_acquirer_id = fields.Many2one('external.agent.acquirer')
