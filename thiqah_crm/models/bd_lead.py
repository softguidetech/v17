

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class OpportunitySize(models.Model):
    _name = "opportunity.size"
    _rec_name = "size_value"
    _description = "Opportunity Size"

    size_value = fields.Float("Opportunity size", required=True)


class SPManager(models.Model):
    _name = "sp.manager"
    _description = "Sp Manager"

    name = fields.Char(translate=True, required=True)


class ResStakeholders(models.Model):
    _name = "res.stakeholder"
    _description = "Res Stakeholder"

    name = fields.Char(translate=True, required=True)


class InternalStatus(models.Model):
    _name = "internal.status"
    _description = "Internal Status"

    name = fields.Char(translate=True, required=True)


class LeadSource(models.Model):
    _name = "lead.source"
    _description = "lead source"

    name = fields.Char(translate=True, required=True)
    code = fields.Char(required=True)

    event_as_source = fields.Boolean(default=False)
