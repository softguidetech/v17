# -*- coding: utf-8 -*-

"""This model delegate the draft requests generated from the incomming mails"""


from odoo import models, fields


class DraftRequest(models.Model):
    _name = 'thiqah.portal.draft.request'
    _description = 'Thiqah Draft Request'

    partner_to = fields.Char('To')
    partner_from = fields.Char('From')
    assign_to = fields.Char('Assing To')
    assign_number = fields.Char('Assign To Number')
    date = fields.Date('Request Date')
    subject = fields.Char('Subject')

    message_id = fields.Many2one(
        'mail.message'
    )
