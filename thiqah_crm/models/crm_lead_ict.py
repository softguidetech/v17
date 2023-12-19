# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class CrmLeadIct(models.Model):
    _name = "crm.lead.ict"
  
    
    name = fields.Char(string="ICT")
    
    #Child
    ict_services = fields.One2many('crm.lead.ict_services','parent_ict' ,string="ICt Services")
    
    

class SectorsOfInterest(models.Model):
    _name = "crm.lead.sectors_of_interest"
  
    
    name = fields.Char()
    
    
class TypesOfServices(models.Model):
    _name = "crm.lead.types_of_services_provided"
  
    
    name = fields.Char()
    
    
    
    




class CrmLeadIctServices(models.Model):
    _name = "crm.lead.ict_services"
  
    
    name = fields.Char(string="ICT Services")
    
    #Parent
    parent_ict = fields.Many2one('crm.lead.ict',string="ICT")
    
    #Child
    ict_services_infos = fields.One2many('crm.lead.ict_services_info','parent_ict_services' ,string="ICt Services Info")



class CrmLeadIctServicesInfo(models.Model):
    _name = "crm.lead.ict_services_info"
  
    
    name = fields.Char(string="ICT Services Info")
    
    #Parent
    parent_ict_services = fields.Many2one('crm.lead.ict_services',string="ICT Services ")