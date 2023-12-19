# -*- coding: utf-8 -*-

from odoo import models, fields


class Country(models.Model):
    _inherit = 'res.country'

    nationality_ar = fields.Char()
    nationality_en = fields.Char()
