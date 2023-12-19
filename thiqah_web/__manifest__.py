

{
    "name": "THIQAH Web",
    "category": "Extra Tools",
    'author': 'THIQAH',
    'description': "allowed  maximum attachment size and supported types",
    'website': 'https://thiqah.sa',

    "depends": [
        'documents', 'web', 'mail', 'base'
    ],
    "data": [
        "views/login.xml",
        "views/res_config_settings_view.xml",

    ],

    'assets': {
        'web.assets_qweb': [
            'thiqah_web/static/src/xml/*.xml',

        ],
        'web.assets_backend': [
            # 'thiqah_web/static/src/js/*/*.js',
            # 'thiqah_web/static/src/js/file_upload_mixin.js',
            # 'thiqah_web/static/src/js/kanban/*.js',
        ],



    },

    "application": False,
    "installable": True,
    'auto_install': False,
    'license': 'OEEL-1',
}
