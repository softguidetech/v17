# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'THIQAH Approvals - CRM Evaluation',
    'version': '17.0',
    'category': 'Human Resources/Approvals',
    'description': """
        
    """,
    'depends': ['approvals', 'crm',],
    'data': [
        'security/ir.model.access.csv',
        'data/approval_category_data.xml',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
       
        'report/business_commitee_tracker_report.xml',
         'report/business_commitee_tracker_view.xml',
        'views/menu.xml'
    ],
    'demo': [
       
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
