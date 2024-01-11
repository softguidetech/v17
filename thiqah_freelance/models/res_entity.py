# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Entity(models.Model):
    _name = 'res.entity'
    _description = 'Entities'
    _rec_name = 'full_name'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    full_name = fields.Char(string='Full Name')