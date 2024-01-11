# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
   
    background_image = fields.Binary(
        string='Apps Menu Background Image',
        attachment=True
    )
    company_title = fields.Char("Company Title",translate=True)
    