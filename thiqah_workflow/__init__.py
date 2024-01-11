# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID
from odoo.models import BaseModel, check_pg_name
from odoo.tools import OrderedSet, LastOrderedSet
import logging
_logger = logging.getLogger(__name__)

# Backup original function for any later use
_build_model_old = BaseModel._build_model


EXCLUDED_MODELS = r"^_unknown$|odoo\.workflo.+|res\..+|ir\..+" + \
                  "|bus\..+|base\..+|base\_.+|^base$"


def update_workflow(self):
    """
    Updates Odoo model and registry to apply new workflow changes.
    :return:
    """
    # Variables
    workflow_workflow = self.env['workflow.workflow'].sudo()
    concerned_model = [model.model for model in workflow_workflow.search(
        []).mapped('model_id')]

    # Update
    self.env.cr.commit()
    cr = self.env.registry.cursor()
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.reset()
    # see ir.model.create()
    # reg = modules.registry.Registry.new(self.env.cr.dbname, update_module=True)
    # reg.init_models(self.env.cr, concerned_model, {})
    # self.env.cr.commit()


def update_workflow_reload(self):
    """
    Updates Odoo model and registry to apply new workflow changes with reload.
    :return:
    """
    update_workflow(self)
    # Reload client
    return {
        'type': 'ir.actions.client',
        'tag': 'reload',
    }


# Monkey Patched _build_model method
#
# Goal: try to apply inheritance at the instantiation level and
#       put objects in the pool var
#
@classmethod
def _build_model_new(cls, pool, cr):
    """ Instantiate a given model in the registry.

    This method creates or extends a "registry" class for the given model.
    This "registry" class carries inferred model metadata, and inherits (in
    the Python sense) from all classes that define the model, and possibly
    other registry classes.
    
    """
   
    if getattr(cls, '_constraints', None):
        _logger.warning("Model attribute '_constraints' is no longer supported, "
                        "please use @api.constrains on methods instead.")

    # Keep links to non-inherited constraints in cls; this is useful for
    # instance when exporting translations
    cls._local_sql_constraints = cls.__dict__.get('_sql_constraints', [])

    # all models except 'base' implicitly inherit from 'base'
    name = cls._name
    parents = list(cls._inherit)
    if name != 'base':
        parents.append('base')
    

    # create or retrieve the model's class
    if name in parents:
        if name not in pool:
            raise TypeError("Model %r does not exist in registry." % name)
        ModelClass = pool[name]
        ModelClass._build_model_check_base(cls)
        check_parent = ModelClass._build_model_check_parent
    else:
        ModelClass = type(name, (cls,), {
            '_name': name,
            '_register': False,
            '_original_module': cls._module,
            '_inherit_module': {},                  # map parent to introducing module
            '_inherit_children': OrderedSet(),      # names of children models
            '_inherits_children': set(),            # names of children models
            '_fields': {},                          # populated in _setup_base()
        })
        check_parent = cls._build_model_check_parent

    # determine all the classes the model should inherit from
    bases = LastOrderedSet([cls])
    for parent in parents:
        if parent not in pool:
            raise TypeError(
                "Model %r inherits from non-existing model %r." % (name, parent))
        parent_class = pool[parent]
        if parent == name:
            for base in parent_class.__base_classes:
                bases.add(base)
        else:
            check_parent(cls, parent_class)
            bases.add(parent_class)
            ModelClass._inherit_module[parent] = cls._module
            parent_class._inherit_children.add(name)

    # ModelClass.__bases__ must be assigned those classes; however, this
    # operation is quite slow, so we do it once in method _prepare_setup()
    ModelClass.__base_classes = tuple(bases)

    # determine the attributes of the model's class
    ModelClass._build_model_attributes(pool)

    check_pg_name(ModelClass._table)

    # Transience
    if ModelClass._transient:
        assert ModelClass._log_access, \
            "TransientModels must have log_access turned on, " \
            "in order to implement their vacuum policy"

    # link the class to the registry, and update the registry
    ModelClass.pool = pool
    pool[name] = ModelClass

    # backward compatibility: instantiate the model, and initialize it
    model = object.__new__(ModelClass)
    model.__init__(pool, cr)

    return ModelClass


# Patching _build_model with new method
# BaseModel._build_model = _build_model_new
