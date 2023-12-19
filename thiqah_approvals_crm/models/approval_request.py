# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _,Command
from odoo.exceptions import UserError
from collections import defaultdict

class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    vote_value = fields.Integer('Vote Value')


          
class ApprovalCategoryApprover(models.Model):
    _inherit = 'approval.category.approver'
    
    vote_value = fields.Integer('Vote Value',default=1)    

                
class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    opportunity_id = fields.Many2one('crm.lead','Opportunity')

    #Ovveride this fct to change list status 
    def _compute_request_status(self):
        for request in self:
            status_lst=[]
            #Append status per vote value
            for approve in request.approver_ids:
                i=0
                while (i<approve.vote_value):
                    status_lst.append(approve.status)
                    i+=1

            required_statuses = request.approver_ids.filtered('required').mapped('status')
            required_approved = required_statuses.count('approved') == len(required_statuses)
            minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(status_lst)

            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused') >= minimal_approver:
                    status = 'refused'
                elif status_lst.count('new'):
                    status = 'new'
                elif status_lst.count('approved') >= minimal_approver and required_approved:
                    status = 'approved'
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status
    
    #Ovveride This fct to change stage of opportunity after all approval accept
    def action_approve(self, approver=None):
        super().action_approve(approver=None)
        if self.category_id.approval_type=='crm_evaluation' and self.opportunity_id.id and self.request_status == 'approved' and self.opportunity_id.brochure_evaluation_status =='participation_decision' and self.opportunity_id.stage_id.is_brochure_evaluation:
            user = self.env.ref('base.user_root')
            self.with_user(user.id).opportunity_id.sudo().accept_decision()
    
    #Ovveride This fct to change stage of opportunity after all approval refuse
    def action_refuse(self, approver=None):
        super().action_refuse(approver=None)
        if self.category_id.approval_type=='crm_evaluation' and self.opportunity_id.id and self.request_status == 'refused' and self.opportunity_id.brochure_evaluation_status =='participation_decision' and self.opportunity_id.stage_id.is_brochure_evaluation:
            user = self.env.ref('base.user_root')
            self.with_user(user.id).opportunity_id.sudo().reject_decision()
           
           
    #Override this fct to add vote value per approval line
    @api.depends('category_id', 'request_owner_id')
    def _compute_approver_ids(self):
        for request in self:
            #Don't remove manually added approvers
            users_to_approver = defaultdict(lambda: self.env['approval.approver'])
            for approver in request.approver_ids:
                users_to_approver[approver.user_id.id] |= approver
            users_to_category_approver = defaultdict(lambda: self.env['approval.category.approver'])
            for approver in request.category_id.approver_ids:
                users_to_category_approver[approver.user_id.id] |= approver
            new_users = request.category_id.user_ids
            manager_user = 0
            if request.category_id.manager_approval:
                employee = self.env['hr.employee'].search([('user_id', '=', request.request_owner_id.id)], limit=1)
                if employee.parent_id.user_id:
                    new_users |= employee.parent_id.user_id
                    manager_user = employee.parent_id.user_id.id
            approver_id_vals = []
            for user in new_users:
                # Force require on the manager if he is explicitely in the list
                required = users_to_category_approver[user.id].required or \
                    (request.category_id.manager_approval == 'required' if manager_user == user.id else False)
                current_approver = users_to_approver[user.id]
                if current_approver and current_approver.required != required:
                    approver_id_vals.append(Command.update(current_approver.id, {'required': required,'vote_value':users_to_category_approver[user.id].vote_value,}))
                elif not current_approver:
                    approver_id_vals.append(Command.create({
                        'user_id': user.id,
                        'status': 'new',
                        'required': required,
                        'vote_value':users_to_category_approver[user.id].vote_value,
                    }))
            request.update({'approver_ids': approver_id_vals})
  
  
  
    #"Retur"