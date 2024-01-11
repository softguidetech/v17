odoo.define('thiqah.utils', function (require) {
    "use strict";
    
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    /**
     * Delete a target row in o_portal_table.
     *
     * @param {e} event 
     * @param {string} abstractfield
     * @param {integr} fieldID
     * @param {string[]} abstractfields
     * @param {integer[]} fieldIds
     * @returns {Boolean}
     */
    function _deleteRow(e, abstractfield, recordID, abstractfields, fieldIds, modelName, selector){
        var $target = $(e.target).closest('tr');
        var $abstractfield = $target.attr(abstractfield);
        var $fieldID = $target.attr(recordID);
        // get index for each parameter
        var abstractfieldIndex = abstractfields.indexOf($abstractfield);
        var fieldIDIndex = abstractfields.indexOf($fieldID);

        // delete the current data from these arrays to avoid the previous test without any need.
        abstractfields.splice(abstractfieldIndex,1);
        fieldIds.splice(fieldIDIndex,1);
        
        var data = {
            'model_name':modelName,
            'record_id': $fieldID,
        }

        // delete record from database.
        ajax.post('/project/subelement/unlink',data).then(function(result){
            if (result == 'unauthorized'){
               $(selector).text(_t("You don't have permission. Contact your administrator."));
               $(selector).removeClass('d-none alert-success').addClass('alert-danger');
               return false;
            }
            else if(result == 'True'){
                // delete row.
                $target.remove();
                $(selector).removeClass('alert-danger').addClass('d-none');
                return result
            }
        }).guardedCatch(function (error) {
            $(selector).text(_t("You don't have permission. Contact your administrator."));
        });
    }

    /**
     * Open a target model in o_portal_table.
     *
     * @param {object} self 
     * @param {string} selector
     * @param {string} tag
     * @param {integer} recordID
     * @returns {Boolean}
     */
    function _onOpenModal(self,selector,modalSelector,tag,recordID){
        $(selector).val($(self)[0].$el.closest(tag).attr(recordID));
        $(modalSelector).show();
    }


    /**
     * Converts a number to/from a human readable string: 1337 ↔> 1.34kB
     *
     * @param {object} self 
     * @param {Float} recordID
     * @returns {Float}
     */
       function toFixedWithoutZeros(self,number){
            return number;
    }



    /**
     * Clean inputs
     *
     * @param {Array} inputs 
     * @returns {Boolean}
     */
    function _cleanInputes(self,inputs){
        // clean inputs after each CRUD action in general.
    }
    
    return {
        _deleteRow: _deleteRow,
        _onOpenModal : _onOpenModal
    };
    
    });
    