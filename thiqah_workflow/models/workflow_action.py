# -*- coding: utf-8 -*-

"""
Concerns buttons that the origin of all actions.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, time, timedelta
import random
import string
import logging

_logger = logging.getLogger(__name__)


PYTHON_CODE_TEMP = """# Available locals:
#  - time, date, datetime, timedelta: Python libraries.
#  - env: Odoo Environement.
#  - model: Model of the record on which the action is triggered.
#  - obj: Record on which the action is triggered if there is one, otherwise None.
#  - user, Current user object.
#  - workflow: Workflow engine.
#  - syslog : syslog(message), function to log debug information to Odoo logging file or console.
#  - warning: warning(message), Warning Exception to use with raise.
# To return an action, assign: action = {...}
"""


class WorkflowAction(models.Model):
    _name = 'workflow.action'
    _description = 'Workflow Action'

    # _sql_constraints = [
    #     ('uniq_name', 'unique(name)', _("Action name must be unique.")),
    # ]

    def _generate_key(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

    name = fields.Char('Name', translate=True)
    type = fields.Char('Type', default='object')
    description = fields.Char('Description')

    is_highlight = fields.Boolean(default=False)
    has_icon = fields.Boolean(
        string='Has Icon', help="Enable it to add icon to the button.")
    icon = fields.Char(
        string='Icon', help="Enter icon name like: fa-print, it's recommended to use FontAwesome Icons.")
    workflow_id = fields.Many2one(
        'workflow.workflow', string='Workflow')

    # Buttons delegating actions can be related to one or many states.
    # This button is related to this state (Question of visibility).
    state_id = fields.Many2one(
        'workflow.state', string="State From", required=True, ondelete="cascade")

    state_to = fields.Many2one(
        'workflow.state', string="State To", required=True, ondelete="cascade")

    # Buttons
    button_key = fields.Char(string='Button Key', default=_generate_key)
    action_type = fields.Selection([
        ('transition', ' Transition From To'),
        ('python_code', 'Python Code'),
        ('action_server', 'Actino Server'),
        ('window_action', 'Window Action'),
    ], required=True
    )
    is_return_action = fields.Boolean( help="Set to True if this action is a return action.", default=False)

    # Python code
    condition_code = fields.Text(string='Python Code', default=PYTHON_CODE_TEMP)

    # Action Server
    server_action_id = fields.Many2one('ir.actions.server', string='Server Action')

    # Window Action
    window_action_id = fields.Many2one('ir.actions.act_window', string='Window Action')

    def name_get(self):
        result = []
        for action in self:
            result.append((action.id, action.description if action.description else action.name))
        return result

    @api.onchange('state_id', 'state_to')
    def _compute_transition_id(self):
        
        for action in self:
            
            transaction_id = self.env['workflow.transition'].sudo().search([('state_from.id', '=', action.state_id.id), ('state_to.id', '=', action.state_to.id)], limit=1)
            
            action.transition_id = transaction_id.id
            
            

    # This data is important to trigger the transition.
    transition_id = fields.Many2one('workflow.transition', string='Transition', compute=_compute_transition_id)

    # Methods For buttons
    @api.constrains('button_key')
    def _constraint_button_key(self):
        for action in self:
            search_count = self.search_count([
                ('id', '!=', action.id),
                ('button_key', '=', action.button_key),
            ])
            if search_count > 0:
                action.button_key = self._generate_key()

    def _run_transition(self):
        for action in self:
            return action.transition_id.trigger_transition()

    def execute_action(self):
        for action in self:
            func = getattr(self, "_run_%s" % action.action_type)
            return func()

    def warning(self, msg):
        if not isinstance(msg, str):
            msg = str(msg)
        raise Warning(msg)

    def syslog(self, msg):
        if not isinstance(msg, str):
            msg = str(msg)
        _logger.info(msg)
