# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_wathiq = fields.Boolean('Is Wathiq', default=False)

    # These fields are dedeicated to the aahd sales dashbaord.
    is_digital_aahd = fields.Boolean(
        'Is digital', groups="thiqah_crm.group_thiqah_aahd_sales_manager_grp")
    is_non_digital_aahd = fields.Boolean(
        'Is Non-Digital', groups="thiqah_crm.group_thiqah_aahd_sales_manager_grp")
