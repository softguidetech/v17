# -*- coding: utf-8 -*-

"""This model delegate the requiring actions related to the department employee"""

from odoo import models, fields, api


class RequiringAction(models.Model):
    _name = 'thiqah.portal.requiring.action'

    related_code = fields.Char('Related Code')
    process_name = fields.Char('Process Name')
    type = fields.Char('Type')
    service_request_id = fields.Integer('Request ID')

    service_catalog = fields.Char('', compute='compute_service_catalog')
    service_status = fields.Char()

    # In case when the action was trigged , triggred set to True
    is_triggered = fields.Boolean(default=False)

    # Fields dedicated to the department task dashboard
    current_step = fields.Char('Current Step')
    last_step = fields.Char('Last Step')
    last_step_created_by = fields.Many2one('res.users')
    last_step_created_at = fields.Date('Last Step Create At')

    def compute_service_catalog(self):
        for action in self:
            action.service_catalog = self.env['thiqah.project.service.request'].search([
                ('id', '=', int(action.service_request_id))
            ], limit=1).catalog_id.name_en

    # Relations
    user_ids = fields.One2many('res.users', 'requiring_action_id')

    users_ids = fields.Char()

    @api.model
    def cron_requiring_actions(self):
        """
        Assign each the department employee their requests.
        """
        # Delete all rows.
        self.env.cr.execute("""
        delete from thiqah_portal_requiring_action
        """)
        # get workflow(s) related to the service request Model.
        workflows = self.env['workflow.workflow'].sudo().search([
            ('model_id',
             '=',
             self.env['ir.model'].sudo().search([
                 ('model', '=', 'thiqah.project.service.request')
             ]).id
             )
        ])
        # get all path(s) from each transition with their allowed users.
        # datastrucutre format == [(status_technical_name,[allowed_user_ids])]

        # actions_permissions = []
        for workflow in workflows:
            for transition in workflow.transition_ids:

                requests = self.env['thiqah.project.service.request'].sudo().search([
                    ('state', '=', transition.state_from.technical_name)
                ])

                for request in requests:
                    self.create({
                        'service_request_id': request.id,
                        'related_code': request.sequence,
                        'process_name': request.catalog_id.name_en,
                        'type': 'Request Workflow',
                        'service_status': request.state,
                        'user_ids': [(6, 0, transition.transition_validation_ids.user_ids.ids)],
                        'current_step': request.current_step,
                        'last_step': request.last_step,
                        'last_step_created_by': request.last_step_created_by.id,
                        'last_step_created_at': request.last_step_created_at,
                        'users_ids': str([(6, 0, transition.transition_validation_ids.user_ids.ids)])
                    })

                # actions_permissions.append(
                #     (transition.state_from.technical_name,
                #      transition.transition_validation_ids.user_ids.ids)
                # )
        # ==> [('done', [35, 2]), ('draft', []), ('in_progress', [])]

        # if actions_permissions:
        #     # get all requests
        #     for action_permission in actions_permissions:
        #         # get service request which have 'this' state (technical_name)

        #     requests = self.env['thiqah.project.service.request'].sudo()
