# -*- coding: utf-8 -*-
# import base64
# import json
# import logging

# from odoo.http import request
from odoo import http
# import unicodedata

# from odoo.tools import pycompat
# from odoo.addons.web.controllers.main import CSVExport, Binary, serialize_exception, _serialize_exception, clean
from odoo.addons.web.controllers.export import CSVExport
from odoo.addons.web.controllers.binary import Binary
import json
import werkzeug
import functools
import logging

_logger = logging.getLogger(__name__)


def serialize_exception_patched(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            _logger.exception("An exception occurred during an http request")
            # se = _serialize_exception(e)
            se =  http.serialize_exception(e)
            error = {
                # 'code': 200,
                'message': "Odoo Server Error",
                # 'data': se
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))
    return wrap


# Monkey Patch
serialize_exception = serialize_exception_patched


class CSVExportInherit(CSVExport):

    @http.route('/web/export/csv', type='http', auth="user")
    # @serialize_exception
    def index(self, data):
        return self.base(data)


# class BinaryInherit(Binary):

#     @http.route('/web/binary/upload', type='http', auth="user")
#     # @serialize_exception
#     def upload(self, ufile, callback=None):
#         # TODO: might be useful to have a configuration flag for max-length file uploads
#         out = """<script language="javascript" type="text/javascript">
#                     var win = window.top.window;
#                     win.jQuery(win).trigger(%s, %s);
#                 </script>"""
#         try:
#             data = ufile.read()
#             args = [len(data), ufile.filename,
#                     ufile.content_type, pycompat.to_text(base64.b64encode(data))]
#         except Exception as e:
#             args = [False, str(e)]
#         return out % (json.dumps(clean(callback)), json.dumps(args)) if callback else json.dumps(args)

#     @http.route('/web/binary/upload_attachment', type='http', auth="user")
#     # @serialize_exception
#     def upload_attachment(self, model, id, ufile, callback=None):
#         files = request.httprequest.files.getlist('ufile')
#         Model = request.env['ir.attachment']
#         out = """<script language="javascript" type="text/javascript">
#                     var win = window.top.window;
#                     win.jQuery(win).trigger(%s, %s);
#                 </script>"""
#         args = []
#         for ufile in files:

#             filename = ufile.filename
#             if request.httprequest.user_agent.browser == 'safari':
#                 # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
#                 # we need to send it the same stuff, otherwise it'll fail
#                 filename = unicodedata.normalize('NFD', ufile.filename)

#             try:
#                 attachment = Model.create({
#                     'name': filename,
#                     'datas': base64.encodebytes(ufile.read()),
#                     'res_model': model,
#                     'res_id': int(id)
#                 })
#                 attachment._post_add_create()
#             except Exception:
#                 args.append({'error': _("Something horrible happened")})
#                 _logger.exception(
#                     "Fail to upload attachment %s" % ufile.filename)
#             else:
#                 args.append({
#                     'filename': clean(filename),
#                     'mimetype': ufile.content_type,
#                     'id': attachment.id,
#                     'size': attachment.file_size
#                 })
#         return out % (json.dumps(clean(callback)), json.dumps(args)) if callback else json.dumps(args)


