# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentType(models.Model):
    _name = 'document.type'
    _inherit = 'thiqah_project.base_type'
    _description = 'Document Type'

    code = fields.Char('code')
