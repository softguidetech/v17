# -*- coding: utf-8 -*-
from odoo import models, fields


class ParametesClickUp(models.Model):
    _inherit = 'ir.attachment'

    # Overriding {set readonly to Ture}
    name = fields.Char('Name', required=True, readonly=True)
    datas = fields.Binary(string='File Content (base64)',
                          compute='_compute_datas', inverse='_inverse_datas', readonly=True)
