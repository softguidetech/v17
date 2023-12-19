import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FreelanceWorkorder(models.Model):
    _name = 'freelance.workorder'
    _rec_name = 'sequence'
    _description = 'Freelancer Workorder'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string='Sequence', default=_('New'),copy=False)
    state = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'), ('paid', 'Paid')], string='State', default='draft')
    freelancer_id = fields.Many2one(comodel_name='freelance.application', string='Freelancer')
    frequest_id = fields.Many2one(comodel_name='freelance.request', string='Freelance Request')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    due_date = fields.Date(string='Due Date')
    amount = fields.Float(string='Amount', tracking=True, digits=(12,2))
    description = fields.Text(string='Description')
    justification = fields.Text(string='Amount Adjust Justification')
    duration = fields.Integer(string='Duration')
    entity_code = fields.Char(related='frequest_id.entity_code')

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code(self._name) or 'New'
        return super(FreelanceWorkorder, self).create(vals)

    def action_confirmed(self):
        for rec in self:
            if rec.state == "draft":
                rec.state = "confirmed"

    def action_paid(self):
        for rec in self:
            if rec.state == "confirmed":
                rec.state = "paid"