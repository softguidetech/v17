# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class Attachments(models.Model):
    _inherit = "ir.attachment"

