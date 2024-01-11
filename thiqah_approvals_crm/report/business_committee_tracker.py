# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
from odoo.tools import config, date_utils, get_lang


class CommiteeTrackerreport(models.Model):
    _name = 'business.committee.tracker.report'
    _description ='Business Committee Tracker Report'
    
    
    filter_date = fields.Selection([('week','This Week'),
                                    ('month','This Month'),
                                    ('quarter','This Quarter'),
                                    ('year','This Year'),
                                    ],string="Period",default="week")
    
    
    #Report Name
    def _get_report_base_filename(self):
        return _("Business Committee Tracker")
    
    #Get report data according to report type choosed
    #Action print
    def action_report_print(self):
        return self.env.ref('thiqah_approvals_crm.thiqah_business_commitee_report').report_action(self)

    def get_approvals_data(self):
        
        date=fields.Date.today()
        period_type=self.filter_date
        if period_type == 'week':
                
            this_week_end_date = fields.Date.from_string(date) + datetime.timedelta(days=7)

            peride_date= (date,this_week_end_date)
        elif period_type == 'month':
            peride_date= date_utils.get_month(date)
        elif period_type == 'quarter':
            peride_date= date_utils.get_fiscal_year(date)
        else:
            peride_date= date_utils.get_month(date)[0]
        res=self.env['approval.request'].search([('create_date','>=',peride_date[0]),('create_date','<=',peride_date[1])])
        return res