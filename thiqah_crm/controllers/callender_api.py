from odoo import http,  _
from odoo.http import request
from decimal import *
from odoo.osv.expression import AND
from odoo.exceptions import AccessError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from ...thiqah_base.controllers import thiqah_portal
import json
import ast
import pandas as pd
from datetime import datetime
import os
import msal
import requests
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
def generate_access_token(app_id, scopes):
    # Save Session Token as a token file
    access_token_cache = msal.SerializableTokenCache()

    # read the token file
    if os.path.exists('ms_graph_api_token.json'):
        access_token_cache.deserialize(open("ms_graph_api_token.json", "r").read())
        token_detail = json.load(open('ms_graph_api_token.json',))
        token_detail_key = list(token_detail['AccessToken'].keys())[0]
        token_expiration = datetime.fromtimestamp(int(token_detail['AccessToken'][token_detail_key]['expires_on']))
        if datetime.now() > token_expiration:
            os.remove('ms_graph_api_token.json')
            access_token_cache = msal.SerializableTokenCache()

    # assign a SerializableTokenCache object to the client instance
    client = msal.PublicClientApplication(client_id=app_id, token_cache=access_token_cache)

    accounts = client.get_accounts()
    if accounts:
        # load the session
        token_response = client.acquire_token_silent(scopes, accounts[0])
    else:
        # authetnicate your accoutn as usual
        flow = client.initiate_device_flow(scopes=scopes)
        
        # webbrowser.open('https://microsoft.com/devicelogin')
        token_response = client.acquire_token_by_device_flow("{'user_code': 'CC8SXL7EN', 'device_code': 'CAQABAAEAAAD--DLA3VO7QrddgJg7WevrK85b3aSVm8A7clSfwQd1MbHy2Uxc1tShPFbeUbWRRv5jWM4rrF70pD-LHMkljPBjcomzE8O0zK-kkBwbtrzzYBbh_WXhdjwn9YDe587k4SgwXGyFgMPLC5nhoF7alX16Wqa6V5p6BVzsMQAMROrAo9II96SkYPiN0MGxDAamrHJSr9aKfDWp1YQ9Vjf6VQhh5tKHU-JmVfLJ7cpFrORGT8Ts5qAzQvweGi6KntU6tpLLPg1WW2MYQzZrHltPpAlW9zmi8eyLVtvF06-PEXY8IU_HkxygwQMSMdVHXOl22tsLm1gTgf-yuqYQUY_Siy6kXsoDLs9ObYwwGjSUb-pUcT2BKg_kWBRo-YkYPxB2sqqo0_LdpuTCuMy5h34LVKkyIAA', 'verification_uri': 'https://microsoft.com/devicelogin', 'expires_in': 900, 'interval': 5, 'message': 'To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code CC8SXL7EN to authenticate.', 'expires_at': 1685840298.6767554, '_correlation_id': 'a6ff98cb-1c1c-432a-b64a-5b42c09b9fec'}")

    with open('ms_graph_api_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())

    return token_response
def generate_user_code(app_id, scopes):
    # Save Session Token as a token file
    access_token_cache = msal.SerializableTokenCache()
    client = msal.PublicClientApplication(client_id=app_id, token_cache=access_token_cache)
    flow = client.initiate_device_flow(scopes=scopes)
    return flow['user_code']

def construct_event_detail(event_name, **event_details):
    request_body = {
        'subject': event_name
    }
    for key, val in event_details.items():
        request_body[key] = val
    return request_body


class ThiqahCalApiController(http.Controller):
    @http.route('/add_user_code_calender_token_create', type="http", website=True,auth="user", csrf=False)
    def add_user_code_calender_token_create(self):
        APPLICATION_id = "fd0cb42e-b7ae-4c03-9ee9-11b556880048"
        CLIENT_SECRET = "bzo8Q~YE2TcCtQoaD~QwAhGXsxJFKLVGatnXsbSA"
        SCOPES = ['Calendars.ReadWrite']
        access_token_cache = msal.SerializableTokenCache()
        client = msal.PublicClientApplication(client_id=APPLICATION_id, token_cache=access_token_cache)
        flow = json.loads(request.env.user.user_outlook_code)
        token_response = client.acquire_token_by_device_flow({'user_code': flow['user_code'], 
                                                              'device_code': flow['device_code'], 
                                                              'verification_uri': 'https://microsoft.com/devicelogin', 
                                                              'expires_in': 900, 
                                                              'interval': 5, 
                                                              'message': 'To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code CE3W89EC9 to authenticate.', 
                                                              'expires_at': 1685866972.3222637,
                                                              '_correlation_id': flow['_correlation_id']}
                                                            )
        if 'access_token' in token_response:
            request.env.user.user_outlook_token = token_response['access_token']
    
    @http.route('/add_user_code_calender', type="http", website=True,auth="user", csrf=False)
    def add_user_code_calender(self):
        # APPLICATION_id = "fd0cb42e-b7ae-4c03-9ee9-11b556880048"
        # CLIENT_SECRET = "bzo8Q~YE2TcCtQoaD~QwAhGXsxJFKLVGatnXsbSA"
        # SCOPES = ['Calendars.ReadWrite']
        # access_token_cache = msal.SerializableTokenCache()
        # client = msal.PublicClientApplication(client_id=APPLICATION_id, token_cache=access_token_cache)
        # flow = client.initiate_device_flow(scopes=SCOPES)
        
        # request.env.user.user_outlook_user_code = flow['user_code']
        # request.env.user.user_outlook_code = json.dumps(flow)
        
        
        
        
        # return json.dumps({'user_code':flow['user_code']})
        return json.dumps({'user_code':''})
    
    
    @http.route('/check_user_calender', type="http", website=True)
    def check_user_calender(self):
        if  request.session.uid:
            if request.env.user.user_outlook_token:
                
                return {'conect_st':'already_connected'}
            
            if request.env.user.user_outlook_token:
                
                return {'conect_st':'not_connected'}
        
        
    @http.route('/calender_thiqa_api', type="http", website=True)
    def calender_thiqa_api(self):
        APPLICATION_id = "fd0cb42e-b7ae-4c03-9ee9-11b556880048"
        CLIENT_SECRET = "bzo8Q~YE2TcCtQoaD~QwAhGXsxJFKLVGatnXsbSA"
        SCOPES = ['Calendars.ReadWrite']
        
        
        headers = {
           'Authorization': 'Bearer ' + request.env.user.user_outlook_token
        }

        event_name  = "Test Event "
        start = {
            'dateTime': '2023-06-5T08:00:00',
            'timeZone': 'America/Los_Angeles'
        }
        end = {
            'dateTime': '2023-06-06T17:00:00',
            'timeZone': 'America/Los_Angeles'
        } 
        body = {
            # html or text
            'contentType': 'html',
            'content': '<b>2 weeks vacation</b>'
        }
        location = {
            'displayName': 'Tokyo, Japan'
        }
        attendees = [
            {
                'emailAddress': {
                    'address': 'jiejenn@learndataanalysis.org'
                },
                'type': 'required' # or optional
            }
        ]
        response_create = requests.post(f'{GRAPH_API_ENDPOINT}/me/events', headers=headers,
                                            json=construct_event_detail(
                                                                            event_name,
                                                                            body=body,
                                                                            location=location,
                                                                            start=start,
                                                                            end=end,
                                                                            attendees=attendees,
                                                                        )
                                        )
        
        return str(response_create.text)
