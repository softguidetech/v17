# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'THIQAH Theme',
    'category': 'Web',
    'version': '1.0',
    'sequence': 2,
    'description': """
        This module update odoo theme.""",
    'depends': ['base', 'web'],
    'author': 'THIQAH',
    'website': 'https://thiqah.sa',
    'data': [

    ],
    'assets': {
        'web._assets_primary_variables': [
            'thiqah_theme/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'thiqah_theme/static/src/fonts/fonts.scss',
        ],
        'web.assets_backend': [
            'thiqah_theme/static/src/scss/ui.scss',
            # 'thiqah_theme/static/src/scss/style.scss',
            # 'thiqah_theme/static/src/js/app_title.js',
        ],
    },
    'bootstrap': True,  # load translations for login screen,
    'license': 'LGPL-3',
}
