# -*- coding: utf-8 -*-
"""
(1) https://docs.python.org/3/library/configparser.html : read configuratioin file.
"""
from odoo import models, fields, _
from odoo.exceptions import ValidationError

from urllib.parse import urlencode


class external_communication(models.Model):
    _name = 'external.agent.acquirer'
    _inherit = ['external.communication.utils']
    _description = 'Base External Communication Agent'

    name = fields.Char(required=True)
    provider = fields.Char(required=True)
    state = fields.Selection([
        ('disabled', 'Disabled'),
        ('enabled', 'Enabled'),
        ('test', 'Test Mode'),
    ], default='test')

    #####################################
    # base Details
    #####################################
    onboarding_url = fields.Char(required=True)

    #####################################
    # Authorization
    #####################################
    authorization_type = fields.Selection([
        ('no_auth', 'NO AUTHORIZATION'),
        ('api_key', 'API KEY'),
        ('bearer_token', 'BEARER TOKEN'),
        ('basic_auth', 'BASIC AUTHORIZATION'),
        ('query_params', 'QUERY PARAMS')
    ], default='no_auth')

    # api_key
    api_key_add_to = fields.Selection([
        ('header', 'Header'),
        ('query_params', 'QUERY PARAMS')
    ], default='header')

    api_key_key = fields.Char()
    api_key_value = fields.Char()

    # bearer_token
    bearer_token = fields.Char()

    # basic_auth
    username = fields.Char()
    password = fields.Char()

    # query_params
    query_params_ids = fields.One2many(
        'external.query.params', 'agent_acquirer_id')

    # endpoints
    endpoint_ids = fields.One2many(
        'external.agent.endpoint', 'agent_acquirer_id')

    #############
    # Views Outils
    #############

    def _compute_endpoint_count(self):
        self.ensure_one()
        endpoints_data = self.env['external.agent.endpoint'].read_group(
            domain=[('agent_acquirer_id', 'in', self.ids)],
            fields=['agent_acquirer_id'], groupby=['agent_acquirer_id']
        )

        self.endpoint_count = 0
        for group in endpoints_data:
            agent_acquirer = self.browse(group['agent_acquirer_id'][0])
            if agent_acquirer in self:
                agent_acquirer.endpoint_count += group['agent_acquirer_id_count']

    endpoint_count = fields.Integer(
        compute='_compute_endpoint_count', string='Endpoints Count')

    def action_view_endpoint(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'external_communication.act_agent_to_endpoints')

        action['domain'] = [
            ('agent_acquirer_id.id', 'in', self.ids)]

        return action

    #####################################

    def _prepare_endpoint(self, uri):
        return self.onboarding_url + uri

    def _prepare_params(self):
        values = {}
        for acquirer in self:
            for query_params_id in acquirer.query_params_ids:
                values[query_params_id.key] = query_params_id.value
        return values

    def _endpoint_with_parameter(self):
        if self.authorization_type == 'query_params':
            return '?'+urlencode(self._prepare_params())
        return ''

    def get_url(self):
        """
        :return
            url_s = {
                'authentication_endpoint_id':{
                    'method':'get',
                    'url':'url'
                    .........
                }
            }
        """
        url_s = {}
        for agent in self:
            for authentication_endpoint in agent.endpoint_ids:
                url_s[authentication_endpoint.id] = {
                    'method': authentication_endpoint.type,
                    'url': self._prepare_endpoint(
                        authentication_endpoint.uri)+self._endpoint_with_parameter()
                }

                # self._prepare_endpoint(
                #     authentication_endpoint.uri)+self._endpoint_with_parameter()

        return url_s

    # def authenticate(self):
    #     """.depending from the authorization_type
    #     """
    #     # Prepare authentication needs
    #     authenticate_params = {}
    #     if self.authorization_type == 'query_params':
    #         authenticate_params = self._prepare_params()

    #     url = self.get_authentication_url()
    #     return url+'?'+urlencode(authenticate_params)

    def do_action(self):
        """."""
        url_s = self.get_url()

        for _, value in url_s.items():
            # TODO: Need to split each response
            if value['method'] == 'get':
                response = self.get(value['url'])
