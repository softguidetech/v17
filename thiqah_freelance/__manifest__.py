# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH Freelance',
    'category': 'Sales/CRM',
    'version': '1.0',
    'summary': 'Thiqah Freealnce requests mangment',
    'author': 'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': ['web','website', 'thiqah_base','thiqah_portal', 'thiqah_workflow'],
    'data': [
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'data/data.xml',
        'report/agreement_report.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/freelance_request_workflow_data.xml',
        'views/templates.xml',
        'views/freelance_request_views.xml',
        'views/freelance_application_views.xml',
        'views/freelance_workorder_views.xml',
        'views/res_entity_views.xml',
        'views/oracle_config_views.xml',
        'views/menus.xml',

    ],
    'assets': {
        'web.assets_frontend':{
            'thiqah_freelance/static/src/js/add_freelance_request.js',
        }
    },
    'bootstrap': True,
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
