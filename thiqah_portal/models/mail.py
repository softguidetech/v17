# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError
from collections import defaultdict


class MailExtension(models.Model):
    _inherit = 'mail.message'

    for_approve_reject = fields.Boolean(default=False)