# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from odoo.tools.translate import _


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.model
    def default_get(self, fields):
        """ Allow support of active_id / active_model instead of jut default_lead_id
        to ease window action definitions, and be backward compatible. """
        result = super(Lead2OpportunityPartner, self).default_get(fields)
        if result.get('lead_id'):
            lead_id = self.env['crm.lead'].browse(int(result.get('lead_id')))
            if lead_id.for_aahd:
                result['lead_source'] = 'for_aahd'
            if lead_id.for_bd:
                result['lead_source'] = 'for_bd'
        return result

    lead_source = fields.Selection([('for_aahd', 'To Aahd Pipeline'),
                                    ('for_bd', 'To Thiqah Pipeline')], 'Lead Type')
    aahd_opportunity_channel_id = fields.Many2one(
        'opportunity.channels', string='Opportunity Channel')
    bd_opportunity_channel_id = fields.Many2one(
        'opportunity.channels', string='Opportunity Channel')

    @api.constrains('lead_source')
    def _check_acces_to_choose_lead_source(self):
        if self.lead_source == 'for_aahd' and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_team_grp') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp')):
            raise UserError(_("You Don't have access to choose this option"))

        if self.lead_source == 'for_bd' and not (self.env.user.has_group('thiqah_crm.group_thiqah_bd_team_members') or self.env.user.has_group('thiqah_crm.sp_link_crm_group')):
            raise UserError(_("You Don't have access to choose this option"))

    def action_apply(self):
        group_to_notify = None
        if not self.lead_source:
            raise ValidationError(_('Please select lead type!'))
        if self.lead_source == 'for_aahd':
            opportunity_channel_id = self.aahd_opportunity_channel_id.id if self.aahd_opportunity_channel_id.id else False
            self = self.with_context(default_for_bd=False, default_for_aahd=True,
                                     form_view_ref='thiqah_crm.thiqah_aahd_crm_lead_view_form', default_opportunity_channel_id=opportunity_channel_id)
            group_to_notify = 'thiqah_crm.group_thiqah_aahd_sales_team_grp'

        if self.lead_source == 'for_bd':
            opportunity_channel_id = self.bd_opportunity_channel_id.id if self.bd_opportunity_channel_id.id else False

            self = self.with_context(default_for_bd=True, default_for_aahd=False,
                                     form_view_ref='thiqah_crm.thiqah_bd_crm_lead_view_form', default_opportunity_channel_id=opportunity_channel_id)
            group_to_notify = 'thiqah_crm.group_thiqah_bd_team_members'

        if self.name == 'merge':
            result_opportunity = self._action_merge()
        else:
            result_opportunity = self._action_convert()

        context = dict(self.env.context)
        active_id = context['active_id'] if 'active_id' in context else False

        # concerned_user = []
        # if not self.env['crm.lead'].sudo().search([
        #     ('id', '=', int(active_id))
        # ]).partner_id:

        # notify any user has the group_to_notify , --see above.
        if group_to_notify:
            template_id = self.env.ref(
                'thiqah_mail_templates.template_mail_notification_aahd_bd_id')
            # TODO: Need A Mixin to organize this process.
            for user_ in self.env['res.users'].sudo().search([]):
                if user_.has_group(group_to_notify):
                    template_id.send_mail(int(active_id), force_send=True, email_values={
                        'email_to': user_.email})

        return result_opportunity.redirect_lead_opportunity_view()
