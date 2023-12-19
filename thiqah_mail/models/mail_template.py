# -*- coding: utf-8 -*-

from odoo import models, api
from xmlrpc import client as xmlrpclib
import email
import logging

_logger = logging.getLogger(__name__)


class MailTemplateInherit(models.AbstractModel):
    _inherit = 'mail.template'
    _description = 'Thiqah Mail Template Inherit'

    # def write(self, vals):
    #     thqiah_notification_template_id = self.env.ref(
    #         'thiqah_mail_templates.to_do_service_request').sudo().id
    #     if self.id == thqiah_notification_template_id:
    #         return False
    #     return super().write(vals)
