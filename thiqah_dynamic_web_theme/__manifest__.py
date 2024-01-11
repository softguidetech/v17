# -*- coding: utf-8 -*-
{
    'name': 'THIQAH Dynamic Backend Theme', 
    'summary': 'Odoo Backend Theme',
    'version': '17.0',
    'category': 'Themes/Backend', 
    'license': 'LGPL-3', 
    'author':'THIQAH',
    'description': "",
    'website': 'https://thiqah.sa',
    'depends': [
        'base',
        'web_editor',
        'mail',
        'web',
    ],
    
    'data': [
       'views/res_config_settings_view.xml',
       'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_qweb': [
        ],
        'web._assets_primary_variables': [
            'thiqah_dynamic_web_theme/static/src/scss/colors.scss',
        ],
        'web._assets_backend_helpers': [
            'thiqah_dynamic_web_theme/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'thiqah_dynamic_web_theme/static/src/scss/webclient/**/*.scss',
           'thiqah_dynamic_web_theme/static/src/scss/legacy/fields.scss',
           'thiqah_dynamic_web_theme/static/src/scss/legacy/settings_view.scss',
            # 'thiqah_dynamic_web_theme/static/src/js/app_title.js',
	        'thiqah_dynamic_web_theme/static/src/scss/*.scss',
        ],
         'web.assets_frontend': [
         
        ],
        'web._assets_common_styles': [
           'thiqah_dynamic_web_theme/static/src/scss/legacy/ui.scss',
        ],
    },
    'images': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': '_uninstall_reset_changes',
}
