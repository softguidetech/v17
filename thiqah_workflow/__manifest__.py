# -*- coding: utf-8 -*-
{
    'name': "thiqah_workflow",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # test upload to gitlab
    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ir_actions_act_window.xml',
        'views/ir_ui_menu.xml',
        'views/workflow_action.xml',
        'views/workflow_state.xml',
        'views/workflow_transition.xml',
        'views/workflow_workflow.xml',
        'views/workflow_transition_validation.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'thiqah_workflow/static/src/js/script.js',
    #     ]
    # },
    'license': 'OEEL-1',

}
