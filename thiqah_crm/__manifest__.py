# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH CRM',
    'category': 'Sales/CRM',
    'sequence': 2,
    'version': '1.0',
    'summary': 'Thiqah Custom CRM',
    'author': 'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': [
        'web', 'web_domain_field', 'base', 'crm', 'product', 'helpdesk', 'mail', 'project', 'utm', ],
    'data': [

        'security/security.xml',
        'security/aahd_crm_security.xml',
        'security/bd_crm_security.xml',
        'security/ir.model.access.csv',

        # for Legal Team
        'views/legal_action.xml',
        'views/contract.xml',

        'data/client_satus_data.xml',
        'data/email_template.xml',
        'data/opportunity_channel_data.xml',
        'data/crm_stage_data.xml',
        'data/ir_cron_data.xml',
        'data/customer_sequence_code.xml',
        'data/lead_source.xml',
        'data/thiqah_crm_tag.xml',

        'views/res_partner_views.xml',
        'views/res_users.xml',
        'views/client_status_views.xml',
        'views/opportunity_channel_views.xml',
        'views/product_views.xml',
        'views/crm_stage_views.xml',
        'views/thiqah_crm_stage_views.xml',
        'views/thiqah_crm_tag_views.xml',
        'views/crm_lead_views.xml',
        'views/aahd_crm_lead_views.xml',
        'views/bd_crm_lead_views.xml',
        'views/opp_size_views.xml',
        'views/sp_manager_views.xml',
        'views/res_stackeholder_views.xml',
        'views/lead_source_views.xml',
        'views/internal_status_views.xml',
        'views/helpdesk_views.xml',
        'views/portfolio_category_views.xml',
        'views/portfolio_category_views.xml',

        'views/crm_dashboard_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/crm_lead_to_opportunity_views.xml',
        'views/crm_team_views.xml',

        'report/thiqah_crm_ontime_view.xml',
        'report/thiqah_crm_view.xml',
        'report/thiqah_awarded_opportunities_template.xml',
        'report/thiqah_submitted_opportunities_template.xml',
        'report/thiqah_potential_opportunities_template.xml',
        'report/thiqah_opportunities_report.xml',
        'report/thiqah_tickets_on_time_report.xml',
        'views/menu_dashboard_view.xml',
        'views/crm_lead_event.xml',
        'views/crm_menu_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            # 'thiqah_portal/static/src/scss/variables.scss',
            # 'thiqah_portal/static/src/scss/service_requests_dashboard.scss',
            # 'thiqah_portal/static/src/scss/style.scss',
            # 'thiqah_portal/static/src/scss/responsive.scss',
            # 'thiqah_crm/static/src/css/style.scss',
            # 'thiqah_crm/static/src/scss/thiqah_legal_dashboard.scss',
            # 'thiqah_crm/static/src/scss/bd_dashboard.scss',
            # 'thiqah_crm/static/src/scss/aahd_dashbaord.scss',
            # 'thiqah_crm/static/src/scss/style_dash.scss',
            # 'thiqah_crm/static/src/js/dynamic_dashboard.js',
            # 'thiqah_crm/static/src/js/all_data_dashboard.js',
            # # 'thiqah_crm/static/src/js/libs/chartjs-plugin-datalabels.min.js',
            # 'thiqah_crm/static/src/js/crm_edit.js',
            # 'thiqah_crm/static/src/js/folower_customer.js',
            # 'thiqah_crm/static/src/js/legal_dashboard.js',
            # 'thiqah_crm/static/src/js/bd_dashboard.js',
            # 'thiqah_crm/static/src/js/aahd_sales_dashboard.js',

            # 'thiqah_crm/static/src/js/navbar/systray.js',
            # 'thiqah_crm/static/src/css/navbar/systray.css',

            # Core Patch
            # 'thiqah_crm/static/src/js/core_kanban_patch.js',




        ],
        'web.report_assets_common': [
            'thiqah_crm/static/src/scss/style_report.scss',
        ],
        #         'mail.assets_discuss_public': [
        #             'thiqah_crm/static/src/xml/composer.xml',
        #         ],
        'web.assets_qweb': [
            'thiqah_crm/static/src/xml/navbar/systray.xml',
            'thiqah_crm/static/src/xml/crm_dashboard_templates.xml',
            'thiqah_crm/static/src/xml/crm_dashboard_templates_all.xml',
            'thiqah_crm/static/src/xml/composer.xml',
            'thiqah_crm/static/src/xml/legal_dashboard.xml',
            'thiqah_crm/static/src/xml/bd_dashboard.xml',
            'thiqah_crm/static/src/xml/aahd_sales_dashboard.xml',


        ],

    },
    'bootstrap': True,
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}
