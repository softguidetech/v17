# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from imaplib import IMAP4, IMAP4_SSL
from poplib import POP3, POP3_SSL

from odoo import _, api, fields, models
from odoo.exceptions import UserError


MAIL_TIMEOUT = 60
MAX_POP_MESSAGES = 50
_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    """Add the Outlook OAuth authentication on the incoming mail servers."""

    _name = 'fetchmail.server'
    _inherit = ['fetchmail.server', 'microsoft.outlook.mixin']

    _OUTLOOK_SCOPE = 'https://outlook.office.com/IMAP.AccessAsUser.All'

    server_type = fields.Selection(selection_add=[('outlook', 'Outlook OAuth Authentication')], ondelete={'outlook': 'set default'})

    def _compute_server_type_info(self):
        outlook_servers = self.filtered(lambda server: server.server_type == 'outlook')
        outlook_servers.server_type_info = _(
            'Connect your personal Outlook account using OAuth. \n'
            'You will be redirected to the Outlook login page to accept '
            'the permissions.')
        super(FetchmailServer, self - outlook_servers)._compute_server_type_info()

    @api.depends('server_type')
    def _compute_is_microsoft_outlook_configured(self):
        outlook_servers = self.filtered(lambda server: server.server_type == 'outlook')
        (self - outlook_servers).is_microsoft_outlook_configured = False
        super(FetchmailServer, outlook_servers)._compute_is_microsoft_outlook_configured()

    @api.constrains('server_type', 'is_ssl')
    def _check_use_microsoft_outlook_service(self):
        for server in self:
            if server.server_type == 'outlook' and not server.is_ssl:
                raise UserError(_('SSL is required for the server %r.', server.name))

    @api.onchange('server_type')
    def onchange_server_type(self):
        """Set the default configuration for a IMAP Outlook server."""
        if self.server_type == 'outlook':
            self.server = 'imap.outlook.com'
            self.is_ssl = True
            self.port = 993
        else:
            self.microsoft_outlook_refresh_token = False
            self.microsoft_outlook_access_token = False
            self.microsoft_outlook_access_token_expiration = False
            super(FetchmailServer, self).onchange_server_type()

    def _imap_login(self, connection):
        """Authenticate the IMAP connection.

        If the mail server is Outlook, we use the OAuth2 authentication protocol.
        """
        self.ensure_one()
        if self.server_type == 'outlook':
            auth_string = self._generate_outlook_oauth2_string(self.user)
            connection.authenticate('XOAUTH2', lambda x: auth_string)
            connection.select('INBOX')
        else:
            super()._imap_login(connection)

    def _get_connection_type(self):
        """Return which connection must be used for this mail server (IMAP or POP).
        The Outlook mail server used an IMAP connection.
        """
        self.ensure_one()
        if self.server_type == 'outlook':
            return 'imap'
        return self.server_type

    def connect(self, allow_archived=False):
        """
        :param bool allow_archived: by default (False), an exception is raised when calling this method on an
           archived record. It can be set to True for testing so that the exception is no longer raised.
        """
        self.ensure_one()
        if not allow_archived and not self.active:
            raise UserError(_('The server "%s" cannot be used because it is archived.', self.display_name))
        connection_type = self._get_connection_type()
        if connection_type == 'imap':
            if self.is_ssl:
                connection = IMAP4_SSL(self.server, int(self.port))
            else:
                connection = IMAP4(self.server, int(self.port))
            self._imap_login(connection)
        elif connection_type == 'pop':
            if self.is_ssl:
                connection = POP3_SSL(self.server, int(self.port), timeout=MAIL_TIMEOUT)
            else:
                connection = POP3(self.server, int(self.port), timeout=MAIL_TIMEOUT)
            #TODO: use this to remove only unread messages
            #connection.user("recent:"+server.user)
            connection.user(self.user)
            connection.pass_(self.password)
        return connection
    
    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.server_type, server.name)
            additionnal_context['default_fetchmail_server_id'] = server.id
            count, failed = 0, 0
            imap_server = None
            pop_server = None
            connection_type = server._get_connection_type()
            if connection_type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, data[0][1], save_original=server.original, strip_attachments=(not server.attach))
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                            failed += 1
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.server_type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        try:
                            imap_server.close()
                            imap_server.logout()
                        except OSError:
                            _logger.warning('Failed to properly finish imap connection: %s.', server.name, exc_info=True)
            elif connection_type == 'pop':
                try:
                    while True:
                        failed_in_loop = 0
                        num = 0
                        pop_server = server.connect()
                        (num_messages, total_size) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, num_messages) + 1):
                            (header, messages, octets) = pop_server.retr(num)
                            message = (b'\n').join(messages)
                            res_id = None
                            try:
                                res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, message, save_original=server.original, strip_attachments=(not server.attach))
                                pop_server.dele(num)
                            except Exception:
                                _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                                failed += 1
                                failed_in_loop += 1
                            self.env.cr.commit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", num, server.server_type, server.name, (num - failed_in_loop), failed_in_loop)
                        # Stop if (1) no more message left or (2) all messages have failed
                        if num_messages < MAX_POP_MESSAGES or failed_in_loop == num:
                            break
                        pop_server.quit()
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if pop_server:
                        try:
                            pop_server.quit()
                        except OSError:
                            _logger.warning('Failed to properly finish pop connection: %s.', server.name, exc_info=True)
            server.write({'date': fields.Datetime.now()})
        return True
    
    @api.model
    def _fetch_mails(self):
        """ Method called by cron to fetch mails from servers """
        return self.search([('state', '=', 'done'), ('server_type', '!=', 'local')]).fetch_mail()