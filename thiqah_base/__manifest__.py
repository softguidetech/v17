# -*- coding: utf-8 -*-
{
    'name': "Thiqah Base",

    'summary': """
        This module contains all customizations affecting the core such as overriding core security rules.
        """,

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
    'depends': ['base', 'project', 'thiqah_project', 'thiqah_portal', 'mail', 'calendar', 'contacts', 'website','portal', 'hr','auditlog','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/base_groups.xml',
        'security/ir_ui_menu.xml',
        'security/project_security.xml',
        'security/crm.xml',
        'security/service_request_groups.xml',
        'data/user_category.xml',
        'data/nationalities_data.xml',
        'views/views.xml',
        'views/res_users.xml',
        'views/user_category.xml',
        'views/res_partner_views.xml',
        'views/hr_department.xml',
        'views/res_country.xml',
        'views/user_service_access_views.xml',

        # Report
        'report/thiqah_user_analysis_wizard.xml',
        'report/user_analysis_configuration.xml',
        'report/user_analysis_templates.xml',
        'report/user_analysis_xlsx.xml',

        # Action(s) Window
        'views/ir_actions_act_window.xml',

        # Menu(s)
        'views/menuitem.xml',


    ],
    'assets': {
        'web.assets_backend': {
            # 'thiqah_base/static/src/js/navbar/systray.js',
            'thiqah_base/static/src/css/navbar/systray.css',
            # 'thiqah_base/static/src/js/message/message_action_list.js',
        },
        'web.assets_common': {
            'thiqah_base/static/libs/bootstrap-select/bootstrap-select.min.css',
            'thiqah_base/static/libs/bootstrap-select/bootstrap-select.min.js',
            'thiqah_base/static/src/js/utils.js',
        },
        'web.assets_qweb': {
            'thiqah_base/static/src/xml/navbar/systray.xml',
        },
        # 'web.report_assets_common': [
        #     'thiqah_base/static/src/scss/report.scss',
        # ],
    },
    'license': 'OEEL-1',
}
