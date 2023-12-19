# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class ThiqahCrmTag(models.Model):
    _name = 'thiqah.crm.tag'
    _inherit = 'crm.tag'


class CrmTagInherit(models.Model):
    _inherit = 'crm.tag'

    @api.model_create_multi
    def create(self, vals_list):
        if not self._name == 'thiqah.crm.tag':
            if vals_list[0]['name'].lower() in ('new', 'need for action'):
                raise UserError(_('This name is reserved.'))
        return super(CrmTagInherit, self).create(vals_list)
