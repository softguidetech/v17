# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

_content_selection = [('from_etmd', 'For ETMD'),
                      ('from_client_direct',
                       'For Client Directly'),
                      ('for_two', 'For Two'),
                      ('no_value', 'No Value')
                      ]


class Stage(models.Model):
    _inherit = "crm.stage"

    @api.depends('for_aahd', 'from_etmd', 'from_client_direct')
    def _compute_opp_source(self):
        for rec in self:
            if rec.for_aahd and rec.from_etmd and not rec.from_client_direct:
                rec.opp_source = 'from_etmd'
            elif rec.for_aahd and rec.from_client_direct and not rec.from_etmd:
                rec.opp_source = 'from_client_direct'
            elif rec.for_aahd and rec.from_client_direct and rec.from_etmd:
                rec.opp_source = 'for_two'
            elif rec.for_aahd and not rec.from_client_direct and not rec.from_etmd:
                rec.opp_source = 'no_value'
            else:
                rec.opp_source = 'no_value'

    # @api.depends('for_bd', 'generic_bd', 'regional_expansion')
    # def _compute_bg_stages(self):
    #     for rec in self:
    #         if rec.for_bd and rec.generic_bd and not rec.regional_expansion:
    #             rec.bd_stages = 'generic_bd'
    #         elif rec.for_bd and rec.regional_expansion and not rec.generic_bd:
    #             rec.bd_stages = 'regional_expansion'
    #         elif rec.for_bd and rec.regional_expansion and rec.generic_bd:
    #             rec.bd_stages = 'for_two'
    #         elif rec.for_bd and not rec.regional_expansion and not rec.generic_bd:
    #             rec.bd_stages = 'no_value'
    #         else:
    #             rec.bd_stages = 'no_value'

    @api.depends('for_bd', 'from_etmd_bd', 'from_client_direct_bd')
    def _compute_bg_stages(self):
        for rec in self:
            if rec.for_bd and rec.from_etmd_bd and not rec.from_client_direct_bd:
                rec.bd_stages = 'from_etmd'
            elif rec.for_bd and rec.from_client_direct_bd and not rec.from_etmd_bd:
                rec.bd_stages = 'from_client_direct'
            elif rec.for_bd and rec.from_client_direct_bd and rec.from_etmd_bd:
                rec.bd_stages = 'for_two'
            elif rec.for_bd and not rec.from_client_direct_bd and not rec.from_etmd_bd:
                rec.bd_stages = 'no_value'
            else:
                rec.bd_stages = 'no_value'

    for_aahd = fields.Boolean('For Aahd', default=False)

    from_etmd = fields.Boolean('From ETMD', default=False)

    from_client_direct = fields.Boolean('From Client Directly', default=False)

    opp_source = fields.Selection(_content_selection, compute="_compute_opp_source",
                                  string='Opp Source', store=True)

    is_proposal = fields.Boolean(string='For Proposal', default=False)

    is_brochure_evaluation = fields.Boolean(
        'For Brochure Evaluation', default=False)

    is_overdue = fields.Boolean('For Overdue Stage', default=False)

    for_bd = fields.Boolean('For Business Development', default=False)
    is_submitted = fields.Boolean('For Submitted Stage', default=False)

    # is_cancelled = fields.Boolean('For Cancelled Stage', default=False)

    # generic_bd = fields.Boolean('Generic BD Stages', default=False)

    # regional_expansion = fields.Boolean(
    #     'Regional expansion Stages', default=False)

    # Extension
    is_invisible_wathiq = fields.Boolean('Invisible For Wathiq',default=False)

    from_etmd_bd = fields.Boolean('From ETMD', default=False)

    from_client_direct_bd = fields.Boolean(
        'From Client Directly', default=False)

    is_proposal_bd = fields.Boolean(string='For Proposal', default=False)

    is_brochure_evaluation_bd = fields.Boolean(
        'For Brochure Evaluation', default=False)

    is_overdue_bd = fields.Boolean('For Overdue Stage', default=False)

    bd_stages = fields.Selection(
        _content_selection, compute="_compute_bg_stages", string='BD Stages', store=True)

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(
                _("You don't have access to create new stage, please contact your administrator"))
        return super(Stage, self).create(vals)

    def write(self, vals):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(
                _("You don't have access to create new stage, please contact your administrator"))
        return super(Stage, self).write(vals)
