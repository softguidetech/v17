# -*- encoding:utf-8 -*-
from odoo import models, fields


class UserCategory(models.Model):
    _name = 'user.category'

    name = fields.Char()
    code = fields.Char()
