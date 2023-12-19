# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_title = fields.Char(
        related='company_id.company_title',
        readonly=False
    )

    theme_background_image = fields.Binary(
        related='company_id.background_image',
        readonly=False
    )
    theme_color_brand = fields.Char(
        string='Theme Brand Color'
    )

    theme_color_primary = fields.Char(
        string='Theme Primary Color'
    )

    theme_color_required = fields.Char(
        string='Theme Required Color'
    )

    theme_color_menu = fields.Char(
        string='Theme Menu Color'
    )

    theme_color_appbar_color = fields.Char(
        string='Theme AppBar Color'
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()

        if self.env.user.company_id.background_image:
            img_url = 'url(/web/image/res.company/%s/background_image);' % (
                self.env.user.company_id.id)
        else:
            img_url = 'url(/thiqah_dynamic_web_theme/static/img/background.png);'

        variables = [
            {'name': 'o-brand-odoo', 'value': self.theme_color_brand or "#243742"},
            {'name': 'o-brand-primary', 'value': self.theme_color_primary or "#5D8DA8"},
            {'name': 'mk-required-color',
                'value': self.theme_color_required or "#d1dfe6"},
            {'name': 'mk-apps-color', 'value': self.theme_color_menu or "#f8f9fa"},
            {'name': 'mk-appbar-color',
                'value': self.theme_color_appbar_color or "#dee2e6"},
            {'name': 'mk-background-image', 'value': img_url},
        ]

        self.env['web_editor.assets'].replace_variables_values(
            '/thiqah_dynamic_web_theme/static/src/scss/colors.scss', 'web._assets_primary_variables', variables
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        variables = [
            'o-brand-odoo',
            'o-brand-primary',
            'mk-required-color',
            'mk-apps-color',
            'mk-appbar-color',
        ]
        colors = self.env['web_editor.assets'].get_variables_values(
            '/thiqah_dynamic_web_theme/static/src/scss/colors.scss', 'web._assets_primary_variables', variables
        )

        res.update({
            'theme_color_brand': colors['o-brand-odoo'],
            'theme_color_primary': colors['o-brand-primary'],
            'theme_color_required': colors['mk-required-color'],
            'theme_color_menu': colors['mk-apps-color'],
            'theme_color_appbar_color': colors['mk-appbar-color'],
        })
        return res
