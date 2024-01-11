# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main
from odoo.addons.web.controllers.main import ensure_db
from odoo.exceptions import AccessError
import traceback
from odoo.tools import ustr


from odoo.http import serialize_exception


def serialize_exception_patched(e):
    return {
        "name": 'Exception',
        # "name": type(e).__module__ + "." + type(e).__name__ if type(e).__module__ else type(e).__name__,
        "debug": 'Odoo Server Error',
        # "debug": traceback.format_exc(),
        # "message": ustr(e),
        "message": 'Odoo Server Error',
        "arguments": '',
        # "arguments": e.args,
        # "context": getattr(e, 'context', {}),
        "context": '',
    }

# Monkey Patch
serialize_exception = serialize_exception_patched

# class HomeExtension(main.Home):

#     def web_client(self, s_action=None, **kw):
#         ensure_db()
#         if not request.session.uid:
#             return request.redirect('/web/login', 303)
#         if kw.get('redirect'):
#             return request.redirect(kw.get('redirect'), 303)

#         request.uid = request.session.uid
#         try:
#             context = request.env['ir.http'].webclient_rendering_context()
#             response = request.render(
#                 'web.webclient_bootstrap', qcontext=context)
#             response.headers['X-Frame-Options'] = 'DENY'
#             return response
#         except AccessError:
#             return request.redirect('/web/login?error=access')
