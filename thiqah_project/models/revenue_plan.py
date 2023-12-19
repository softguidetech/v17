# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class RevenuePlan(models.Model):
    _name = 'thiqah.revenue.plan'
    _description = 'Thiqah Revenue Plan'

    invoice_number = fields.Char()
    # sequence = fields.Char(string='Invoice Number', required=True,
    #                        readonly=True, default=lambda self: _('New'))

    invoice_date = fields.Date('Invoice Date')
    payment_date = fields.Date('Payment Date')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref(
        'base.main_company').currency_id)

    amount_billed = fields.Monetary(
        'Amount Billed', currency_field='currency_id')

    amount_received = fields.Monetary(
        'Amount Received', currency_field='currency_id')

    amount_due = fields.Monetary('Amount Due', currency_field='currency_id')

    status = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ])

    # Relation
    project_id = fields.Many2one('project.project',readonly=True)

    # @api.model
    # def create(self, vals):
    #     """
    #     override the create method to add sequence processing.
    #     """
    #     if vals.get('sequence', _('New')) == _('New'):
    #         vals['sequence'] = self.env['ir.sequence'].next_by_code(
    #             'thiqah_revenue_plan') or _('New')
    #     res = super(RevenuePlan, self).create(vals)
    #     return res
