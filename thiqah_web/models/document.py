# -*- coding: utf-8 -*-

import base64
from odoo.tools.mimetypes import guess_mimetype
from odoo import models, fields, api, _, tools
from odoo.exceptions import AccessError, UserError
from collections import defaultdict


import logging
_logger = logging.getLogger(__name__)


class Document(models.Model):
    _inherit = 'documents.document'

    def check_name_files(self, filename):
        _logger.info('check_name_files filename %s', filename)
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        if filename and '.' in filename:
            extension = filename.split('.')
            # _logger.info('check_name_files extension %s', extension)
            if len(extension) > 2:
                raise UserError(_("Double Extension File Type Not supported!"))
            if extension[1] and extension[1] not in list_supported_type and binary_supported_types != '*':
                raise UserError(_("Extension File Type Not supported!"))
        return True

    def check_magic_number_files(self, datas):
        # _logger.info('check_magic_number_files datas %s', datas)
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        raw = base64.b64decode(datas)
        if raw:
            mimetype = guess_mimetype(raw)
            _logger.info('check_magic_number_files mimetype %s', mimetype)
            if mimetype and mimetype not in list_supported_type and binary_supported_types != '*':
                raise UserError(_("Magic Number File Not supported!"))
        return True

    def check_extension_files(self, mimetype):
        _logger.info('check_extension_files mimetype %s', mimetype)
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        if mimetype and mimetype not in list_supported_type and binary_supported_types != '*':
            raise UserError(_("Extension File Type Not supported!"))
        return True

    # def check_size_files(self,datas):
    #     IrConfigSudo = self.env['ir.config_parameter'].sudo()
    #     max_file_upload_size = int(IrConfigSudo.get_param('web.max_file_upload_size'))
    #     file_size=len(datas)/(1024 * 1024)
    #     if file_size and max_file_upload_size and file_size > max_file_upload_size:
    #         raise UserError(_("The selected file exceed the maximum file size!"))
    #     return True

    @api.model
    def create(self, vals):
        _logger.info('create vals %s', vals)
        try:
            if 'mimetype' in vals and vals['mimetype']:
                self.check_extension_files(vals['mimetype'])
            # if 'datas' in vals and vals['datas']:
                # self.check_size_files(str(vals['datas']))
#               self.check_magic_number_files(str(vals['datas']))
            if 'name' in vals and vals['name']:
                self.check_name_files(vals['name'])
        except Exception as e:
            _logger.error(
                'exception error for check extension/size document %s', e)
            raise UserError(e)
        return super().create(vals)

    def write(self, vals):
        _logger.info('write vals %s', vals)
        try:
            if 'mimetype' in vals and vals['mimetype']:
                self.check_extension_files(vals['mimetype'])
            # if 'datas' in vals and vals['datas']:
                # self.check_size_files(vals['datas'])
                # self.check_magic_number_files(vals['datas'])
            if 'name' in vals and vals['name']:
                self.check_name_files(vals['name'])
        except Exception as e:
            _logger.error(
                'exception error for check extension/size document %s', e)
            raise UserError(e)
        return super(Document, self).write(vals)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def check_name_files(self, filename):
        _logger.info('check_name_files filename %s', filename)
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        if filename and '.' in filename:
            extension = filename.split('.')
            _logger.info('check_name_files extension %s', extension)
            if len(extension) > 2:
                raise UserError(_("Double Extension File Type Not supported!"))
            if extension[1] and extension[1] not in list_supported_type and binary_supported_types != '*':
                raise UserError(_("Extension File Type Not supported!"))
        return True

    def check_magic_number_files(self, datas):
        _logger.info('check_magic_number_files datas %s', datas)
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        raw = base64.b64decode(datas)
        if raw:
            mimetype = guess_mimetype(raw)
            _logger.info('check_magic_number_files mimetype %s', mimetype)
            if mimetype and mimetype not in list_supported_type and binary_supported_types != '*':
                raise UserError(_("Magic Number File Not supported!"))
        return True

    def check_extension_files(self, mimetype):
        _logger.info('check_extension_files mimetype %s', mimetype)
        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        if mimetype and mimetype not in list_supported_type and binary_supported_types != '*':
            raise UserError(_("Extension File Type Not supported!"))
        return True

    # def check_size_files(self,datas):
    #     IrConfigSudo = self.env['ir.config_parameter'].sudo()
    #     max_file_upload_size = int(IrConfigSudo.get_param('web.max_file_upload_size'))
    #     file_size=len(datas)/(1024 * 1024)
    #     if file_size and max_file_upload_size and file_size > max_file_upload_size:
    #         raise UserError(_("The selected file exceed the maximum file size!"))
    #     return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _logger.info('create IrAttachment vals %s', vals)
            try:
                if 'mimetype' in vals and vals['mimetype'] and (('res_model' in vals and vals['res_model'] != 'ir.ui.view') or 'res_model' not in vals):
                    self.check_extension_files(vals['mimetype'])
                # if 'datas' in vals and vals['datas'] and (('res_model' in vals and vals['res_model'] != 'ir.ui.view') or 'res_model' not in vals):
                    # self.check_size_files(vals['datas'])
#                     self.check_magic_number_files(vals['datas'])
                if 'name' in vals and vals['name'] and (('res_model' in vals and vals['res_model'] != 'ir.ui.view') or 'res_model' not in vals):
                    self.check_name_files(vals['name'])

            except Exception as e:
                _logger.error(
                    'exception error for check extension/size attachment %s', e)
                raise UserError(e)
        return super(IrAttachment, self).create(vals_list)

    def write(self, vals):
        _logger.info('write IrAttachment vals %s', vals)
        try:
            res_model = self.res_model if 'res_model' not in vals else vals['res_model']
            if 'mimetype' in vals and vals['mimetype'] and ((res_model and res_model != 'ir.ui.view') or not res_model):
                self.check_extension_files(vals['mimetype'])
            # if 'datas' in vals and vals['datas'] and ((res_model and res_model != 'ir.ui.view') or not res_model):
                # self.check_size_files(vals['datas'])
#                 self.check_magic_number_files(vals['datas'])
            if 'name' in vals and vals['name'] and ((res_model and res_model != 'ir.ui.view') or not res_model):
                self.check_name_files(vals['name'])
        except Exception as e:
            _logger.error(
                'exception error for check extension/size attachment %s', e)
            raise UserError(e)
        return super(IrAttachment, self).write(vals)

  