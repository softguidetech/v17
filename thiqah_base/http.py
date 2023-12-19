from odoo.http import WebRequest, Response, JsonRequest, SessionExpiredException, AuthenticationError, serialize_exception
from odoo.service import model as service_model
from odoo.tools import ustr

import odoo
import traceback

import werkzeug.exceptions

import logging
_logger = logging.getLogger(__name__)


def serialize_exception_patched(e):
    return {
        "name": 'Error',
        "debug": '',
        "message": '',
        "arguments": '',
        "context": '',
    }


serialize_exception = serialize_exception_patched


def _call_function_patched(self, *args, **kwargs):
    request = self
    if self.endpoint.routing['type'] != self._request_type:
        msg = "%s, %s: Function declared as capable of handling request of type '%s' but called with a request of type '%s'"
        params = (self.endpoint.original, self.httprequest.path,
                  self.endpoint.routing['type'], self._request_type)
        _logger.info(msg, *params)
        # Change : Neutralize this exception trigger from the werkzeug
        raise werkzeug.exceptions.BadRequest(msg % params)

    if self.endpoint_arguments:
        kwargs.update(self.endpoint_arguments)

    # Backward for 7.0
    if self.endpoint.first_arg_is_req:
        args = (request,) + args

    first_time = True

    # Correct exception handling and concurrency retry
    @service_model.check
    def checked_call(___dbname, *a, **kw):
        nonlocal first_time
        # The decorator can call us more than once if there is an database error. In this
        # case, the request cursor is unusable. Rollback transaction to create a new one.
        if self._cr and not first_time:
            self._cr.rollback()
            self.env.clear()
        first_time = False
        result = self.endpoint(*a, **kw)
        if isinstance(result, Response) and result.is_qweb:
            # Early rendering of lazy responses to benefit from @service_model.check protection
            result.flatten()
        if self._cr is not None:
            # flush here to avoid triggering a serialization error outside
            # of this context, which would not retry the call
            self._cr.flush()
        return result

    if self.db:
        return checked_call(self.db, *args, **kwargs)
    return self.endpoint(*args, **kwargs)


WebRequest._call_function = _call_function_patched


# class WebRequestExtension(WebRequest):


def _handle_exception_patched(self, exception):
    """Called within an except block to allow converting exceptions
       to arbitrary responses. Anything returned (except None) will
       be used as response."""
    try:
        return super(JsonRequest, self)._handle_exception(exception)
    except Exception:
        if not isinstance(exception, SessionExpiredException):
            if exception.args and exception.args[0] == "bus.Bus not available in test mode":
                _logger.info(exception)
            elif isinstance(exception, (odoo.exceptions.UserError,
                                        werkzeug.exceptions.NotFound)):
                _logger.warning(exception)
            else:
                _logger.exception(
                    "Exception during JSON request handling.")
        error = {
            'code': 200,
            'message': "Odoo Server Error",
            'data': 'Exception',
            # 'data': serialize_exception(exception),
        }
        if isinstance(exception, werkzeug.exceptions.NotFound):
            error['http_status'] = 404
            error['code'] = 404
            error['message'] = "404: Not Found"
        if isinstance(exception, AuthenticationError):
            error['code'] = 100
            error['message'] = "Odoo Session Invalid"
        if isinstance(exception, SessionExpiredException):
            error['code'] = 100
            error['message'] = "Odoo Session Expired"
        return self._json_response(error=error)


# JsonRequest._handle_exception =_handle_exception_patched
