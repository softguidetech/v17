# -*- coding: utf-8 -*-
"""
(1) https://docs.python.org/3/library/configparser.html : read configuratioin file.
"""
from odoo import models, fields, api, _


class ExternalCommunication(models.Model):
    _name = 'external.agent.endpoint'
    _description = 'Communication endpoints'

    name = fields.Char()

    uri = fields.Char(required=True)

    type = fields.Selection([
        ('authentication', 'Authentication'),
        ('get', 'GET'),
        ('post', 'POST'),
    ])

    # Endpoint Parameters
    parameter_ids = fields.Many2many(
        'external.query.params',
        'endpoint_parameters_relation',
        'endpoint_id',
        'parameter_id',
        string='Endpoint Parameters',
    )
    
    #  Relationship
    agent_acquirer_id = fields.Many2one('external.agent.acquirer')

    ###################
    # Odoo Core | ORM
    ###################

    # def name_get(self):
    #     result = []
    #     for endpoint in self:
    #         name = endpoint.code + ' ' + endpoint.name
    #         result.append((endpoint.id, name))
    #     return result

    sequence = fields.Char(string='Order Reference', required=True,
                           readonly=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'external.agent.endpoint') or _('New')
        res = super(ExternalCommunication, self).create(vals)
        return res
