# -*- coding: utf-8 -*-

from odoo import models, fields


class BaseType(models.Model):
    _name = 'thiqah_project.base_type'

    name_ar = fields.Char(
        "Name (Arabic)", help="Name in english.")

    name_en = fields.Char(
        "Name (English)", help="Name in arabic.", required=True,translate=True)

    code = fields.Char()


    