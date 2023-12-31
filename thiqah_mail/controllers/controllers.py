# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper,PortalChatter
from odoo.http import request, route


class PortalChatterInherit(PortalChatter):

    @http.route(['/mail/chatter_post'], type='json', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, attachment_ids=None, attachment_tokens=None, **kw):
        """Create a new `mail.message` with the given `message` and/or `attachment_ids` and return new message values.

        The message will be associated to the record `res_id` of the model
        `res_model`. The user must have access rights on this target document or
        must provide valid identifiers through `kw`. See `_message_post_helper`.
        """
        res_id = int(res_id)

        self._portal_post_check_attachments(attachment_ids, attachment_tokens)

        if message or attachment_ids:
            result = {'default_message': message}
            # message is received in plaintext and saved in html
            # if message:
            #     message = plaintext2html(message)

            post_values = {
                'res_model': res_model,
                'res_id': res_id,
                'message': message,
                'send_after_commit': False,
                'attachment_ids': False,  # will be added afterward
            }
            post_values.update((fname, kw.get(fname)) for fname in self._portal_post_filter_params())
            message = _message_post_helper(**post_values)
            result.update({'default_message_id': message.id})

            if attachment_ids:
                # sudo write the attachment to bypass the read access
                # verification in mail message
                record = request.env[res_model].browse(res_id)
                message_values = {'res_id': res_id, 'model': res_model}
                attachments = record._message_post_process_attachments([], attachment_ids, message_values)

                if attachments.get('attachment_ids'):
                    message.sudo().write(attachments)

                result.update({'default_attachment_ids': message.attachment_ids.sudo().read(['id', 'name', 'mimetype', 'file_size', 'access_token'])})
            return result