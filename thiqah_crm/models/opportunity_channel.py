# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
import logging
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

_content_selection = [('from_etmd', 'From ETMD'),
                      ('from_client_direct',
                       'From Client Directly'),
                      ]


class OpportunityChannel(models.Model):
    _name = "opportunity.channels"
    _description = 'Opportunity Channels'

    name = fields.Char(translate=True)
    for_aahd = fields.Boolean('For Aahd', default=False)
    for_bd = fields.Boolean('For Business Development', default=False)

    opp_source = fields.Selection(
        _content_selection, string='Opp Source', default='from_etmd')

    # bd_stages = fields.Selection([('generic_bd', 'Generic BD Stages'),
    #                               ('regional_expansion',
    #                                'Regional expansion Stages')
    #                               ], string='BD Stages', default='generic_bd')

    # Extension
    bd_stages = fields.Selection(
        _content_selection, string='BD Stages', default='from_etmd')
