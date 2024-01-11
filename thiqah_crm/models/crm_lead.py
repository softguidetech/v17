# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.tools.translate import _
from datetime import date, datetime, timedelta
from odoo import api, fields, models
from odoo.exceptions import AccessDenied, UserError, ValidationError
import json
from odoo.osv.expression import AND
from lxml import etree

today = datetime.today()
_logger = logging.getLogger(__name__)

aahd_source_content = [
    ('rfp', 'RFP'),
    ('digital_solution', 'Digital Solution'),
    ('rfi_rfq_preq', 'RFI/RFQ/PreQ'),
    ('change_request', 'Change Request'),
]

MESSAGE_IS_WATHIQ_ERROR = 'There is no product named wathiq.Please verify your configuration in the services section.'


class LeadLost(models.TransientModel):
    _inherit = "crm.lead.lost"
    
    lost_proposal_amount = fields.Float()

class Lead(models.Model):
    _inherit = "crm.lead"

    development_of_location = fields.Many2one('res.country', string="Country", default=lambda self: self.env.ref('base.sa'))
    is_ict = fields.Boolean(default=False,string="IS ICT")
    ict = fields.Many2one('crm.lead.ict')
    ict_services = fields.Many2one('crm.lead.ict_services')
    ict_services_info = fields.Many2one('crm.lead.ict_services_info')
    sectors_of_interest = fields.Many2many('crm.lead.sectors_of_interest') 
    types_of_services_provided = fields.Many2many('crm.lead.types_of_services_provided') 
    services_for = fields.Selection(selection=[('private', 'Private'), ('se_gov', 'Semi Government'), ('gov', 'Government'), ],defualt="gov", string='Services For')
    aligned_with_market_startegy = fields.Selection(selection=[('5', 'Highly Likely'),('4', 'Likely'),('3', 'Neutral'),('2', ' Unlikely'),('1', 'Highly Unlikely'), ],defualt="5", string='The lead interests are aligned with Thiqah’s go to market strategy ')
    potential_sectorial_interests = fields.Selection(selection=[('5', 'Highly Likely'),('4', 'Likely'),('3', 'Neutral'),('2', ' Unlikely'),('1', 'Highly Unlikely'), ],defualt="5", string='The lead has a potential with Thiqah’s sectorial interests – Specify Sectors ')
    serves_strategy_initiatives = fields.Selection(selection=[('5', 'Highly Likely'),('4', 'Likely'),('3', 'Neutral'),('2', ' Unlikely'),('1', 'Highly Unlikely'), ],defualt="5", string='The lead directly serves Thiqah’s strategy, or initiatives, or themes – Specify if any')
    involves_addressing_market_needs = fields.Selection(selection=[('5', 'Highly Likely'),('4', 'Likely'),('3', 'Neutral'),('2', ' Unlikely'),('1', 'Highly Unlikely'), ],defualt="5", string='Leads work involves addressing the market needs and gaps')
    total_score_compute = fields.Integer (compute="compute_final_total_score_max")
    passing_score_lead_evaluation = fields.Integer(default=lambda self: self.compute_score_max() , readonly=False, max=20 )
    passed_score = fields.Boolean(default=False)
    select_all_apply = fields.Selection([('regulatory_tech', 'Regulatory Technology Offering'),('smart_solution', 'Smart Solution Offering')],string="")
    product_name = fields.Char(string='Product Name')
    sectors = fields.Char(string='Specify Sectors')
    init_themes = fields.Char(string='Specify Initiative/Themes')
    stage_domain_ids = fields.Many2many('crm.stage', string='CRM Domain', compute="_compute_domain_stage")
    business_case_attachment = fields.Binary(string="Business Case Attachment", attachment=True)
    
    @api.constrains('profit_margin')
    def _check_values(self):
        if self.profit_margin < 1:
            raise Warning(_('Values should not be zero.'))            

    def compute_score_max(self):
        for rec in self:
            params = self.env['ir.config_parameter'].sudo()
            saved_score = int(params.get_param('thiqah_crm.passing_score_lead_evaluation'))
            rec.passing_score_lead_evaluation = saved_score
    
    @api.depends('involves_addressing_market_needs',  'serves_strategy_initiatives', 'potential_sectorial_interests', 'aligned_with_market_startegy')
    def compute_final_total_score_max(self):
        params = self.env['ir.config_parameter'].sudo()
        saved_score = int(params.get_param('thiqah_crm.passing_score_lead_evaluation'))
        for rec in self :
            rec.passing_score_lead_evaluation = saved_score
            s1 = 0
            s2 = 0
            s3 = 0
            s4 = 0
            if rec.aligned_with_market_startegy:
                s1 = int(rec.aligned_with_market_startegy)
            if rec.potential_sectorial_interests:
                s2 = int(rec.potential_sectorial_interests)
            if rec.serves_strategy_initiatives:    
                s3 = int(rec.serves_strategy_initiatives)
            if  rec.involves_addressing_market_needs :   
                s4 = int(rec.involves_addressing_market_needs)
            rec.total_score_compute = 0
            rec.total_score_compute = (s1 + s2 + s3 + s4)
        
    @api.onchange('ict')
    def _onchange_ict(self):
        domain = []
        self.ict_services = False
        if self.ict:
            domain = [('parent_ict', '=', self.ict.id)]
        return {'domain': {'ict_services': domain}}
    
    @api.onchange('ict_services')
    def _onchange_ict_services(self):
        domain = []
        self.ict_services_info = False
        if self.ict_services:
            domain = [('parent_ict_services', '=', self.ict_services.id)]
        return {'domain': {'ict_services_info': domain}}

    @api.model
    def check_is_brochure_evaluation_stage(self, recordId):
        rec = self.browse(recordId)
        if rec.stage_id.is_won:
            if self.env.user.has_group('thiqah_crm.group_thiqah_aahd_vb_grp'):
                return False
            return True
        if ((self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_manager') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_member_grp')) and rec.stage_id.is_brochure_evaluation):
            return False
        elif ((self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_manager') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_member_grp'))
              and not rec.stage_id.is_brochure_evaluation and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_team_grp') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp'))):
            return True
        else:
            return False

    # From overdue return to first stage
    def set_to_first_stage(self):
        stages = self.get_domain_stages(
            self.for_aahd, self.for_bd, self.opportunity_channel_id)
        if stages:
            self.write({'stage_id': stages[0].id})

    # Get filtred stages for aahd or bd
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages_ids = super()._read_group_stage_ids(stages, domain, order)
        ctx = self.env.context

        if 'default_for_aahd' in ctx and ctx['default_for_aahd'] == True:
            stages_ids = stages_ids.filtered(
                lambda stage: stage.for_aahd == True)

        if 'default_for_bd' in ctx and ctx['default_for_bd'] == True:
            stages_ids = stages_ids.filtered(
                lambda stage: stage.for_bd == True)

        return stages_ids

    # For Lead pipline ###################### ###################### ######################
    thiqah_lead_stage_id = fields.Many2one(
        'thiqah.crm.stage', string='Stage', index=True, tracking=True,
        compute='_compute_thiqah_stage_id', readonly=False, store=True,
        copy=False, group_expand='_read_group_lead_stage_ids', ondelete='restrict',
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")

    def _thiqah_stage_find(self, team_id=False, domain=None, order='sequence', limit=1):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :param order : base search order for stage
            :param limit : base search limit for stage
            :returns crm.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for lead in self:
            if lead.team_id:
                team_ids.add(lead.team_id.id)

        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_id', '=', False),
                             ('team_id', 'in', list(team_ids))]
        else:
            search_domain = [('team_id', '=', False)]

        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        stages = self.env['thiqah.crm.stage'].search(
            search_domain, order=order, limit=limit)
        return stages

    @api.depends('team_id', 'type')
    def _compute_thiqah_stage_id(self):
        for lead in self:
            if not lead.thiqah_lead_stage_id:
                lead.thiqah_lead_stage_id = lead._thiqah_stage_find(
                    domain=[('fold', '=', False)]).id

    @api.model
    def _read_group_lead_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|',
                             ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids),
                             ('team_id', '=', False)]

        # perform search
        # stage_ids = stages._search(
        #     search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return self.env['thiqah.crm.stage'].search([])

    is_idea = fields.Boolean(default=False)
    is_qualification_stage = fields.Boolean(related='thiqah_lead_stage_id.is_qualification')

    # is_readonly_grouped_by = fields.Boolean(
    #     compute='set_grouped_by_readonly', store=True)

    first_name = fields.Char()
    last_name = fields.Char()
    organization = fields.Char()

    idea_name = fields.Char()
    problem = fields.Text()
    solution = fields.Text()

    # def set_grouped_by_readonly(self):
    #     """
    #     _setState() from kanban_render.js
    #     Deactivate the drag'n'drop either:
    #     - if the groupedBy field is readonly (on the field attrs or in the view) ***** This one ******
    #     - if the groupedBy field is of type many2many
    #     - for date and datetime if :
    #         - allowGroupRangeValue is not true
    #     """
    #     for lead in self:
    #         lead.is_readonly_grouped_by = True if not self.env.user.has_group(
    #             'thiqah_crm.sp_team_group') else False

    is_likned_to_event = fields.Boolean(
        related='source_lead_id.event_as_source')

    def _set_readonly_field(self, document, field_name, is_readonly, res):
        """."""
        for node in document.xpath("//field[@name='"+field_name+"']"):
            node.set("readonly", "1")
            modifiers = json.loads(node.get("modifiers"))
            modifiers['readonly'] = is_readonly
            node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(document)
        return res

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # Monkey Patch
        # OVERRIDE to add the 'thiqah_lead_stage_id' field dynamically inside the view depending of the permissions.
        # instantiate this etree.XML() in case of need.
        res = super().fields_view_get(view_id=view_id,
                                      view_type=view_type, toolbar=toolbar, submenu=submenu)

        if not self.env.user.has_group('thiqah_crm.sp_team_group'):
            if view_type == 'kanban':
                document = etree.XML(res['arch'])
                res = self._set_readonly_field(
                    document, 'thiqah_lead_stage_id', True, res)

        if view_type == 'form':
            is_from_event = dict(self.env.context).get(
                'default_from_event', False)

            # set source lead readonly when the previous node is the event action.
            document = etree.XML(res['arch'])
            if is_from_event:
                res = self._set_readonly_field(
                    document, 'source_lead_id', is_from_event, res)
            else:
                res = self._set_readonly_field(
                    document, 'source_lead_id', is_from_event, res)

        return res

    display_event_id = fields.Many2one('crm.lead.event', index=True)

    def get_thiqa_domain_stages(self):
        domain = [('fold', '=', False)]

        stages = self._thiqah_stage_find(
            domain=domain, limit=None, order='sequence asc')
        return stages

    def action_lead_next_stage(self):
        for lead in self:

            stages = lead.get_thiqa_domain_stages()
            _logger.info('stages: %s', stages)

            stages_sequences = [stage.sequence for stage in stages]

            stage_id = next(
                (stage for stage in stages if stage.sequence > lead.thiqah_lead_stage_id.sequence), None)

            _logger.info('stage from the lead: %s', stage_id)
            _logger.info('sequence stage from the lead: %s',
                         lead.thiqah_lead_stage_id.sequence)

            if stage_id:
                if stage_id.sequence in stages_sequences[1:-1]:
                    if not self.env.user.has_group('thiqah_crm.marketing_development_group'):
                        raise ValidationError(
                            _('This action is reserved for users with the marketing development group.'))

                if stage_id.is_qualification:
                    if not self.env.user.has_group('thiqah_crm.sp_team_group'):
                        raise ValidationError(
                            _('This action is reserved for users with the sp group.'))

                    # notify any user has the sp team group.
                    template_id = self.env.ref(
                        'thiqah_mail_templates.template_mail_notification_sp_team_id')

                    for user_ in self.env.ref('thiqah_crm.sp_team_group').users:
                        # inject the sp user concerned to adapt the rendering to the template.
                        mail = template_id.send_mail(lead.id, force_send=True, email_values={
                                'email_to': user_.email})
                        try:
                            lead.env['mail.mail'].sudo().browse(mail).write({'res_id': False})
                        except Exception:
                            pass
                lead.write({'thiqah_lead_stage_id': stage_id.id})

    sp_assing_to_id = fields.Many2one('res.users')

    def get_backend_url(self):
        for lead in self:
            return '/web#id=%s' % (lead.id) + '&cids=1&menu_id=165&action=236&model=crm.lead&view_type=form'

    ###################### ###################### ######################

    @api.depends('operational_costs', 'profit_margin')
    def compute_financial_offer_value(self):
        for rec in self:
            percent_profit_margin = 100-rec.profit_margin
            rec.financial_offer_value = rec.operational_costs / \
                (percent_profit_margin/100)

    # Recompute stage to get only etmd stages in case of opportunity channel is for etmd or directly client stages
    # Customization
    # TODO: Avoiding workflow reset to new after change the sales person

    @api.depends('team_id', 'type', 'opportunity_channel_id', 'opportunity_channel_id.opp_source', 'for_aahd', 'for_bd', 'opportunity_channel_id.bd_stages')
    def _compute_stage_id(self):
        for lead in self:
            ctx = self.env.context
            if ('default_opportunity_channel_id' in ctx and ctx['default_opportunity_channel_id']):
                opportunity_channel_id = ctx['default_opportunity_channel_id']
                self.env.cr.execute("update crm_lead set opportunity_channel_id=%s where id=%s" % (
                    opportunity_channel_id, lead.id))
                self.env.cr.commit()

            if ('default_for_aahd' in ctx and ctx['default_for_aahd'] == True) or lead.for_aahd:

                if lead.opportunity_channel_id.opp_source:
                    lead.stage_id = lead._stage_find(domain=[('fold', '=', False), ('for_aahd', '=', True), (
                        'opp_source', 'in', ('for_two', lead.opportunity_channel_id.opp_source))]).id
                else:
                    lead.stage_id = lead._stage_find(
                        domain=[('fold', '=', False), ('for_aahd', '=', True)]).id

            elif ('default_for_bd' in ctx and ctx['default_for_bd'] == True) or lead.for_bd:
                domain = [('fold', '=', False), ('for_bd', '=', True)]

                if lead.opportunity_channel_id.bd_stages:
                    domain += [('bd_stages', 'in', ('for_two',
                                lead.opportunity_channel_id.bd_stages))]

                lead.stage_id = lead._stage_find(domain=domain).id

            else:
                lead.stage_id = lead._stage_find(
                    domain=[('fold', '=', False)]).id

    @api.depends('work_area_value', 'budget_and_margin_value', 'duration_value',
                 'partner_value', 'project_risk_value', 'carrying_capacity_value')
    def compute_final_result(self):
        for rec in self:
            rec.final_result = rec.work_area_value+rec.budget_and_margin_value + rec.duration_value + \
                rec.partner_value + rec.project_risk_value + rec.carrying_capacity_value

    @api.constrains('work_area_value', 'budget_and_margin_value', 'duration_value',
                    'partner_value', 'project_risk_value', 'carrying_capacity_value', 'work_area_value_max', 'budget_and_margin_value_max', 'duration_value_max',
                    'partner_value_max', 'project_risk_value_max', 'carrying_capacity_value_max',)
    def check_max_values_creteria(self):
        rec = self
        if rec.work_area_value > rec.work_area_value_max:
            raise UserError(_('Check Work Area Value'))
        if rec.budget_and_margin_value > rec.budget_and_margin_value_max:
            raise UserError(_('Check Budget And Margin Value'))
        if rec.duration_value > rec.duration_value_max:
            raise UserError(_('Check Duration Value'))
        if rec.partner_value > rec.partner_value_max:
            raise UserError(_('Check Partner Value'))
        if rec.project_risk_value > rec.project_risk_value_max:
            raise UserError(_('Check Project Risk Value'))
        if rec.carrying_capacity_value > rec.carrying_capacity_value_max:
            raise UserError(_('Check Carrying Capacity Value'))
#         if rec.strategic_recommendations_value > rec.strategic_recommendations_value_max:
#             raise UserError(_('Check strategic Recommendations Value'))

    @api.depends('approval_request_id', 'stage_id', 'brochure_evaluation_status')
    def compute_visible_approval_request_user(self):
        for rec in self:
            rec.visible_approval_request = False
            if rec.approval_request_id:
                if self.env.user.has_group('approvals.group_approval_user') and self.env.user.id in rec.approval_request_id.approver_ids.mapped('user_id').ids and rec.brochure_evaluation_status == 'participation_decision':
                    rec.visible_approval_request = True

    def action_show_approval_request(self):
        self.ensure_one()
        return {
            'view_mode': 'form',
            'res_model': 'approval.request',
            'domain': [('id', '=', self.approval_request_id.id)],
            'res_id': self.approval_request_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'edit': False}
        }

    @api.depends('stage_id', 'opportunity_channel_id.opp_source', 'opportunity_channel_id', 'for_aahd', 'for_bd', 'opportunity_channel_id.bd_stages')
    def compute_visible_stage_user(self):
        for rec in self:
            rec.stage_visible = True
            stages = self.get_domain_stages(
                rec.for_aahd, rec.for_bd, rec.opportunity_channel_id)
            next_stage_id = next(
                (stage for stage in stages if stage.sequence > self.stage_id.sequence), None)
            if next_stage_id:

                # Nxt stage is Proposal
                if next_stage_id.is_proposal and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_proposal_member_grp') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp')):
                    rec.stage_visible = False

                # this stage is Proposal
                elif self.stage_id.is_proposal and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_proposal_member_grp')
                                                        or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_team_grp')
                                                        or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp')
                                                        or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_vb_grp')
                                                        ):
                    rec.stage_visible = False

                # Nxt stage is Evaluation for evaluation_member
                elif next_stage_id.is_brochure_evaluation and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_team_grp') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp') or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_vb_grp')):
                    rec.stage_visible = False

                # Actual stage is evaluation
                elif self.stage_id.is_brochure_evaluation and not self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_manager'):
                    rec.stage_visible = False
                # Actual stage is won/lost
                elif self.stage_id.is_won or self.active == False:
                    rec.stage_visible = False

                else:
                    rec.stage_visible = True
            else:
                rec.stage_visible = False

    def get_domain_opportunity_channel_id(self):
        ctx = self.env.context
        context = ctx.copy()
        domain = []
        if 'default_for_bd' in context and context['default_for_bd']:
            domain += [('for_bd', '=', True)]
        if 'default_for_aahd' in context and context['default_for_aahd']:
            domain += [('for_aahd', '=', True)]
        return domain

    for_aahd = fields.Boolean('For Aahd', default=False)
    for_bd = fields.Boolean('For Business Development', default=False)

    product_ids = fields.Many2many(
        'product.template', string='Services', domain="[('detailed_type','=','service')]")

    ############################
    # Tools And fields for Aahd Sales Dashboard.
    ############################

    product_for_filter_id = fields.Many2one(
        'product.template', string='Services(Aahd Sales Dahsboard)', domain="[('detailed_type','=','service'),('is_wathiq','=',False)]")

    product_is_wathiq = fields.Boolean(
        related='product_for_filter_id.is_wathiq', string='Is Wathiq')

    aahd_source_id = fields.Many2one(
        'thiqah.aahd.source', 'This Field is dedicated to aahd sales dashboard')

    date_open_won = fields.Datetime('Winning Date', store=True)

    aahd_source = fields.Selection(aahd_source_content, default='')

    is_digital_aahd = fields.Boolean(
        related='product_for_filter_id.is_digital_aahd', store=True, groups="thiqah_crm.group_thiqah_aahd_sales_manager_grp")

    is_non_digital_aahd = fields.Boolean(
        related='product_for_filter_id.is_non_digital_aahd', store=True, groups="thiqah_crm.group_thiqah_aahd_sales_manager_grp")

    is_opportunity_won = fields.Boolean(
        default=False, help='This computed field indicates if this lead is won or not.')

    opportunity_channel_id = fields.Many2one(
        'opportunity.channels', string='Opportunity Channel', domain=get_domain_opportunity_channel_id)

    client_status_id = fields.Many2one('client.status', string='Client Status')

    proposal_status = fields.Selection([
        ('draft', 'Pending'),
        ('under_development', 'Under development'),
        ('submitted', 'Submitted'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Proposal Status', default='draft', tracking=True)

    submission_status = fields.Selection([
        ('draft', 'Draft'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Submission Status', default='draft', tracking=True)

    # actions for submission_status
    def award_submission(self):
        for lead in self:
            lead.write({
                'submission_status': 'awarded'
            })

    def reject_submission(self):
        for lead in self:
            lead.write({
                'submission_status': 'rejected'
            })

    def cancel_submission(self):
        for lead in self:
            lead.write({
                'submission_status': 'cancelled'
            })

    # submission button
    def action_submission(self):
        """."""
        self.action_set_next_stage()

    brochure_evaluation_status = fields.Selection([('prepare_doc', 'Preparing the evaluation document'),
                                                   ('participation_decision',
                                                    'Participation decision'),
                                                   ('accepted', 'Accepted'),
                                                   ('rejected', 'Rejected'),
                                                   ], string='Brochure Evaluation Status', default='prepare_doc', tracking=True)

    # expected_revenue = fields.Monetary(
    #     string='Expected Revenue', currency_field='company_currency', tracking=True)
    won_revenue = fields.Monetary(
        string='Won Proposal Amount', currency_field='company_currency', tracking=True)
    stage_is_proposal = fields.Boolean(
        related='stage_id.is_proposal', store=True)
    stage_is_submitted = fields.Boolean(
        related='stage_id.is_submitted', store=True)
    stage_is_overdue = fields.Boolean(
        related='stage_id.is_overdue', store=True)
    stage_is_won = fields.Boolean(
        related='stage_id.is_won', store=True)
    stage_is_brochure_evaluation = fields.Boolean(
        related='stage_id.is_brochure_evaluation', store=True)
    stage_for_aahd = fields.Boolean(
        related='stage_id.for_aahd', store=True, string="Stage For Aahd")
    stage_for_bd = fields.Boolean(
        related='stage_id.for_bd', store=True, string="Stage For BD")
    stage_for_etmd = fields.Boolean(
        related='stage_id.from_etmd', store=True, string="Stage Opp Source")

    stage_client_direct = fields.Boolean(
        related='stage_id.from_client_direct', store=True, string="Stage Opp Source")

    stage_opp_source = fields.Selection(
        related='stage_id.opp_source', store=True)

    opportunity_channel_opp_source = fields.Selection(
        related='opportunity_channel_id.opp_source', store=True)

    opportunity_channel_bd_stages = fields.Selection(
        related='opportunity_channel_id.bd_stages', store=True)

    stage_is_overdue_bd = fields.Boolean(
        related='stage_id.is_overdue_bd', store=True)
    stage_is_proposal_bd = fields.Boolean(
        related='stage_id.is_proposal_bd', store=True)
    stage_is_brochure_evaluation_bd = fields.Boolean(
        related='stage_id.is_brochure_evaluation_bd', store=True)

    # add these fields(sector,deputy,chef) those are related to the customer
    category_portfolio_id = fields.Many2one(
        related="partner_id.category_portfolio_id", readonly=False)

    deputy_id = fields.Many2one(related="category_portfolio_id.deputy_id")

    chief_id = fields.Many2one(related="category_portfolio_id.chief_id")
    sp_manager_id = fields.Many2one(
        related="category_portfolio_id.sp_manager_id")

    is_wathiq = fields.Boolean(
        'Is Wathiq', default=False)

    # Extension : Modify the visibilty of the satge_id depending of the is_wathiq checkbox.
    stage_id_domain = fields.Char(
        compute="_compute_stage_id_domain",
        readonly=True,
        store=False,
    )

    def _get_previous_date(self, days):
        today = datetime.today()
        if days == 30:
            return today - timedelta(days=33)
        return today - timedelta(days=days)

    def _get_tag(self, days):
        if days == 3:
            return self.env.ref('thiqah_crm.thiqah_crm_tag_new')
        if days == 30:
            return self.env.ref('thiqah_crm.thiqah_crm_tag_need')

    def _prepare_tag_ids(self, tag_ids, reference_date, days):
        created_date_ = self.create_date
        # if days == 30:
        #     created_date_ = created_date_ + timedelta(days=3)
        if days == 3:
            if created_date_ >= reference_date:
                tag = self._get_tag(days)
                if tag:
                    tag_ids.append(tag.id)
            return tag_ids

        if days == 30:
            if created_date_ <= reference_date:
                tag = self._get_tag(days)
                if tag:
                    tag_ids.append(tag.id)
            return tag_ids

    # @api.depends('create_date')
    def _compute_thiqah_tag_ids(self):
        first_stage_id = self.env['crm.stage'].search(
            [('for_aahd', '=', True)], order='sequence', limit=1)
        reference_date = None
        for lead in self:
            tag_ids = []
            if lead.stage_id.id == first_stage_id.id:
                # For 'New' Label
                days = 3
                reference_date = lead._get_previous_date(days)
                tag_ids = lead._prepare_tag_ids(tag_ids, reference_date, days)

                if not tag_ids:
                    # if not self.env['thiqah.crm.tag'].search(
                    #     [
                    #         ('name', '=', tag_ids[0])
                    #     ]
                    # ) == 'New':
                    # For 'Need For Action' Label
                    days = 30
                    reference_date = lead._get_previous_date(days)
                    tag_ids = lead._prepare_tag_ids(
                        tag_ids, reference_date, days)

            # DO_ACTION
            # _logger.info('TAGs====>%s,%s,%s,%s ', tag_ids,
            #              lead.name, reference_date, lead.create_date)
            lead.thiqah_tag_ids = [(6, 0, tag_ids)]

    thiqah_tag_ids = fields.Many2many(
        'thiqah.crm.tag', 'thiqah_crm_tag_rel', 'lead_id', 'thiqah_tag_id', string='Tags',
        help="Classify and analyze your lead/opportunity categories like: Training, Service", compute='_compute_thiqah_tag_ids', readonly=True)

    #############################################
    # Outils for the legal team actions.
    #############################################

    need_legal_action = fields.Boolean(default=False)

    legal_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_legal', 'Waiting For Legal Approval'),
        ('need_contract', 'Need Contract'),
        ('no_need_contract', 'No Need Contract'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True)

    no_need_Contract = fields.Boolean(default=False)
    need_Contract = fields.Boolean(default=False)
    is_rejected = fields.Boolean(default=False)

    def need_legal_approval(self):
        """
        .
        """
        for rec in self:
            rec.write(
                {
                    'need_legal_action': True,
                    'legal_state': 'waiting_approval_legal'
                }
            )

    def need_contract(self):
        """"""
        for rec in self:
            rec.write(
                {
                    'legal_state': 'need_contract',
                    'need_Contract': True,
                    'no_need_Contract': False,
                    'is_rejected': False,
                }
            )

    def no_need_contract(self):
        """"""
        for rec in self:
            rec.write(
                {
                    'legal_state': 'no_need_contract',
                    'need_Contract': False,
                    'no_need_Contract': True,
                    'is_rejected': False,
                }
            )

    def reject(self):
        """"""
        for rec in self:
            rec.write(
                {
                    'legal_state': 'rejected',
                    'is_rejected': True,
                    'need_Contract': False,
                    'no_need_Contract': False
                }
            )

    project_ids = fields.One2many(
        'project.project', 'lead_id', string="Projects Generated")

    project_count = fields.Integer(compute='compute_project_count')

    def compute_project_count(self):
        for rec in self:
            rec.project_count = len(rec.project_ids)

    def action_link_project(self):
        """ Open Project Management view from the current opportunity supposed it's the origin of the project.
            :return dict: dictionary value for created Project view
        """
        self.ensure_one()  # Singleton
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'domain': [('lead_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # https://statisticsglobe.com/convert-timedelta-months-python
    def timedelta_in_months(self, end, start):
        # returning the calculation
        return 12 * (end.year - start.year) + (end.month - start.month)

    last_action_date = fields.Datetime(
        readonly=True, default=fields.Datetime.now())

    # @api.depends('create_date')
    def _compute_opportunity_is_overdue(self):
        for lead in self:
            timedelta_in_months = self.timedelta_in_months(
                today, lead.last_action_date)

            first_stage_id = self.env['crm.stage'].search(
                [('for_aahd', '=', True)], order='sequence', limit=1)

            if lead.stage_id.id == first_stage_id.id and timedelta_in_months > 3:
                lead.opportunity_is_overdue = True
                
                # get the overdue stage
                lead.stage_id = self.env['crm.stage'].search(
                    [('for_aahd', '=', True), ('is_overdue', '=', True)], limit=1).id
            else:
                lead.opportunity_is_overdue = False

    opportunity_is_overdue = fields.Boolean(
        default=False, compute='_compute_opportunity_is_overdue', readonly=True)

    @api.depends('is_wathiq')
    def _compute_domain_stage(self):
        for rec in self:
            domain = [('for_aahd', '=', True), ('opp_source', 'in',
                                                ['for_two', 'opportunity_channel_opp_source'])]
            if rec.is_wathiq:
                domain = AND([
                    domain, [('is_invisible_wathiq', '=', False)]
                ])
            # else:
            rec.stage_domain_ids = rec.env['crm.stage'].search(domain)

    @api.depends('is_wathiq')
    def _compute_stage_id_domain(self):
        for rec in self:
            domain = [('for_aahd', '=', True), ('opp_source', 'in',
                                                ('for_two', 'opportunity_channel_opp_source'))]
            if rec.is_wathiq:
                domain = AND([
                    domain, [('is_invisible_wathiq', '=', False)]
                ])
            # else:
            rec.stage_id_domain = json.dumps(domain)

    @api.onchange("is_wathiq")
    def _onchange_is_wathiq(self):
        for lead in self:
            if lead.is_wathiq:
                is_wathiq_product = self.env['product.template'].search([
                    ('is_wathiq', '=', True)
                ], limit=1)

                if not is_wathiq_product:
                    raise ValidationError(_(MESSAGE_IS_WATHIQ_ERROR))

                    # return {'warning': {
                    #     'title': _("Warning"),
                    #     'message': ('There is no product named wathiq.Please verify your configuration in the services section.')}}

                lead.product_for_filter_id = is_wathiq_product.id
            else:
                lead.product_for_filter_id = None

    service_type = fields.Selection([('enterprise', 'Enterprise'),
                                     ('basic', 'Basic'),
                                     ('batch', 'Batch'),
                                     ], string='Service Type', tracking=True, default='enterprise', required=True)

    wathiq_email = fields.Char('Wathiq Email')
    proposal_deadline = fields.Datetime(string="Proposal Deadline")
    proposal_submitted_datetime = fields.Datetime(
        string="Proposal Submitted On")
    account_manager_id = fields.Many2one(
        related="partner_id.account_manager_id", readonly=False, string="Account Manager")
    scoop_details = fields.Text(string='Scoop Details')
    project_date_deadline = fields.Date(string="Project Deadline")
    project_execution_time = fields.Integer(string="Execution(Years)")

    # Evaluation
    operational_costs = fields.Monetary(
        "operational costs", currency_field='company_currency', tracking=True)
    profit_margin = fields.Float("Profit margin")
    financial_offer_value = fields.Monetary(
        "Financial offer value", currency_field='company_currency', compute=compute_financial_offer_value)
    cost_details = fields.Selection([('direct', 'Direct'),
                                     ('indirect', 'Indirect')], string="Cost details",)
    execution_direction = fields.Selection([('internal', 'Internal'),
                                            ('external', 'External')], string="Execution Direction",)
    technical_recommendation_notes = fields.Html("Recommendation Notes")
    technical_recommendation = fields.Text("Recommendation")
    technical_recommendation_member_bc = fields.Html(
        "Recommendations of members of the Business Committee")
    work_area_value = fields.Integer("Scoop Of Work")
    budget_and_margin_value = fields.Integer("Budget And margin")
    duration_value = fields.Integer("Duration")
    partner_value = fields.Integer("Client")
    project_risk_value = fields.Integer("Project Risk")
    carrying_capacity_value = fields.Integer("Carrying Capacity")
    strategic_recommendations_value = fields.Integer(
        "strategic Recommendations")
    final_result = fields.Integer(
        "Final Result", compute="compute_final_result")
    work_area_value_max = fields.Integer(
        related='company_id.work_area_value_max')
    budget_and_margin_value_max = fields.Integer(
        related='company_id.budget_and_margin_value_max')
    duration_value_max = fields.Integer(
        related='company_id.duration_value_max')
    partner_value_max = fields.Integer(related='company_id.partner_value_max')
    project_risk_value_max = fields.Integer(
        related='company_id.project_risk_value_max')
    carrying_capacity_value_max = fields.Integer(
        related='company_id.carrying_capacity_value_max')
    strategic_recommendations_value_max = fields.Integer(
        related='company_id.strategic_recommendations_value_max')
    final_result_max = fields.Integer(related='company_id.final_result_max')
    stage_visible = fields.Boolean(
        'Visible Stage', compute="compute_visible_stage_user")
    
    pre_saleperson_id = fields.Many2one(
        'res.users', string='Pre Salesperson',
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)

    is_global_archived = fields.Boolean(default=False)

    def action_set_archived(self):
        for lead in self:
            lead.write({
                'is_global_archived': True
            })

    ###############
    # for bd
    ###############
    # sp_manager_id = fields.Many2one('sp.manager',string='Sp Manager')

    source_lead_id = fields.Many2one(
        'lead.source', string='Source Lead')#, compute="_compute_source_lead_id")

    def _compute_source_lead_id(self):
        self.ensure_one()
        if dict(self.env.context).get('default_from_event', False):
            self.source_lead_id = self.env['lead.source'].sudo().search([
                ('event_as_source', '=', True)
            ]).id
        else:
            self.source_lead_id = None

    business_developer_id = fields.Many2one('res.partner', string='Business Developer', domain=[
                                            ('is_business_developer', '=', True)])
    internal_status_id = fields.Many2one(
        'internal.status', string='Internal Status')
    stackeholder_id = fields.Many2one('res.stakeholder', string='Stackeholder')
    opp_size_id = fields.Many2one(
        'opportunity.size', string='Opportunity Size')
    initial_revshare = fields.Float('Initial revshare %')
    team_id = fields.Many2one(
        'crm.team', string='Sales Team', ondelete="set null")
    vb_account_id = fields.Many2one(
        related="category_portfolio_id.vb_account_id")
    approval_request_id = fields.Many2one(
        "approval.request", "Approval Request")
    visible_approval_request = fields.Boolean(
        'Visible Approval Request', compute="compute_visible_approval_request_user")
    # Customer / contact
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="[('is_customer', '=', True),'|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    # Attachments
    documents_count = fields.Integer(
        compute='_compute_documents_count', string="File")

    def _compute_documents_count(self):
        for lead in self:
            lead.documents_count = self.env['documents.document'].search_count([
                ('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)
            ])

    # Outils for the aahd sales dashbaord.

    def action_open_documents(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'documents.document_action')
        action['domain'] = [('res_model', '=', 'crm.lead'),
                            ('res_id', '=', self.id)]

        return action

    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        self.action_unarchive()
        # group the leads by team_id, in order to write once by values couple (each write leads to frequency increment)
        leads_by_won_stage = {}
        for lead in self:
            domain = [('is_won', '=', True)]

            if lead.for_aahd == True:
                domain += [('for_aahd', '=', True)]
                if lead.opportunity_channel_id.opp_source:
                    domain += [('opp_source', 'in', ('for_two',
                                lead.opportunity_channel_id.opp_source))]

            elif lead.for_bd == True:
                domain += [('for_bd', '=', True)]
                if lead.opportunity_channel_id.bd_stages:
                    domain += [('bd_stages', 'in', ('for_two',
                                lead.opportunity_channel_id.bd_stages))]
            else:
                domain = domain
            won_stages = self._stage_find(domain=domain, limit=None)

            # ABD : We could have a mixed pipeline, with "won" stages being separated by "standard"
            # stages. In the future, we may want to prevent any "standard" stage to have a higher
            # sequence than any "won" stage. But while this is not the case, searching
            # for the "won" stage while alterning the sequence order (see below) will correctly
            # handle such a case :
            #       stage sequence : [x] [x (won)] [y] [y (won)] [z] [z (won)]
            #       when in stage [y] and marked as "won", should go to the stage [y (won)],
            #       not in [x (won)] nor [z (won)]
            stage_id = next(
                (stage for stage in won_stages if stage.sequence > lead.stage_id.sequence), None)
            if not stage_id:
                stage_id = next((stage for stage in reversed(
                    won_stages) if stage.sequence <= lead.stage_id.sequence), won_stages)
            if stage_id in leads_by_won_stage:
                leads_by_won_stage[stage_id] += lead
            else:
                leads_by_won_stage[stage_id] = lead
        for won_stage_id, leads in leads_by_won_stage.items():
            leads.write({'stage_id': won_stage_id.id, 'probability': 100})
        return True
#

    def redirect_lead_opportunity_view(self):
        self.ensure_one()
        ctx = self.env.context
        context = ctx.copy()
        context['default_type'] = self.type
        if 'default_opportunity_channel_id' in context:
            self.opportunity_channel_id = context['default_opportunity_channel_id']
        if 'default_for_bd' in context:
            self.for_bd = context['default_for_bd']
        if 'default_for_aahd' in context:
            self.for_aahd = context['default_for_aahd']
        return {
            'name': _('Lead or Opportunity'),
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'domain': [('type', '=', self.type)],
            'res_id': self.id,
            #             'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context}

    def _handle_aahd_bd_exception(self, error_message):
        context = dict(self.env.context)
        if context.get('default_for_aahd', False):
            if self.env.user.has_group('thiqah_crm.aahd_bd_group'):
                # get first stage
                first_stage = self.env['crm.stage'].search(
                    [('for_aahd', '=', True)], order='sequence', limit=1)
                if first_stage:
                    if self.stage_id.id != first_stage.id:
                        raise UserError(
                            _(error_message))

    # raise error when won revenue is not set
    # raise error when stage is not for ETMD

    def do_notify_sp_manager(self, record_id, email):
        for lead in self:
            template_id = self.env.ref(
                'thiqah_mail_templates.template_mail_notification_sp_manager')
            if email:
                template_id.send_mail(record_id, force_send=True, email_values={
                    'email_to': email})

    def _check_partner_id(self, record_id):
        for lead in self:
            if lead.partner_id:
                if lead.sp_manager_id:
                    # template_id = self.env.ref(
                    #     'thiqah_mail_templates.template_mail_notification_sp_manager')

                    # if lead.sp_manager_id.email:
                    #     template_id.send_mail(int(str(lead.id).split('_')[1]), force_send=True, email_values={
                    #                           'email_to': lead.sp_manager_id.email})
                    # lead.sp_email_sent = True
                    self.do_notify_sp_manager(
                        record_id, lead.sp_manager_id.email)

    def write(self, vals):
        for rec in self:
            if 'stage_id' in vals and vals['stage_id'] != False:
                stage_id = vals['stage_id']
            else:
                stage_id = rec.stage_id.id if rec.stage_id else False

            if stage_id:
                stage_id = self.env['crm.stage'].browse(stage_id)
                if (rec.for_aahd and stage_id.is_won and (('won_revenue' in vals and vals['won_revenue'] == 0) or (rec.won_revenue == 0 and 'won_revenue' not in vals))):
                    raise UserError(_('Please add Won Proposal Amount'))
                # Proposal Stage
                if self.env.user.id != self.env.ref('base.user_root').id and stage_id.is_proposal and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_team_grp')
                                                                                                           or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp')
                                                                                                           or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_presalesteam')
                                                                                                           or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_manager')
                                                                                                           or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_vb_grp')):
                    raise UserError(_("You haven't access to update data on this stage"))
                # Evaluation Stage
                elif self.env.user.id != self.env.ref('base.user_root').id and rec.stage_id.is_brochure_evaluation and not (self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_team_grp')
                                                                                                                            or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_sales_manager_grp')
                                                                                                                            or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_manager')
                                                                                                                            or self.env.user.has_group('thiqah_crm.group_thiqah_aahd_evaluation_member_grp')):
                    raise UserError(_("You haven't access to update data on this stage"))
            if 'opportunity_channel_id' in vals and vals['opportunity_channel_id'] != False:
                opportunity_channel_id = vals['opportunity_channel_id']
            else:
                opportunity_channel_id = rec.opportunity_channel_id.id if rec.opportunity_channel_id else False

            if opportunity_channel_id:
                opportunity_channel_id = self.env['opportunity.channels'].browse(
                    opportunity_channel_id)

                if rec.for_aahd and opportunity_channel_id.opp_source and stage_id and stage_id.opp_source not in (opportunity_channel_id.opp_source, 'for_two') and not stage_id.is_won:
                    raise UserError(_('This Stage is not compatible with Aahd Opportunity Channel'))

                if rec.for_bd and opportunity_channel_id.bd_stages and stage_id and stage_id.bd_stages not in (opportunity_channel_id.bd_stages, 'for_two') and not stage_id.is_won:
                    raise UserError(_('This Stage is not compatible with BD Stages'))
            if rec.is_wathiq:
                is_wathiq_product = self.env['product.template'].search([('is_wathiq', '=', True)], limit=1)

                if not is_wathiq_product:
                    return {'warning': {
                        'title': _("Warning"),
                        'message': ('There is no product named wathiq.Please verify your configuration in the services section.')}}

                vals['product_for_filter_id'] = is_wathiq_product.id

            error_message = "You can't modify the record at this stage."
            self._handle_aahd_bd_exception(error_message)
            if 'partner_id' in vals:
                rec._check_partner_id(int(vals['partner_id']))

            if 'total_score_compute' in vals:
                params = self.env['ir.config_parameter'].sudo()
                saved_score = int(params.get_param('thiqah_crm.passing_score_lead_evaluation'))
                rec.passing_score_lead_evaluation = saved_score
                if (int(vals['total_score_compute']) >= int(rec.passing_score_lead_evaluation)) or vals.get('passed_score'):
                    current_stage = False
                    for stage in self.env['thiqah.crm.stage'].sudo().search([]):
                        if current_stage:
                            rec.thiqah_lead_stage_id = stage.id
                            rec.passed_score = True
                            break
                        if rec.thiqah_lead_stage_id.id == stage.id:
                            current_stage = True
        return super().write(vals)

    def unlink(self):
        # context = dict(self.env.context)
        # if context.get('default_for_aahd', False):
        #     if self.env.user.has_group('thiqah_crm.aahd_bd_group'):
        #         # get first stage
        #         first_stage = self.env['crm.stage'].search(
        #             [('for_aahd', '=', True)], order='sequence', limit=1)
        #         if first_stage:
        #             if self.stage_id.id != first_stage.id:
        #                 raise UserError(
        #                     _("You can't modify the record at this stage."))
        error_message = "You can't delete the record at this stage."
        self._handle_aahd_bd_exception(error_message)

        return super().unlink()

    def get_domain_stages(self, for_aahd, for_bd, opportunity_channel_id):
        domain = [('fold', '=', False)]

        # Extension
        # Modify the domain depending from the is_wathiq checkbox
        # set(is_invisible_wathiq) to True when is_wathiq is False

        if self.is_wathiq:
            domain = AND([
                domain, [('is_invisible_wathiq', '=', False)]
            ])

        if for_aahd == True:
            domain += [('for_aahd', '=', True)]
            if opportunity_channel_id.opp_source:
                domain += [('opp_source', 'in', ('for_two',
                            opportunity_channel_id.opp_source))]

        elif for_bd == True:
            domain += [('for_bd', '=', True)]
            if opportunity_channel_id.bd_stages:
                #                 domain+=[('bd_stages','=',self.opportunity_channel_id.bd_stages)]
                domain += [('bd_stages', 'in', ('for_two',
                            opportunity_channel_id.bd_stages))]
        else:
            domain = domain

        stages = self._stage_find(
            domain=domain, limit=None, order='sequence asc')
        return stages

    # Notification && onchange
    # def _compute_partner_is_set(self):
    #     for lead in self:

    sp_email_sent = fields.Boolean(default='False')

    # Pass to next Stage

    def action_set_next_stage(self):
        for lead in self:
            stages = lead.get_domain_stages(
                lead.for_aahd, lead.for_bd, lead.opportunity_channel_id)

            stage_id = next(
                (stage for stage in stages if stage.sequence > lead.stage_id.sequence), None)

            if stage_id:
                lead.write({'stage_id': stage_id.id})

            self.last_action_date = today
            self.do_notify_sp_manager(lead.id, lead.sp_manager_id.email)

    def action_cancel(self):
        """."""
        for lead in self:
            lead.write({
                'proposal_status': 'cancelled'
            })

    # Fct to under development
    def under_development_opportunity_proposal(self):
        self.write({'proposal_status': 'under_development'})

    # Fct to submit proposal
    def submitted_opportunity_proposal(self):
        self.write({'proposal_status': 'submitted',
                   'proposal_submitted_datetime': fields.Datetime.now()})

    # Fct to award proposal

    def awarded_opportunity_proposal(self):
        self.write({'proposal_status': 'awarded'})
#         stages = self._stage_find(domain=[('id', '!=', self.stage_id.id)], limit=None)
        # stages = self.get_domain_stages(
        #     self.for_aahd, self.for_bd, self.opportunity_channel_id)
        # stage_id = next(
        #     (stage for stage in stages if stage.sequence > self.stage_id.sequence), None)
        # if stage_id:
        #     self.stage_id = stage_id.id

    # Fct to reject proposal
    def rejected_opportunity_proposal(self):
        self.write({'proposal_status': 'rejected', 'active': False})

    event_id = fields.Many2one('crm.lead.event', string='Event',
                               compute='_compute_event_id', recursive=True, store=True, readonly=False,
                               index=True, tracking=True, check_company=True, change_default=True)

    parent_id = fields.Many2one(
        'crm.lead', string='Parent Lead', index=True)

    @api.depends('parent_id.event_id', 'display_event_id')
    def _compute_event_id(self):
        for event in self:
            if event.parent_id:
                event.event_id = event.display_event_id or event.parent_id.event_id

    @api.model_create_multi
    def create(self, vals_list):
        context = dict(self.env.context)
        if context.get('default_for_bd', False):
            permissions = [self.env.user.has_group('thiqah_crm.group_thiqah_sp_manager'), self.env.user.has_group(
                'thiqah_crm.group_thiqah_bd_team_members'), self.env.user.has_group('thiqah_crm.marketing_development_group')]
            permissions = list(set(permissions))
            if not (len(permissions) == 2) or (len(permissions) == 1 and permissions[0] == True):
                raise AccessDenied()
            # if not self.env.user.has_group('thiqah_crm.group_thiqah_sp_manager') or not self.env.user.has_group('thiqah_crm.group_thiqah_bd_team_members') or not self.env.user.has_group('thiqah_crm.marketing_development_group'):
            #         raise AccessDenied()
        for vals in vals_list:
            event_id = vals.get('event_id') or self.env.context.get('default_event_id')
            if event_id:
                vals['display_event_id'] = event_id
        res = super(Lead, self).create(vals_list)
        
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        model_name = self._name.replace('.', '%2E')  # Escape the dot in the model name
        record_id = res.id
        link = f"{base_url}/web#id={record_id}&model={model_name}&view_type=form"
       
        
        if res.user_id:
            user = self.env['res.users'].sudo().browse(res.user_id.id)
            mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
            mail_values = {
                    'subject': _('Opportunity Assignment'),
                    'email_from': self.env.user.partner_id.email_formatted,
                    'email_to': user.email,
                    'mail_server_id':mail_server.id,
                    'body_html': f'''
                                    <p style="margin: 0px;">
                                        <span>Dear {res.user_id.name},</span><br />
                                        <span style="margin-top: 8px;">You have been assigned to Opportunity : {res.name}.</span>
                                    </p>
                                    <p style="padding-top: 24px; padding-bottom: 16px;">
                                        <a href="{link}" t-att-data-oe-model="object._name" t-att-data-oe-id="object.id" style="background-color:#36b4e5; padding: 10px; text-decoration: none; color: #fff; border-radius: 5px;">
                                                View {res.name}
                                        </a>
                                    </p>
                    ''',                     
                    'auto_delete': True,
                }
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send(raise_exception=False)
        if res.pre_saleperson_id:
            user = self.env['res.users'].sudo().browse(res.pre_saleperson_id.id)
            mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
            mail_values = {
                    'subject': _('Opportunity Assignment'),
                    'email_from': self.env.user.partner_id.email_formatted,
                    'email_to': user.email,
                    'mail_server_id':mail_server.id,
                    'body_html': f'''
                                    <p style="margin: 0px;">
                                        <span>Dear {res.user_id.name},</span><br />
                                        <span style="margin-top: 8px;">You have been assigned to Opportunity : {res.name}.</span>
                                    </p>
                                    <p style="padding-top: 24px; padding-bottom: 16px;">
                                        <a href="{link}" t-att-data-oe-model="object._name" t-att-data-oe-id="object.id" style="background-color:#36b4e5; padding: 10px; text-decoration: none; color: #fff; border-radius: 5px;">
                                                View {res.name}
                                        </a>
                                    </p>
                    ''',                            
                    'auto_delete': True,
                }
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send(raise_exception=False)
            
            # self.env['notification.system'].sudo().create({
            #         'message_id': get_random_string(23),
            #         'name': _('Opportunity Assignment'),
            #         'description': _(f'You are assined to Opportunity : {res.name} AS Pre saleperson'),
            #         'user_id': res.pre_saleperson_id.id,
            #         'url_redirect': "/",
            #         'model_id': res.id,
            #         'model_name': 'crm.lead'
            #     })
        return res

    # Fct to Prepare Doc
    def preparing_evaluation(self):
        self.write({'brochure_evaluation_status': 'prepare_doc'})

    # Create Request Approval on Participate Decision
    def create_approval_request(self):
        request_approval_obj = self.env['approval.request'].sudo()
        if not self.approval_request_id.id:
            if self.for_bd:
                categ_id = self.env.ref('thiqah_approvals_crm.approval_category_data_crm_evaluation_thiqah')
            else:
                categ_id = self.env.ref('thiqah_approvals_crm.approval_category_data_crm_evaluation')
            approval_request_id = request_approval_obj.create({
                'name': self.name,
                'category_id': categ_id.id,
                'opportunity_id': self.id,
                'request_owner_id': categ_id.request_owner_id.id
            })
            approval_request_id._compute_approver_ids()
            approval_request_id.action_confirm()
            self.write({'approval_request_id': approval_request_id.id})

    # Fct to Participation Decision
    def participation_decision(self):
        self.write({'brochure_evaluation_status': 'participation_decision'})
        self.create_approval_request()

    # Fct to accept decision

    def accept_decision(self):
        self.write({'brochure_evaluation_status': 'accepted'})
#         stages = self._stage_find(domain=[('id', '!=', self.stage_id.id)], limit=None)
        stages = self.get_domain_stages(
            self.for_aahd, self.for_bd, self.opportunity_channel_id)
        stage_id = next(
            (stage for stage in stages if stage.sequence > self.stage_id.sequence), None)
        if stage_id:
            self.stage_id = stage_id.id

    # Fct to reject decision
    def reject_decision(self):
        self.write({'brochure_evaluation_status': 'rejected', 'active': False})

    # Override fct to change rainbowman image path
    def action_set_won_rainbowman(self):
        self.ensure_one()

        context = dict(self.env.context)
        #  Avoid any side effect
        if 'default_for_aahd' in context:
            if context['default_for_aahd']:
                # raise exception if profit margin is null
                if not self.is_wathiq:
                    if not self.profit_margin > 0:
                        raise UserError(
                            _('The profit margin should not be zero or under.'))

                if not self.date_open_won:
                    raise UserError(
                        _('To complete this action the wining date is required.'))

                self.write({
                    'is_opportunity_won': True,
                    'submission_status': 'awarded'
                    # 'date_open_won': fields.Datetime.now()
                })

        self.action_set_won()

        # set expected_revenue to null
        # self.expected_revenue = None

        message = self._get_rainbowman_message()
        if message:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/thiqah_crm/static/src/img/rainbow_man_thiqah.svg',
                    'type': 'rainbow_man',
                }
            }
        return True

    # Fct to notify sales person and sales team manager before x days of proposal deadline
    @api.model
    def _cron_notification_before_proposal_deadline(self):
        activate_notif_salesperson = self.env['ir.config_parameter'].sudo(
        ).get_param('activate.notif.salesperson')

        activate_notif_salesteam_manager = self.env['ir.config_parameter'].sudo(
        ).get_param('activate.notif.salesteam_manager')

        # deprecated from this process , migrate to the cron_set_overdue method.
        overdue_stage_id = self.env['crm.stage'].search(
            [('for_aahd', '=', True), ('is_overdue', '=', True)], limit=1)

        proposal_stages = self.env['crm.stage'].search(
            [('for_aahd', '=', True), ('from_etmd', '=', True), ('is_proposal', '=', True)], order='sequence')

        etmd_stages = self.env['crm.stage'].search(
            [('for_aahd', '=', True), ('from_etmd', '=', True), ('id', 'not in', proposal_stages.ids)])

        aahd_stages_ids = etmd_stages.filtered(
            lambda stg: stg.sequence < proposal_stages[0].sequence) if proposal_stages else etmd_stages

        # Notify SalesPerson
        if activate_notif_salesperson:
            nbr_days_notif_salespersonnbr = self.env['ir.config_parameter'].sudo(
            ).get_param('nbr.days.notif.salesperson')

            email_template_id_salesperson = self.env['ir.config_parameter'].sudo(
            ).get_param('email_template.notif.salesperson') or False

            date_notif_salesperson = date.today(
            ) - timedelta(days=int(nbr_days_notif_salespersonnbr))
            for rec in self.search([
                ('stage_id', 'in', aahd_stages_ids.ids),
                ('proposal_deadline', '>=', datetime.combine(
                    date_notif_salesperson, datetime.min.time())),
                ('proposal_deadline', '<=', datetime.combine(
                    date_notif_salesperson, datetime.max.time())),
            ]):

                if email_template_id_salesperson and rec.team_id.user_id:
                    email_values = {'email_to': rec.team_id.user_id.email,
                                    'partner_ids': rec.team_id.user_id.partner_id.ids}
                    self.env['mail.template'].browse(
                        int(email_template_id_salesperson)).send_mail(rec.id, force_send=True)

                # rec.stage_id = overdue_stage_id.id

        # Notify SalesTeamManager
        if activate_notif_salesteam_manager:
            nbr_days_notif_salesteam_manager = self.env['ir.config_parameter'].sudo(
            ).get_param('nbr.days.notif.salesteam_manager')
            email_template_id_salesteam_manager = self.env['ir.config_parameter'].sudo(
            ).get_param('email_template.notif.salesteam_manager') or False

            date_notif_salesteam_manager = date.today(
            ) - timedelta(days=int(nbr_days_notif_salesteam_manager))
            for rec1 in self.search([
                ('stage_id', 'in', aahd_stages_ids.ids),
                ('proposal_deadline', '>=', datetime.combine(
                    date_notif_salesteam_manager, datetime.min.time())),
                ('proposal_deadline', '<=', datetime.combine(
                    date_notif_salesteam_manager, datetime.max.time())),
            ]):
                if email_template_id_salesteam_manager and rec1.user_id:
                    email_values = {'email_to': rec1.user_id.email,
                                    'partner_ids': rec1.user_id.partner_id.ids}
                    self.env['mail.template'].browse(int(email_template_id_salesteam_manager)).send_mail(
                        rec1.id, force_send=True, email_values=email_values)

                # rec1.stage_id = overdue_stage_id.id

    ###################################
    # Cron Jobs
    ###################################

    is_archived = fields.Boolean(default=False)

    is_lost_last_year = fields.Boolean(
        default=False, compute="_compute_lost_last_year", store=True)

    @api.depends("create_date", "active")
    def _compute_lost_last_year(self):
        for lead in self:
            if lead.create_date.year == int(datetime.today().strftime("%Y"))-1 and lead.active == False:
                lead.is_lost_last_year = True

    def thiqah_action_archive(self):
        self.ensure_one()
        self.is_archived = True

    def archive_winning_opportunities(self):
        """
        Any winning opportunity in the last year will be archived automatically.
        """
        current_year = datetime.today().strftime("%Y")  # str
        for lead in self.search([
            ('for_aahd', '=', True),
        ]):
            if str(lead.create_date.year) != current_year and lead.is_won == True:
                lead.thiqah_action_archive()

        # if lead.create_date.year == int(current_year)-1:
        #     if lead.active == False:
        #         lead
            if lead.create_date.year == int(current_year)-1:
                if lead.active == False:
                    lead.is_lost_last_year = True

    def cron_set_overdue(self):
        """
        this cron job ensure the dynamic setting to overdue status after x days.
        """

        overdue_stage_id = self.env['crm.stage'].search(
            [('for_aahd', '=', True), ('is_overdue', '=', True)], limit=1)

        # filter the stage_ids && ensure that the won and the lost are exluded (there is no stage with lost indication so we will apply 'active is false')
        # Overdue will be included.
        _stage_ids = self.env['crm.stage'].search(
            [('for_aahd', '=', True), ('is_won', '=', False)], order='sequence')

        # get the configuration parameters
        activate_overdue_criteria = self.env['ir.config_parameter'].sudo(
        ).get_param('activate.overdue.criteria')

        if activate_overdue_criteria:
            # get the days to determine the overdue
            nbr_days_to_overdue = self.env['ir.config_parameter'].sudo(
            ).get_param('nbr.days.overdue')

            domain = [('stage_id', 'in', _stage_ids.ids),
                      ('active', '=', True)]

            for lead in self.search(domain):
                # Calculating the length(duration) of stay
                deadline_date = lead.create_date + \
                    timedelta(days=int(nbr_days_to_overdue))

                if date.today() > deadline_date.date():
                    lead.stage_id = overdue_stage_id.id

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Override"""
        if custom_values is None:
            custom_values = {'type': 'lead'}
        if msg_dict.get('subject'):
            custom_values['name'] = msg_dict['subject']
        if msg_dict.get('body'):
            custom_values['description'] = msg_dict['body']
            msg_dict.pop('body')
        return super(Lead, self.with_context(from_mail=True)).message_new(msg_dict, custom_values)
