# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

 
class MailThread(models.AbstractModel):
    _inherit = "mail.thread"
    
    def _message_compute_author(self, author_id=None, email_from=None, raise_exception=True):
        """ Tool method computing author information for messages. Purpose is
        to ensure maximum coherence between author / current user / email_from
        when sending emails. """
        author_id, email_from = super()._message_compute_author(author_id,email_from,raise_exception)
        smtp_server = self.env['ir.mail_server'].sudo().search([('active','=',True)], limit=1)
        email_from = "%s <%s>" %(self.env.user.company_id.name,smtp_server.smtp_user)
        email_from=email_from
        return author_id, email_from
    
    
    
    
    # ------------------------------------------------------
    # MESSAGE READ / FETCH / FAILURE API
    # ------------------------------------------------------
    def _notify_compute_recipients(self, message, msg_vals):
        """ Compute recipients to notify based on subtype and followers. This
        method returns data structured as expected for ``_notify_recipients``. """
        msg_sudo = message.sudo()
        # get values from msg_vals or from message if msg_vals doen't exists
        pids = msg_vals.get('partner_ids', []) if msg_vals else msg_sudo.partner_ids.ids
        message_type = msg_vals.get('message_type') if msg_vals else msg_sudo.message_type
        subtype_id = msg_vals.get('subtype_id') if msg_vals else msg_sudo.subtype_id.id
        # is it possible to have record but no subtype_id ?
        recipients_data = []
        res = self.env['mail.followers']._get_recipient_data(self, message_type, subtype_id, pids)
        if not res:
            return recipients_data

        author_id = msg_vals.get('author_id') or message.author_id.id
        for pid, active, pshare, notif, groups in res:
            if pid and pid == author_id and not self.env.context.get('mail_notify_author'):  # do not notify the author of its own messages
                continue
#             if pid and msg_sudo.partner_ids.ids and pid not in msg_sudo.partner_ids.ids:# and not self.env.context.get('mail_notify_author'):  # do not notify the author of its own messages
#                 continue
            if pid:
                if active is False:
                    continue
                pdata = {'id': pid, 'active': active, 'share': pshare, 'groups': groups or []}
                if msg_sudo.partner_ids.ids and pid not in msg_sudo.partner_ids.ids: 
                    continue
                if notif == 'inbox':
                    recipients_data.append(dict(pdata, notif=notif, type='user'))
                elif not pshare and notif:  # has an user and is not shared, is therefore user
                    recipients_data.append(dict(pdata, notif=notif, type='user'))
                elif pshare and notif:  # has an user but is shared, is therefore portal
                    recipients_data.append(dict(pdata, notif=notif, type='portal'))
                else:  # has no user, is therefore customer
                    recipients_data.append(dict(pdata, notif=notif if notif else 'email', type='customer'))
        return recipients_data
#