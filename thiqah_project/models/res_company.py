# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    assignment_advisor_id = fields.Many2one('res.users')
    digital_solution__id = fields.Many2one('res.users')
