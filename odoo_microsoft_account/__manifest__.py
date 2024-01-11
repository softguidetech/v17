# See LICENSE file for full copyright and licensing details.
{
    'name': 'Microsoft Azure - Odoo SSO Integration',
    'version': '17.0',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'depends': ['auth_oauth'],
    'data': [
        'views/res_config.xml',
        'views/oauth_provider.xml',
        'data/auth_oauth_data.xml',
    ],
    'external_dependencies': {'python': ['simplejson']},
    'installable': True,
    'auto_install': False,
}
