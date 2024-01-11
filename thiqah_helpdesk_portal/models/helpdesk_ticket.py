# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons.helpdesk.models.helpdesk_ticket import HelpdeskTicket


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    icon = fields.Char('Icon')
    show_in_portal = fields.Boolean("Show This Stage On Portal", default=True)
    count_my_tickets = fields.Integer(compute='_compute_my_tickets_count')

    def _compute_my_tickets_count(self):
        res = self.env['helpdesk.ticket'].read_group(
            [('stage_id', 'in', self.ids),
             ('create_uid', '=', self._uid)],
            ['stage_id'], ['stage_id'])
        stage_data = {r['stage_id'][0]: r['stage_id_count'] for r in res}
        for stage in self:
            stage.count_my_tickets = stage_data.get(stage.id, 0)


class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    team_id = fields.Many2one('helpdesk.team', string="Team", required=True)

    description = fields.Text('Description')

    assigned_to_user_id = fields.Many2one('res.users', string='Default Assigned to', tracking=True, required=True,
                                          domain=lambda self: [
                                              ('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])
    required_attachment = fields.Boolean(
        'Need Required Attachment', default=False)

    code = fields.Char('Code', required=True)

    for_sp_manager = fields.Boolean(string="For SP Managers",default=False, required=True)

    @api.model
    def get_team_id(self, type_id):
        if type_id:
            ticket_type_id = self.env['helpdesk.ticket.type'].sudo().search(
                [('id', '=', type_id)], limit=1)
            if ticket_type_id:
                return {'ticket_team_id': ticket_type_id.team_id.id if ticket_type_id.team_id.id else False,
                        'user_id': ticket_type_id.assigned_to_user_id.id if ticket_type_id.assigned_to_user_id else False,
                        'description': ticket_type_id.description or '',
                        'required_attachment': "required" if ticket_type_id.required_attachment else "none",
                        }
        return None


class THIQAHHelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sales_team_id = fields.Many2one(
        'crm.team', string='Sales Team', ondelete="set null")
    sector_id = fields.Many2one(
        'category.portfolio', string='Portfolio', ondelete="set null")
    partner_position = fields.Char('Customer Position')
    responsible_name = fields.Char('Responsible Name')
    responsible_mobile = fields.Char('Responsible Mobile')

    # for technical purpose ,crm_lead_id should be intger 
    crm_lead_id = fields.Integer()

    # Ovveride this fct to do not create customer when add new ticket
    @api.model_create_multi
    def create(self, list_value):
        now = fields.Datetime.now()
        # determine user_id and stage_id if not given. Done in batch.
        teams = self.env['helpdesk.team'].browse(
            [vals['team_id'] for vals in list_value if vals.get('team_id')])
        team_default_map = dict.fromkeys(teams.ids, dict())
        for team in teams:
            team_default_map[team.id] = {
                'stage_id': team._determine_stage()[team.id].id,
                'user_id': team._determine_user_to_assign()[team.id].id
            }

        # Manually create a partner now since 'generate_recipients' doesn't keep the name. This is
        # to avoid intrusive changes in the 'mail' module
        # TDE TODO: to extract and clean in mail thread
        #         for vals in list_value:
        #             partner_id = vals.get('partner_id', False)
        #             partner_name = vals.get('partner_name', False)
        #             partner_email = vals.get('partner_email', False)
        #             if partner_name and partner_email and not partner_id:
        #                 parsed_name, parsed_email = self.env['res.partner']._parse_partner_name(partner_email)
        #                 if not parsed_name:
        #                     parsed_name = partner_name
        #                 try:
        #                     vals['partner_id'] = self.env['res.partner'].find_or_create(
        #                         tools.formataddr((partner_name, parsed_email))
        #                     ).id
        #                 except UnicodeEncodeError:
        #                     # 'formataddr' doesn't support non-ascii characters in email. Therefore, we fall
        #                     # back on a simple partner creation.
        #                     vals['partner_id'] = self.env['res.partner'].create({
        #                         'name': partner_name,
        #                         'email': partner_email,
        #                     }).id

        # determine partner email for ticket with partner but no email given
        partners = self.env['res.partner'].browse([vals['partner_id'] for vals in list_value if
                                                   'partner_id' in vals and vals.get(
                                                       'partner_id') and 'partner_email' not in vals])
        partner_email_map = {partner.id: partner.email for partner in partners}
        partner_name_map = {partner.id: partner.name for partner in partners}

        for vals in list_value:
            if vals.get('team_id'):
                team_default = team_default_map[vals['team_id']]
                if 'stage_id' not in vals:
                    vals['stage_id'] = team_default['stage_id']
                # Note: this will break the randomly distributed user assignment. Indeed, it will be too difficult to
                # equally assigned user when creating ticket in batch, as it requires to search after the last assigned
                # after every ticket creation, which is not very performant. We decided to not cover this user case.
                if 'user_id' not in vals:
                    vals['user_id'] = team_default['user_id']
                if vals.get(
                        'user_id'):  # if a user is finally assigned, force ticket assign_date and reset assign_hours
                    vals['assign_date'] = fields.Datetime.now()
                    vals['assign_hours'] = 0

            # set partner email if in map of not given
            if vals.get('partner_id') in partner_email_map:
                vals['partner_email'] = partner_email_map.get(
                    vals['partner_id'])
            # set partner name if in map of not given
            if vals.get('partner_id') in partner_name_map:
                vals['partner_name'] = partner_name_map.get(vals['partner_id'])

            if vals.get('stage_id'):
                vals['date_last_stage_update'] = now

        # context: no_log, because subtype already handle this
        tickets = super(HelpdeskTicket, self).create(list_value)

        # make customer follower
        for ticket in tickets:
            if ticket.partner_id:
                ticket.message_subscribe(partner_ids=ticket.partner_id.ids)

            ticket._portal_ensure_token()

        # apply SLA
        tickets.sudo()._sla_apply()

        return tickets
