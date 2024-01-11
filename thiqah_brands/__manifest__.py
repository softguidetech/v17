# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH Odoo Brands',
    'category': 'Web',
    'version': '1.0',
    'sequence': 2,
    'description': """
        This module update odoo apps icons.""",
    'depends': ['base', 'web', 'crm', 'mail', 'approvals', 'project', 'event', 'contacts', 'helpdesk',
                'documents', 'calendar', 'mass_mailing', 'marketing_automation','social', 'website', 'thiqah_project'],
# , 'note'
    'author': 'THIQAH',
    'website': 'https://thiqah.sa',
    'data': [
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'thiqah_brands/static/src/css/icon.css',
        ]
    },
    'license': 'LGPL-3',
    'uninstall_hook': '_uninstall_reset_web_icons',
}
