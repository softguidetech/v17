# -*- coding: utf-8 -*-
###############################################################################
#
#    ATIT.
#    Copyright (C) 2020-TODAY ATIT.
#
###############################################################################
from odoo import models
import logging

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
                    attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
                    body_alternative=None, subtype_alternative='plain'):
        """ If use_smtp_account setting is checked, change the email_from value
            to the account email in the highest priority smtp server
        """
        # get highest priority SMTP server to use
        smtp_server = self.sudo().search([('active','=',True)], limit=1)
        reply_to = email_from
        email_from = "%s <%s>" %(self.env.user.company_id.name,smtp_server.smtp_user)
        _logger.info(f"use_smtp_account is active: email used {email_from}")
        return super(IrMailServer, self).build_email(email_from, email_to, subject, body, email_cc=email_cc, email_bcc=email_bcc, reply_to=reply_to,
                attachments=attachments, message_id=message_id, references=references, object_id=object_id, subtype=subtype, headers=headers,
                body_alternative=body_alternative, subtype_alternative=subtype_alternative)
