# -*- coding: utf-8 -*-
{
    'name': "thiqah_project",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Thiqah",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'crm', 'thiqah_crm', 'website', 'documents', 'thiqah_workflow', 'hr'],

    # always loaded
    'data': [
        # Notification
        'data/service_request_template_email.xml',

        # Workflow
        'data/service_request_workflow_data.xml',

        # cron
        'data/sla_indicator_cron.xml',

        # Service Managment
        'views/contract_type.xml',
        'views/risk_type.xml',
        'views/action_type.xml',

        # Thiqah Project Managment
        'views/request_service.xml',
        'views/service_type.xml',
        'views/service_catalog.xml',
        'views/project_project.xml',

        # For both
        'views/request_stage.xml',
        'views/project_department.xml',
        'views/document_type.xml',
        'views/res_config_settings_views.xml',

        #
        'views/crm_lead_inherit.xml',

        # Report
        'report/service_request_template.xml',
        'report/service_request.xml',

        # Mandatory data
        'data/service_data.xml',
        'views/ir_actions_act_window.xml',
        'views/ir_ui_menu.xml',
        'security/base_security.xml',

        'security/ir.model.access.csv',

        # Portal
        'view/website_menu.xml',
        'view/basic_data.xml',
        'view/overall_summary.xml',
        'view/resources.xml',
        'view/risk_issues.xml',
        'view/revenue_plans.xml',
        'view/deliverables.xml',
        'view/utilizations.xml',
        'view/documents.xml',
        'view/project_add_template.xml',
        'view/project_templates.xml',
        'view/risks_issues_update.xml',
        # 'view/project_update.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'thiqah_project/static/src/js/utils.js',
            'thiqah_project/static/src/js/script.js',
            'thiqah_project/static/src/js/add_project.js',
            'thiqah_project/static/src/js/table_project.js',
            # 'thiqah_project/static/src/js/update_utils.js',
            'thiqah_project/static/src/scss/style.scss'
        ]
    },
    'license': 'OEEL-1',
}
