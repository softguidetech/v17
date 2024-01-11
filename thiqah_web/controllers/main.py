# -*- coding: utf-8 -*-

from odoo.tools.mimetypes import guess_mimetype
import base64
import zipfile
import io
import json
import logging
import os
from contextlib import ExitStack

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request, content_disposition
from odoo.tools.translate import _
from odoo.tools import image_process
from odoo.addons.documents.controllers.documents import ShareRoute
from odoo.exceptions import UserError
logger = logging.getLogger(__name__)


class ShareRoute(ShareRoute):

    # Download & upload routes #####################################################################
    def check_name_files(self, filename):
        logger.info('check_name_files ShareRoute filename %s', filename)
        IrConfigSudo = request.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        if filename and '.' in filename:
            extension = filename.split('.')
            logger.info('check_name_files ShareRoute extension %s', extension)
            if len(extension) > 2:
                raise UserError(_("Double Extension File Type Not supported!"))
            if extension[1] and extension[1] not in list_supported_type and binary_supported_types != '*':
                raise UserError(_("Extension File Type Not supported!"))
        return True

    def check_extension_files(self, mimetype):
        logger.info('check_extension_files ShareRoute mimetype %s', mimetype)
        IrConfigSudo = request.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        if mimetype and mimetype not in list_supported_type and binary_supported_types != '*':
            raise UserError(_("Extension File Type Not supported!"))
        return True

    def check_magic_number_files(self, datas):
        logger.info('check_magic_number_files ShareRoute datas %s', datas)
        IrConfigSudo = request.env['ir.config_parameter'].sudo()
        binary_supported_types = IrConfigSudo.get_param(
            'web.binary_supported_types')
        list_supported_type = []
        for suppr_file in binary_supported_types.split(','):
            list_supported_type.append(suppr_file)
        raw = base64.b64decode(datas)
        if raw:
            mimetype = guess_mimetype(raw)
            logger.info('check_magic_number_files mimetype %s', mimetype)
            if mimetype and mimetype not in list_supported_type and binary_supported_types != '*':
                raise UserError(_("Magic Number File Not supported!"))
        return True

    @http.route('/documents/upload_attachment', type='http', methods=['POST'], auth="user")
    def upload_document(self, folder_id, ufile, tag_ids, document_id=False, partner_id=False, owner_id=False):
        files = request.httprequest.files.getlist('ufile')
        result = {'success': _("All files uploaded")}
        tag_ids = tag_ids.split(',') if tag_ids else []
        if document_id:
            document = request.env['documents.document'].browse(
                int(document_id))
            ufile = files[0]
            try:

                data = base64.encodebytes(ufile.read())
                mimetype = ufile.content_type
                self.check_magic_number_files(data)
                self.check_name_files(mimetype)
                document.write({
                    'name': ufile.filename,
                    'datas': data,
                    'mimetype': mimetype,
                })
            except Exception as e:
                logger.exception("Fail to upload document %s" % ufile.filename)
                result = {'error': str(e)}
        else:
            vals_list = []
            for ufile in files:
                try:
                    mimetype = ufile.content_type
                    datas = base64.encodebytes(ufile.read())
                    self.check_magic_number_files(datas)
                    self.check_name_files(mimetype)
                    vals = {
                        'name': ufile.filename,
                        'mimetype': mimetype,
                        'datas': datas,
                        'folder_id': int(folder_id),
                        'tag_ids': tag_ids,
                        'partner_id': int(partner_id)
                    }
                    if owner_id:
                        vals['owner_id'] = int(owner_id)
                    vals_list.append(vals)
                except Exception as e:
                    logger.exception(
                        "Fail to upload document %s" % ufile.filename)
                    result = {'error': str(e)}
            cids = request.httprequest.cookies.get(
                'cids', str(request.env.user.company_id.id))
            allowed_company_ids = [int(cid) for cid in cids.split(',')]
            documents = request.env['documents.document'].with_context(
                allowed_company_ids=allowed_company_ids).create(vals_list)
            result['ids'] = documents.ids

        return json.dumps(result)
