# -*- coding: utf-8 -*-

'''
Support: https://requests.readthedocs.io/en/latest/user/quickstart/
'''
from odoo import models, fields, api

import requests


class ExternalCommunicationUtils(models.AbstractModel):
    _name = 'external.communication.utils'

    def get(self, endpoint, params=None, headers=None, cookies=None):
        """."""
        if params:
            return requests.get(endpoint, params)
        return requests.get(endpoint)

    def post(self, endpoint, data, json=None):
        """requests.post(url, data={key: value}, json={key: value}, args)"""
        return requests.get(endpoint, data=data)
