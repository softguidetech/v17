# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .user_service_access import SERVICES


""""
    Main purpose : + The idea is to extend the users model to add a boolean describing any additional group for the user portal.
    <> External means public or portal user.
    """


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    belongs_to_quality_assurance = fields.Boolean(default=False)
    external_group_ids = fields.One2many('external.user', 'user_id')
    thiqah_category_id = fields.Many2one('user.category')
    entity = fields.Selection([('thiqah', 'Thiqah'), ('ahad', 'Ahad')], string='Entity')
    # is_vp_ = fields.Boolean(compute='_compute_is_vp', store=True)
    # is_director_finance_ = fields.Boolean()
    service_access_ids = fields.One2many('user.service.access', 'user_id', string='Service Access')

    @api.model
    def get_external_group_ids(self):
        for user in self:
            authorized_groups = [
                external_group_id.group_id.id for external_group_id in user.external_group_ids]
            return authorized_groups

    @api.model
    def has_external_group(self, group_ext_id):
        # use singleton's id if called on a non-empty recordset, otherwise
        # context uid
        uid = self.id
        if uid and uid != self._uid:
            self = self.with_user(uid)
        if self.env.ref(group_ext_id).id in self.get_external_group_ids():
            return True

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResUsersInherit, self).create(vals_list)
        for user in res:
            for service in SERVICES:
                user.service_access_ids.create({
                    'service': service[0],
                    'user_id': user.id,
                })
        return res
    
    def check_service_access(self, service, operation='read'):
        self.ensure_one()
        service_access_id = self.service_access_ids.filtered(lambda r: r.service == service)
        if operation == 'read':
            return service_access_id.access_read
        elif operation == 'create':
            return service_access_id.access_create