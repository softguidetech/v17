# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH Client Registration',
    'category': 'Sales/CRM',
    'version': '1.0',
    'summary': 'Thiqah client registration',
    'author': 'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': ['web','website', 'thiqah_base','thiqah_portal', 'thiqah_freelance', 'thiqah_workflow'],
    'data': [
        'data/ir_sequence.xml',
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/portal_layout.xml',
        'views/client_registration_views.xml',
        'views/menus.xml',

    ],
    'assets': {
        'web.assets_frontend':{
            'client_registration/static/src/js/main.js',
            'client_registration/static/src/css/style.css',
        }
    },
    'bootstrap': True,
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
