# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class CrmTeam(models.Model):
    _inherit = "crm.team"
  
    
    account_ids        = fields.One2many('res.partner','team_id','Accounts')