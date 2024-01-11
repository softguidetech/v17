# -*- coding: utf-8 -*-

from datetime import datetime
from hijri_converter import Hijri, Gregorian

from odoo import api, fields, models, _

class FreelanceApplication(models.Model):
    _name = 'freelance.application'
    _description = 'Freelancer Application'
    _inherit = ['mail.thread','mail.activity.mixin','portal.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = "full_name"

    company_id = fields.Many2one('res.company', string='Company', readonly=True, store=True,
        default=lambda self: self.env.company)

    request_id = fields.Many2one('freelance.request', string='Freelance request')
    entity_code = fields.Char(related = 'request_id.entity_code')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', ondelete='restrict')
    
    # Personal Info
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    full_name = fields.Char(string='Full Name',compute='_compute_full_name')
    id_type = fields.Selection([('national_id', 'National ID'), ('passport', 'Passport')], string='ID Type')
    id_number = fields.Char(string='ID Number')
    mobile_number = fields.Char(string='Mobile Number')
    email = fields.Char(string='E-mail')
    nationality_id = fields.Many2one('res.country', string='Nationality')
    address = fields.Char(string='Address')

    # Contract Information
    salary = fields.Monetary(string='Salary')
    withholding_tax = fields.Boolean(string='Withholding tax')
    withholding_tax_comment = fields.Text('Withholding Tax Comment')
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    start_date = fields.Date('Start Date',default=fields.Date.today,)
    end_date = fields.Date('End Date',)

    # Bank Information
    bank_country = fields.Many2one('res.country', string='Bank Country')
    bank_name = fields.Char( string='Bank')
    branch_name = fields.Char(string='Branch')
    bank_id = fields.Char( string='Bank')
    branch_id = fields.Char(string='Branch')
    account = fields.Char(string='Account')
    beneficiary_name = fields.Char(string='Beneficiary Name')
    iban = fields.Char(string='IBAN')

    #APIs Fields
    api_supplier_site_id = fields.Char()
    api_freelancer_name = fields.Char()
    #Helper fields
    is_bank_added = fields.Boolean(default=False)


    def _compute_full_name(self):
        for rec in self:
            rec.full_name = str(rec.first_name) + ' ' + str(rec.last_name)

    def create(self, vals):
        partner_vals = {
                'name': vals.get('first_name') + ' ' + vals.get('last_name'),
                'email': vals.get('email'),
                'mobile': vals.get('mobile_number'),
                'country_id': vals.get('nationality_id'),
                'is_freelancer': True,
            }
        vals['partner_id'] = self.env['res.partner'].sudo().create(partner_vals).id
        res = super().create(vals)
        return res

    def _get_attchments(self):
        return self.env['ir.attachment'].search([('res_id','=',self.id), ('res_model', '=', self._name)])

    def get_hijri_date(self, date_str):
        if date_str:
            now = datetime.strptime(str(date_str), '%Y-%m-%d')
            um = Gregorian(now.year, now.month, now.day).to_hijri()
        else:
            now = datetime.now()
            um = Gregorian(now.year, now.month, now.day).to_hijri()
        year = str(int(um.year)).zfill(4)
        month = str(int(um.month)).zfill(2)
        day = str(int(um.day)).zfill(2)
        hijri_str = "%s/%s/%s" % (year, month, day)
        return hijri_str

    def _get_report_base_filename(self):
        return self.name

class Partner(models.Model):
    _inherit = 'res.partner'

    is_freelancer = fields.Boolean(string='Is Freelancer', readonly=True, store=True)