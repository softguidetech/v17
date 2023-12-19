# -*- coding: utf-8 -*-
from cgi import print_arguments
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo import fields, http, SUPERUSER_ID
from markupsafe import Markup
from odoo.osv.expression import OR
from operator import itemgetter
from odoo.tools import is_html_empty
from odoo.tools import groupby as groupbyelem
from odoo.addons.website.controllers import form, main
# from odoo.addons.website_helpdesk_form.controller.main import WebsiteForm
from odoo.addons.website_helpdesk.controllers.main import WebsiteForm
from odoo.addons.website_helpdesk.controllers.main import WebsiteHelpdesk
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.web import Home
from odoo.http import request
from odoo.exceptions import ValidationError
from datetime import datetime, date

import logging

import base64

_logger = logging.getLogger(__name__)


class WebsiteForms(form.WebsiteForm):

    def extract_data(self, model, values):
        dest_model = request.env[model.sudo().model]

        data = {
            'record': {},        # Values to create record
            'attachments': [],  # Attached files
            'custom': '',        # Custom fields values
            'meta': '',         # Add metadata if enabled
        }

        authorized_fields = model.with_user(
            SUPERUSER_ID)._get_form_writable_fields()

        error_fields = []
        custom_fields = []

        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                field_name = field_name.split('[', 1)[0]

                # If it's an actual binary field, convert the input file
                # If it's not, we'll use attachments instead
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(
                        field_value.read())
                    field_value.stream.seek(0)  # do not consume value forever
                    if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                        data['record'][field_name +
                                       "_filename"] = field_value.filename
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(
                        self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

            # If it's a custom field
            elif field_name != 'context':
                custom_fields.append((field_name, field_value))

        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        # Add metadata if enabled  # ICP for retrocompatibility
        if request.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ = request.httprequest.headers.environ
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP", environ.get("REMOTE_ADDR"),
                "USER_AGENT", environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER", environ.get("HTTP_REFERER")
            )

        # This function can be defined on any model to provide
        # a model-specific filtering of the record values
        # Example:
        # def website_form_input_filter(self, values):
        #     values['name'] = '%s\'s Application' % values['partner_name']
        #     return values
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(
                request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items(
        ) if field['required'] and not label in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)
        return data

    def insert_record(self, request, model, values, custom, meta=None):
        # ensure the mapping between records | criterias.
        for workflow in request.env['workflow.workflow'].sudo().search([]):
            workflow.mapping_records_criterias()

        model_name = model.sudo().model
        current_user = request.env.user.id

        if model_name == 'mail.mail':
            values.update({'reply_to': values.get('email_from')})

        if model_name == 'helpdesk.ticket' and request.env.user:
            user = current_user
            values.update({'activate_notification': True})

            # get the ticket_type_id that should be equivalent to a given type that should be reserved to the sp manageres as name.
            ticket_from_sp = request.env['helpdesk.ticket.type'].sudo().browse(
                [int(values['ticket_type_id'])]).for_sp_manager

            if ticket_from_sp:
                create_values = {
                    'name': values['name'],
                    'type': 'lead',
                    'for_bd': True,
                    'description': values['description']
                }

                if 'partner_id' in values:
                    create_values['partner_id'] = values['partner_id']

                # create a lead and convert it to an opportunity. [('type','=','opportunity'),('for_bd','=',True)]
                lead = request.env['crm.lead'].sudo().create(create_values)
                # lead.convert_opportunity(lead.partner_id.id, user_ids=False, team_id=False)
                values['crm_lead_id'] = lead.id
        elif model_name == 'thiqah.project.service.request':
            values['date_from'] = date.today()
        else:
            user = SUPERUSER_ID

        # TODO: the selection criterion for choosing the user needs more absratcion.
        # knowing that we have chosen to treat the models case by case in order to avoid side effects.

        
        record = request.env[model_name].sudo().with_context(
            mail_create_nosubscribe=True).create(values)

        if custom or meta:
            _custom_label = "%s\n___________\n\n" % _(
                "Other Information:")  # Title for custom fields
            if model_name == 'mail.mail':
                _custom_label = "%s\n___________\n\n" % _(
                    "This message has been posted on your website!")
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
            custom_content = (default_field_data + "\n\n" if default_field_data else '') \
                + (_custom_label + custom + "\n\n" if custom else '') \
                + (self._meta_label + meta if meta else '')

            # If there is a default field configured for this model, use it.
            # If there isn't, put the custom data in a message instead
            if default_field.name:
                if default_field.ttype == 'html' or model_name == 'mail.mail':
                    custom_content = nl2br(custom_content)
                record.update({default_field.name: custom_content})
            else:
                values = {
                    'body': nl2br(custom_content),
                    'model': model_name,
                    'message_type': 'comment',
                    'res_id': record.id,
                }
                request.env['mail.message'].with_user(
                    SUPERUSER_ID).create(values)

        return record.id

    # Link all files attached on the form
    def insert_attachment(self, model, id_record, files):
        orphan_attachment_ids = []
        model_name = model.sudo().model
        record = model.env[model_name].browse(id_record)
        authorized_fields = model.with_user(
            SUPERUSER_ID)._get_form_writable_fields()
        attachment_for_crm = []
        # Customization
        # We need to add the same attachment(s) on crm_lead in case the type is 'change request'
        model_name = model.sudo().model
        crm_lead_id = 0
        if model_name == 'helpdesk.ticket':
            crm_lead_id = record.crm_lead_id

        for file in files:
            custom_field = file.field_name not in authorized_fields
            datas = base64.encodebytes(file.read())
            filename = file.filename
            attachment_value = {
                'name': filename,
                'datas': datas,
                'res_model': model_name,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(
                attachment_value)

            # Customization
            # TODO : we can use IrAttachment.copy()
            if crm_lead_id > 0:
                # If this condition is true , this indicates that the ticket type is Change Request.
                value_for_lead = {
                    'name': filename,
                    'datas': datas,
                    'res_model': 'crm.lead',
                    'res_id': int(crm_lead_id),
                }
                attachment_crm_id = request.env['ir.attachment'].sudo().create(
                    value_for_lead)

                # insert into document.document
                request.env['documents.document'].sudo().create({
                    'name': 'Document-' + str(filename),
                    'type': 'binary',
                    'res_model': 'crm.lead',
                    'res_id': int(crm_lead_id),
                    'folder_id': 1,
                    'attachment_id': attachment_crm_id.id
                })

                # We need to separate the new process from the default one to avoid the side effects.
                attachment_for_crm = [attachment_crm_id.id]

            if attachment_id and not custom_field:
                record.sudo()[file.field_name] = [(4, attachment_id.id)]
            else:
                # extend orphan_attachment_ids to append multpile values;
                orphan_attachment_ids.append(attachment_id.id)

        if model_name != 'mail.mail':
            # If some attachments didn't match a field on the model,
            # we create a mail.message to link them to the record

            # Customization
            # Add a list that collects all the mail's values.
            mails_values = []
            if orphan_attachment_ids:
                values = {
                    'body': _('<p>Attached files : </p>'),
                    'model': model_name,
                    'message_type': 'comment',
                    'res_id': id_record,
                    'attachment_ids': [(6, 0, orphan_attachment_ids)],
                    'subtype_id': request.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'),
                }
                mails_values.append(values)

            if attachment_for_crm:
                values = {
                    'body': _('<p>Attached files : </p>'),
                    'model': 'crm.lead',
                    'message_type': 'comment',
                    'res_id': int(crm_lead_id),
                    'attachment_ids': [(6, 0, attachment_for_crm)],
                    'subtype_id': request.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'),
                }
                mails_values.append(values)

            if mails_values:
                for mail_values in mails_values:
                    request.env['mail.message'].sudo().create(mail_values)
        else:
            # If the model is mail.mail then we have no other choice but to
            # attach the custom binary field files on the attachment_ids field.
            for attachment_id_id in orphan_attachment_ids:
                record.attachment_ids = [(4, attachment_id_id)]

    # Ovveride this fct to do not create customer when add new ticket

    def _handle_website_form(self, model_name, **kwargs):
        res = super(WebsiteForm, self)._handle_website_form(
            model_name, **kwargs)
        return res

    @http.route(['/my/tickets/submit'], type='http', auth="user", methods=['POST'], website=True)
    def portal_helpdesk_ticket_submit(self, **kw):
        partner_id = kw.get('partner_id') if kw.get('partner_id') else False
        category_portfolio_id = kw.get(
            'sector_id') if kw.get('sector_id') else False
        description = kw.get('description') if kw.get('description') else ''
        if partner_id and category_portfolio_id:
            helpdeks_ticket = request.env['helpdesk.ticket'].sudo().create({
                'partner_id': partner_id,
                'category_portfolio_id': category_portfolio_id,
                'description': description,
            })
        values = self._prepare_portal_layout_values()
        return request.render("thiqah_helpdesk_portal.portal_my_helpdesk_home", values)


class WebsiteHelpdesk(WebsiteHelpdesk):

    def get_helpdesk_team_data(self, team, search=None):
        values = super().get_helpdesk_team_data(team, search)
        values['customers'] = request.env['res.partner'].sudo().search(
            [('is_customer', '=', True)])
        values['sales_team'] = request.env['crm.team'].sudo().search([])
        values['sectors'] = request.env['category.portfolio'].sudo().search([])
        # certain types are reserved for sp managers, so this case must be treated.

        has_group = request.env.user.has_group(
            'thiqah_crm.group_thiqah_sp_manager')
        helpdesk_ticket_type = request.env['helpdesk.ticket.type'].sudo()
        if has_group:
            values['ticket_types'] = helpdesk_ticket_type.search([])
        else:
            values['ticket_types'] = helpdesk_ticket_type.search([
                ('for_sp_manager', '=', False)
            ])

        return values

    @http.route(['/new/helpdesk/ticket'], type='http', auth="public", website=True, sitemap=True)
    def website_helpdesk_tickets(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].search([], order="id asc")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        result['is_html_empty'] = is_html_empty
        return request.render("website_helpdesk.team", result)

    @http.route(['/my/tickets/submit'], type='http', auth="user", website=True)
    def portal_helpdesk_ticket_submit(self, **kw):
        partner_id = kw.get('partner_id') if kw.get('partner_id') else False
        category_portfolio_id = kw.get(
            'sector_id') if kw.get('sector_id') else False
        description = kw.get('description') if kw.get('description') else ''
        if partner_id and category_portfolio_id:
            helpdeks_ticket = request.env['helpdesk.ticket'].sudo().create({
                'partner_id': partner_id,
                'category_portfolio_id': category_portfolio_id,
                'description': description,
            })
        values = self._prepare_portal_layout_values()
        return request.render("thiqah_helpdesk_portal.portal_my_helpdesk_home", values)


#
class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        helpdesk_obj = request.env['helpdesk.ticket']
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        # Tickets
        domain = [('create_uid', '=', request.uid)]
        try:
            all_tickets = helpdesk_obj.search_count(domain)
            stage_ids = request.env['helpdesk.stage'].search(
                [('show_in_portal', '=', True)])
        except Exception:
            all_tickets = 0
            stage_ids = request.env['helpdesk.stage']
        values.update({'all_tickets': all_tickets,
                      'tickets_stage_ids': stage_ids})
        return values

    # @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    # def home(self, **kw):
    #     values = self._prepare_portal_layout_values()
    #     # if request.env.user.has_group('base.group_portal'):
    #     #     return '404 Not found'
    #     return request.render("thiqah_helpdesk_portal.portal_my_helpdesk_home", values)

    @http.route(['/my/helpdesk/home'], type='http', auth="user", website=True)
    def my_helpdesk_home(self, **kw):
        values = self._prepare_portal_layout_values()

        return request.render("thiqah_helpdesk_portal.portal_my_helpdesk_home", values)

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None,
                            groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'reference': {'label': _('Reference'), 'order': 'id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_id', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_id', '=', False)]},
            'open': {'label': _('Open'), 'domain': [('close_date', '=', False)]},
            'closed': {'label': _('Closed'), 'domain': [('close_date', '!=', False)]},
            'last_message_sup': {'label': _('Last message is from support')},
            'last_message_cust': {'label': _('Last message is from customer')},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'id': {'input': 'id', 'label': _('Search in Reference')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if filterby in ['last_message_sup', 'last_message_cust']:
            discussion_subtype_id = request.env.ref('mail.mt_comment').id
            messages = request.env['mail.message'].search_read(
                [('model', '=', 'helpdesk.ticket'),
                 ('subtype_id', '=', discussion_subtype_id)],
                fields=['res_id', 'author_id'], order='date desc')
            last_author_dict = {}
            for message in messages:
                if message['res_id'] not in last_author_dict:
                    last_author_dict[message['res_id']
                                     ] = message['author_id'][0]

            ticket_author_list = request.env['helpdesk.ticket'].search_read(
                fields=['id', 'partner_id'])
            ticket_author_dict = dict(
                [(ticket_author['id'], ticket_author['partner_id'][0] if ticket_author['partner_id'] else False) for
                 ticket_author in ticket_author_list])

            last_message_cust = []
            last_message_sup = []
            for ticket_id in last_author_dict.keys():
                if last_author_dict[ticket_id] == ticket_author_dict[ticket_id]:
                    last_message_cust.append(ticket_id)
                else:
                    last_message_sup.append(ticket_id)

            if filterby == 'last_message_cust':
                domain = [('id', 'in', last_message_cust)]
            else:
                domain = [('id', 'in', last_message_sup)]

        else:
            domain = searchbar_filters[filterby]['domain']

        # get user by uid
        user = request.env['res.users'].browse(request.uid)
        if user and not user.has_group('thiqah_helpdesk_portal.group_helpdesk_portal_see_all_ticket'):
            domain += [('create_uid', '=', request.uid)]

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR(
                    [search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR(
                    [search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search),
                                                    ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in in ('status', 'all'):
                search_domain = OR(
                    [search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = request.env['helpdesk.ticket'].search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in,
                      'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )
        # check has group access right

        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page,
                                                        offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in
                               groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return request.render("helpdesk.portal_helpdesk_ticket", values)

    #  add controller submit ticket
    @http.route(['/my/tickets/submit'], type='http', auth="user", website=True, method='POST')
    def portal_helpdesk_ticket_submit(self, **kw):
        partner_id = kw.get('partner_id') if kw.get('partner_id') else False
        category_portfolio_id = kw.get(
            'sector_id') if kw.get('sector_id') else False
        description = kw.get('description') if kw.get('description') else ''
        if partner_id and category_portfolio_id:
            helpdeks_ticket = request.env['helpdesk.ticket'].sudo().create({
                'partner_id': partner_id,
                'category_portfolio_id': category_portfolio_id,
                'description': description,
            })
        values = self._prepare_portal_layout_values()
        return request.render("thiqah_helpdesk_portal.portal_my_helpdesk_home", values)
