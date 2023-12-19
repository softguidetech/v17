# -*- coding: utf-8 -*-
{
    'name': "thiqah_portal",

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

    # any module necessary for this one to work correctly
    'depends': ['web', 'website', 'portal', 'thiqah_project', 'thiqah_workflow', 'auth_oauth'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/requiring_action.xml',
        'data/website_page.xml',
        'views/ir_actions_client.xml',
        'views/ir_ui_menu.xml',
        'views/fields_forms.xml',
        'views/loader.xml',
        'views/portal_template.xml',
        'views/portal_layout.xml',
        'views/portal_request_page.xml',
        'views/dashboard.xml',
        'views/portal_user_views.xml',
        'views/financial_dashboard.xml',
        'views/department_dashboard.xml',
        'views/customer_centricity.xml',
        'views/generate_lead.xml',
        'views/utilization_report_dashboard_template.xml',
        'views/access_denied_template.xml',
        'views/candidate_client_template.xml',
    ],
    'assets': {
         'web.assets_common': [
            'thiqah_portal/static/src/lib/Datatables/dataTables.css',
            'thiqah_portal/static/src/lib/Datatables/dataTables.js',
        ],
        'web.assets_frontend': [
            'thiqah_portal/static/src/lib/table2excel.min.js',
            'thiqah_portal/static/src/lib/bootstrap-datepicker/bootstrap-datepicker.min.js',
            'thiqah_portal/static/src/lib/bootstrap-datepicker/bootstrap-datepicker.min.css',
            'thiqah_portal/static/src/js/dataTables.js',
            'thiqah_portal/static/src/js/service_request.js',
            'thiqah_portal/static/src/js/utilization_report.js',
            'thiqah_portal/static/src/js/request_portal_sidebar.js',
            'thiqah_portal/static/src/js/chart_custom.js',
            'thiqah_portal/static/src/js/chatter.js',
            'thiqah_portal/static/src/js/signup.js',
            'thiqah_portal/static/src/js/department_dashboard.js',
            'thiqah_portal/static/src/js/dashboard_user_class.js',
            'thiqah_portal/static/src/js/dashboard_layout.js',
            'thiqah_portal/static/src/js/customer_centricity.js',
            'thiqah_portal/static/src/scss/loader.scss',
            
            # 'thiqah_portal/static/src/scss/variables.scss',
            'thiqah_portal/static/src/scss/dashboard_user.scss',
            'thiqah_portal/static/src/scss/customer_centricity.scss',
            'thiqah_portal/static/src/scss/aahd_generate_lead.scss',
            'thiqah_portal/static/src/scss/dashboard_layout.scss',
            'thiqah_portal/static/src/scss/service_requests_dashboard.scss',
            'thiqah_portal/static/src/scss/department_task_dashboard.scss',
            'thiqah_portal/static/src/scss/style.scss',
            'thiqah_portal/static/src/scss/responsive.scss',
            'thiqah_portal/static/src/scss/rtl.scss',
            'thiqah_portal/static/src/scss/style.css',
        ],
        'web.assets_backend': [
            'thiqah_portal/static/src/scss/variables.scss',
        ],
        # 'web.assets_qweb': [
        #     'thiqah_portal/static/src/xml/chatter.xml',
        # ],
       
    },
    'license': 'OEEL-1',
}
