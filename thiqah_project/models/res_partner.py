# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    # Tools for financial dahsbaord
    # Attribute projects to each partner to ensure the filter on the financial dahsbaord(computed field)

    project_ids = fields.One2many(
        'project.project', 'partner_id_financial', compute='_compute_project_ids')

    def _compute_project_ids(self):
        for partner in self:
            project_ids = self.env['project.project'].sudo().search([
                ('partner_id', '=', partner.id)
            ]).ids
            partner.update({
                'project_ids': [(6, 0, project_ids)]
            })
