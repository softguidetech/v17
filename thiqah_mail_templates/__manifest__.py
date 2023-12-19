# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH mail Template',
    'sequence': 2,
    'version': '1.0',
    'summary': 'Thiqah Custom email templates',
    'author': 'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': [
        'web', 'base', 'mail', 'portal', 'auth_signup', 'helpdesk', 'documents'
    ],
    'data': [
        'data/mail_templates.xml',
        'data/mail_template_data.xml',
        'data/document_mail_template.xml',
        'data/helpdesk_mail_template.xml',
        'data/portal_mail_template.xml',
        'data/aahd_request_tracker.xml',
        'data/assignment_project_conversion.xml',
        'data/contract_notifcation.xml',
        'data/notification_sp_team.xml',
        'data/notification_aahd_bd.xml',
        'data/notification_sp_manager.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'thiqah_mail_templates/static/scss/mail.scss'
        ],

    },
    'bootstrap': True,
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
