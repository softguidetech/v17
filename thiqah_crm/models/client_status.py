# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class ClientStatus(models.Model):
    _name = "client.status"
    _description = "Client Status"

    name = fields.Char(translate=True)
