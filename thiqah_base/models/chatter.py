# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.returns('mail.thread', lambda value: value.id)
    def message_post(self, **kwargs):
      
        if 'body' in kwargs: 
            link = ""
            new_body = ""
            is_link = False
            for word in kwargs['body'].split():
                if word == "<a" or is_link:
                    is_link = True
                    link = link+" "+word
                    if "</a>" in word:

                        is_link = False
                        if "data-oe-id" in link:
                            new_body = new_body + " " + link
                            link = ""
                else:
                    word = re.sub('[^A-Za-z\u0621-\u064A\u0660-\u06690-9]+', ' ', word)
                    new_body = new_body+" "+word
            kwargs['body'] = '<p>'+new_body+'</p>'

        return super(MailThread, self).message_post(**kwargs)
