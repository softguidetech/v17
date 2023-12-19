# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.http import request

def _uninstall_reset_web_icons(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('base.menu_administration').web_icon='base,static/description/settings.png'
    env.ref('base.menu_management').web_icon='base,static/description/modules.png'
    env.ref('helpdesk.menu_helpdesk_root').web_icon='helpdesk,static/description/icon.png'
    env.ref('calendar.mail_menu_calendar').web_icon='calendar,static/description/icon.png'
    env.ref('contacts.menu_contacts').web_icon='contacts,static/description/icon.png'
    env.ref('crm.crm_menu_root').web_icon='crm,static/description/icon.png'
    env.ref('mail.menu_root_discuss').web_icon='mail,static/description/icon.png'
    env.ref('documents.menu_root').web_icon='documents,static/description/icon.png'
    env.ref('mass_mailing.mass_mailing_menu_root').web_icon='mass_mailing,static/description/icon.png'
    env.ref('event.event_main_menu').web_icon='event,static/description/icon.png'
    env.ref('marketing_automation.marketing_automation_menu').web_icon='marketing_automation,static/description/icon.png'
    env.ref('note.menu_note_notes').web_icon='note,static/description/icon.png'
    env.ref('project.menu_main_pm').web_icon='project,static/description/icon.png'
    env.ref('social.menu_social_global').web_icon='social,static/description/icon.png'
    #env.ref('hr_timesheet.timesheet_menu_root').web_icon='hr_timesheet,static/description/icon.png'
