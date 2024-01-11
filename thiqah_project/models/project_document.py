# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentInherit(models.Model):
    _inherit = 'documents.document'

    project_id = fields.Many2one('project.project')


class ProjectDocument(models.Model):
    _name = 'thiqah.project.document'
    _description = 'Thiqah Project Document'

    name = fields.Char('Name')
    document_type_id = fields.Many2one('document.type')
    description = fields.Text('Description')
