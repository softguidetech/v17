# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH Helpdesk Portal',
    'category': 'Sales/CRM',
    'sequence': 2,
    'version': '1.0',
    'summary': 'Thiqah Custom Portal Helpdesk',
    'author': 'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': [
        'web', 'base', 'website', 'portal', 'project', 'helpdesk', 'website_helpdesk', 'mail', 'notification_system'
    ],
# 'website_helpdesk_form'
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'views/helpdesk_views.xml',
        'views/portal_templates.xml',
        'views/helpdesk_templates.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'thiqah_helpdesk_portal/static/src/scss/style.scss',
            'thiqah_helpdesk_portal/static/src/scss/website_style.scss',
            'thiqah_helpdesk_portal/static/src/js/helpdesk_customisation.js',
        ],


    },
    'bootstrap': True,
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
