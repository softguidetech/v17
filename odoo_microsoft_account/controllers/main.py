# -*- coding: utf-8 -*-

import logging
import json
import odoo
import http.client as httplib
import simplejson
import werkzeug.utils
from odoo import http
from odoo.http import request
from odoo.addons.auth_oauth.controllers.main import OAuthLogin as Home

from odoo.addons.auth_oauth.controllers.main import\
    fragment_to_query_string
# from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url
from odoo.exceptions import AccessDenied
import werkzeug.urls
_logger = logging.getLogger(__name__)


class OAuthLogin(Home):

    def list_providers(self):
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read(
                [('enabled', '=', True)])
        except Exception:
            providers = []
        provider_microsoft = request.env.ref(
            'odoo_microsoft_account.provider_microsoft')
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        for provider in providers:
            if provider.get('id') == provider_microsoft.id:
                return_url = base_url + '/auth_oauth/microsoft/signin'
                params = dict(
                    client_id=provider['client_id'],
                    response_type='code',
                    redirect_uri=return_url,
                    prompt='select_account',
                    scope=provider['scope'],
                )
            else:
                return_url = base_url + '/auth_oauth/signin'
                state = self.get_state(provider)
                params = dict(
                    response_type='token',
                    client_id=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state=json.dumps(state),
                )
            provider['auth_link'] = "%s?%s" % (
                provider['auth_endpoint'], werkzeug.urls.url_encode(params))

        return providers


class OAuthController(http.Controller):

    #     def check_session_logged_in(self,provider, params):
    #         _logger.info('check_session_logged_in fct')
    # #         user = request.env(user=user_id)['res.users'].browse(user_id)
    #         oauth_uid = params['user_id']
    #         users = request.env['res.users'].sudo().search([
    #             ("oauth_uid", "=", oauth_uid),
    #             ('oauth_provider_id', '=', provider)
    #         ], limit=1)
    #         if not users:
    #             users = request.env['res.users'].sudo().search([
    #                 ("login", "=", params.get('email'))
    #             ], limit=1)
    #         if not users:
    #             raise AccessDenied()
    #         #assert len(users.ids) == 1
    #
    #
    #         _logger.debug('Authentication method: ThiqahHome.credentials ! %s %s %s',users,users.sid,users.logged_in)
    #         if users.sid and users.logged_in:
    #             _logger.info('user.logged_in %s',users.logged_in)
    #             _logger.warning("User %s is already logged in "
    #                             "into the system!. Multiple "
    #                             "sessions are not allowed for "
    #                             "security reasons!" % users.name)
    #             request.uid = users.id
    # #             raise AccessDenied("already_logged_in")
    #             url = "/web/login?oauth_error=4"
    #             redirect = werkzeug.utils.redirect(url, 303)
    #             redirect.autocorrect_location_header = False
    #             return redirect
    #         return True

    @http.route('/auth_oauth/microsoft/signin',
                type='http',
                auth='none',
                csrf=False)
    @fragment_to_query_string
    def microsoft_signin(self, **kw):
        pool = request.env
        _logger.info('microsoft_signinmicrosoft_signin')
        root_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + '/'
        oauth_provider_rec = request.env.ref(
            'odoo_microsoft_account.provider_microsoft').id
#         \pool['ir.model.data'].sudo().get_object_reference(
#                 'odoo_microsoft_account',
#                 'provider_microsoft')[1]
        provider = request.env.ref('odoo_microsoft_account.provider_microsoft')
#         \
#             pool['auth.oauth.provider'].sudo().browse(oauth_provider_rec)
        authorization_data = \
            pool['auth.oauth.provider'].sudo().oauth_token(
                'authorization_code',
                provider.sudo(),
                kw.get('code'),
                refresh_token=None)
        access_token = authorization_data.get('access_token')
        refresh_token = authorization_data.get('refresh_token')
        try:
            conn = httplib.HTTPSConnection(provider.data_endpoint)
            conn.request("GET", "/v1.0/me", "", {
                'Authorization': access_token,
                'Accept': 'application/json'
            })
            response = conn.getresponse()
            data = simplejson.loads(response.read())
            displayName = data.get('displayName')
            mail = data.get('userPrincipalName')
            user_id = data.get('id')
            conn.close()
        except Exception as e:
            _logger.info('microsoft_signinmicrosoft_signin e', e)
        try:
            _logger.info('microsoft_signinmicrosoft_signin tryyyy')
            credentials = pool['res.users'].sudo().microsoft_auth_oauth(
                provider.id, {
                    'access_token': access_token,
                    'user_id': user_id,
                    'email': mail,
                    'name': displayName,
                    'microsoft_refresh_token': refresh_token
                })
            request.cr.commit()

#             _logger.info('microsoft_signinmicrosoft_signin check_session_logged_in')
#             self.check_session_logged_in(provider.id, {
#                     'access_token': access_token,
#                     'user_id': user_id,
#                     'email': mail,
#                     'name': displayName,
#                     'microsoft_refresh_token': refresh_token
#                 })

            redirect_url = root_url + 'web?'
            # if redirect_url:
            # Inject in the Auditlog to trace the login action(s).
            # Just create a new record auditlog.login

            traceability_values = {
                'user_id': request.env.user.id,
                # 'user_id': user_id,
                'redirect_to': redirect_url,
                # 'user_category_id': request.env['res.users'].sudo().browse([int(user_id)]).thiqah_category_id if request.env['res.users'].sudo().browse([int(user_id)]) else 0
                # 'user_category_id': request.env.user.thiqah_category_id if request.env.user.thiqah_category_id else 0
            }

            request.env['auditlog.login'].sudo().create(
                traceability_values)
            # pre_uid = request.session.authenticate(dbname, login, key)
            # resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303)
            # resp.autocorrect_location_header = False

            # return login_and_redirect(*credentials,
            #                           redirect_url=root_url + 'web?')
            return _get_login_redirect_url(*credentials,
                                      redirect_url=root_url + 'web?')

        except AttributeError:
            _logger.error(
                "auth_signup not installed on"
                " database %s: oauth sign up cancelled." % (
                    request.cr.dbname))
            url = "/web/login?oauth_error=1"
        except odoo.exceptions.AccessDenied as e:
            _logger.info('AccessDenied as error e %s', e)
            _logger.info('AccessDenied as odoo.exceptions.AccessDenied().args %s',
                         odoo.exceptions.AccessDenied().args)
#             if e == "already_logged_in":
#                 url = "/web/login?oauth_error=4"
#
#             else:
            _logger.info(
                'OAuth2:test access denied,'
                ' redirect to main page in case a valid'
                ' session exists, without setting cookies')
            url = "/web/login?oauth_error=3"
            redirect = werkzeug.utils.redirect(url, 303)
            redirect.autocorrect_location_header = False

            return redirect
        except Exception as e:
            _logger.exception("OAuth2: %s" % str(e))
            url = "/web/login?oauth_error=2"
        # return set_cookie_and_redirect(root_url + url)
        return _get_login_redirect_url(root_url + url)
