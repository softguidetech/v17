from odoo import models, fields

class OracleConfig(models.Model):
    _name = 'oracle.config'

    name = fields.Char(string='Name')
    user_name = fields.Char(string='User Name', required=True)
    password = fields.Char(string='password', required=True)
    url = fields.Char(string='URL', required=True)
    list_banks_endpoint = fields.Char(string='List Banks Endpoint', required=True)
    freelance_endpoint = fields.Char(string='Freelance Endpoint', required=True)
    create_banks_endpoint = fields.Char(string='Create Freelnace Banks Endpoint', required=True)
    create_invoice_endpoint = fields.Char(string='Create Freelance Invoice Endpoint', required=True)
    validate_invoice_endpoint = fields.Char(string='Validate Invoice Endpoint', required=True)
    create_supplier_endpoint = fields.Char(string='Create Supplier Endpoint', required=True)
    create_supplier_bank_endpoint = fields.Char(string='Create Supplier Bank Endpoint', required=True)
    create_supplier_invoice_endpoint = fields.Char(string='Create Supplier Invoice Endpoint', required=True)
    update_supplier_endpoint = fields.Char(string='Update Supplier Endpoint', required=True)
