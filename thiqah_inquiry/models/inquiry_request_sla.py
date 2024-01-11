# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from ...thiqah_inquiry.models.inquiry_request import REQUEST_TYPE, URGENCY

class InquiryRequestSLA(models.Model):
    _name = 'inquiry.request.sla'

    request_type = fields.Selection(REQUEST_TYPE, string='Request Type')
    urgency = fields.Selection(URGENCY, string='Urgency')
    sla_days = fields.Integer(string='SLA Days')

    def name_get(self):
        result = []
        for sla in self:
            name = f'{sla.request_type}-{sla.urgency} ({sla.sla_days})'
            result.append((sla.id, name))
        return result