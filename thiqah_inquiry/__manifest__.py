# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH Inquiry',
    'category': 'Helpdesk',
    'version': '1.0',
    'summary': 'Thiqah Inquiries requests managment',
    'author': 'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': ['website', 'thiqah_base','thiqah_portal', 'thiqah_workflow'],
    'data': [
        'data/ir_sequence.xml',
        'data/data.xml',
        'data/inquiry_request_sla_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/inquiry_request_views.xml',
        'views/portal_layout.xml',
        'views/hr_department.xml',
        'views/inquiry_request_sla_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_frontend':{
            '/thiqah_inquiry/static/src/js/add_inquiry.js',
            '/thiqah_inquiry/static/src/js/dashboard.js',
        }
    },
    'bootstrap': True,
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
