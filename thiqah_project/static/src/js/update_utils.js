

//////////////
// Risk Update
//////////////
odoo.define('thiqah.project.update.risk',function(require){
    'use strict';

    var publicWidget = require('web.public.widget');
    var thiqahUtils = require('thiqah.utils');
    var ajax = require('web.ajax');

    var core = require('web.core');
    var _t = core._t;

    var risk_id = 0;
    var rowIdx = 0;
    var risks_ = []
    const risk_names = [];
    const risk_ids = [];
    var risk_new_ids = [];
    var name_risk = '';

    publicWidget.registry.ThiqahRiskUpdate = publicWidget.Widget.extend({
        selector : '.project_risk_update',
        events : {
            'click #add_project_risk_update':'_onAddRow',
            'click #update_risk_button': '_onClickUpdateRisk',
            'click #table_risk_body_update .remove':'_onDeleteRow', // Event Delegation.
            'click  .open_modal': '_onOpenModal',
        },
        
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            
            // delete whitespace from :
            this.$description_risk_update = this.$('textarea[id="description_risk_update"]');
            var trim_description_risk_update = $.trim(this.$description_risk_update.val());
            this.$description_risk_update.val(trim_description_risk_update);

            this.$corrective_action_update = this.$('textarea[id="corrective_action_update"]');
            var trim_corrective_action_update = $.trim(this.$corrective_action_update.val());
            this.$corrective_action_update.val(trim_corrective_action_update);

            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onOpenModal: function(e){
            // thiqahUtils._onOpenModal(this,'input[name="risk_value"]','#delete_risk_update_confirm_modal','tr','id');
            var risk_id = $(e.target).closest('tr').attr('id');
            this.$('input[name="risk_value"]').val(risk_id);
            $('#delete_risk_update_confirm_modal').show();
        },

        /**
         * @private
         */
        _onClickUpdateRisk: function(){
            //Injection of Adding new rows
            var risks = this.$('input[name="risks"]').val();

            var project_id = this.$('input[name="project_id"]').val();
            
            // in case new lines have been added.
            var risks_new= $('input[name="risk_new_ids"]').val();

            var parameters_add = {
                'risks_new': risks_new,
                'project_id':project_id
            }

            if (risks_new){

                ajax.jsonRpc('/project/risk/new','call',parameters_add).then(function(result){
                    if (result == 'unauthorized'){
                        $('.add_risk_update #details_info').text(_t('You cannot add the risk. Contact your administrator.'));
                        $('.add_risk_update #info_state').removeClass('alert-success').addClass('alert-danger');
                        return false;
                    }
                    else if(result == false){
                        $('.add_risk_update #info_state').addClass('d-none');
                        $('.add_risk_update #details_info').text(_t('You cannot update the risk. Contact your administrator.'));
                        $('.add_risk_update #info_state').removeClass('alert-success').addClass('alert-danger');
                        return false;
                    }
                    else{
                        $('#update_risk_modal').modal('toggle');
                        $("#table_risk_body_update").load(" #table_risk_body_update");
                    }
    
                });
            }
           

            // TODO : make this resources_new string and merge it with the resources
            const risk_ids_ = risks.split(",");
            const risks_ids = $.merge(risk_ids_,risks_);

            
            if(risks_ids){
                $.each( risk_ids, function( index, element ){
                    // Gathering new data.
                    risk_id = parseInt(element);

                    var name_risk_update = $('#risks_tbody_update #'+element+' .name_risk_update').val();
                    var description_risk_update = $('#risks_tbody_update #'+element+' .description_risk_update').val();
                    var owner_risk_update = $('#risks_tbody_update #'+element+' .owner_risk_update').val();
                    var corrective_action_update = $('#risks_tbody_update #'+element+' .corrective_action_update').val();
                    var level_impact_update = $('#risks_tbody_update #'+element+' .level_impact_update').val();
                    var risk_status_update = $('#risks_tbody_update #'+element+' .risk_status_update').val();
                    var risk_type_id_update = $('#risks_tbody_update #'+element+' .risk_type_id_update').val();
    
                    if (name_risk_update || description_risk_update || owner_risk_update || corrective_action_update || level_impact_update || risk_status_update || risk_type_id_update){
                       
                        // Update each risk_id
                        var parameters = {
                            'risk_id': risk_id,
                            'name_risk_update': name_risk_update,
                            'description_risk_update': description_risk_update,
                            'owner_risk_update': owner_risk_update,
                            'corrective_action_update': corrective_action_update,
                            'level_impact_update': level_impact_update,
                            'risk_status_update': risk_status_update,
                            'risk_type_id_update': risk_type_id_update,
                            'risks_new':risks_new
                        }

                        ajax.jsonRpc('/project/risk/update','call',parameters).then(function(result){
                            if (result == 'unauthorized'){
                                $('#details_info').text(_t('You cannot update the risk. Contact your administrator.'));
                                $('#info_state').removeClass('alert-success').addClass('alert-danger');
                                return false;
                            }
                            else if (result == true){
                                $("#table_risk_body_update").load(" #table_risk_body_update");
                            }
                            else if(result == false){
                                $('#info_state').addClass('d-none');
                                $('#details_info').text(_t('You cannot update the risk. Contact your administrator.'));
                                $('#info_state').removeClass('alert-success').addClass('alert-danger');
                                return false;
                            }
                        });
                    }
                });

            }

            // if there is not something wrong.
            // location.reload();
            // window.location.href = '/my/projects/'
            // window.location.href = '/my/projects/'+parseInt(project_id)+'?mode=view'
            
        },


        /**
         * @private
         */
        _onAddRow: function(){
            // Gathering data
            name_risk = this.$('input[name="name_add_update"]').val();
            var description_risk = this.$('textarea[name="description_add_update"]').val();

            var risk_type  = this.$('select[name="type_add_update_id"] option:selected').text();
            var risk_type_id  = this.$('select[name="type_add_update_id"]').val();

            var owner = this.$('input[name="owner_add_update"]').val();
            var corrective_action = this.$('textarea[name="corrective_action_add_update"]').val();

            var level_impact  = this.$('select[name="level_impact_add_update"] option:selected').text();
            var level_impact_key  = this.$('select[name="level_impact_add_update"]').val();

            var risk_status  = this.$('select[name="status_add_update"] option:selected').text();
            var risk_status_key  = this.$('select[name="status_add_update"]').val();


            if(name_risk && description_risk && risk_type_id && owner && corrective_action && level_impact_key && risk_status_key){
                
                if (!risk_names.includes(name_risk)){
                    $('.project_risk_update #info_state').removeClass('alert-danger').addClass('d-none');
                }
    
                 // Ensure that the resource was added once.
                 if (risk_names.includes(name_risk)){
                    $('.project_risk_update #details_info').text(_t('You have already added this risk.'));
                    $('.project_risk_update #info_state').removeClass('d-none alert-success').addClass('alert-danger');
                    return false;
                }

                // Need to insert this.record into thiqah.project.risk
                this._rpc({
                    model: 'thiqah.project.risk',
                    method: 'create',
                    args: [{
                        'name': name_risk,
                        'description': description_risk,
                        'owner': owner,
                        'corrective_action': corrective_action,
                        'level_impact': level_impact_key,
                        'risk_status': risk_status_key,
                        'risk_type_id': parseInt(risk_type_id),
                    }]
                }).then(function (result) {
                        if (result > 0){
                            // fill resource_names to avoid duplcated risks.
                            risk_names.push(name_risk);
                            
                            // set resource_ids value
                            risk_ids.push(parseInt(result))
                            
                            // separate this process even if same data recorded only in risk_ids for clarity.
                            risk_new_ids.push(parseInt(result))
                            risks_.push(parseInt(result))
                            
                            $('input[name="risk_new_ids"]').val("["+risk_new_ids+"]");

                            // Adding a row inside the tbody.              
                            $('#risks_tbody_update').append(`
                            <tr style="background-color:#a1d683;" id="R${++rowIdx}" name-risk="${name_risk}" risk-id="${parseInt(result)}">
                                <td class="row-index">
                                    <p>${name_risk}</p>
                                </td>
                                <td class="row-index">
                                    <p>${description_risk}</p>
                                </td>
                                <td class="row-index">
                                    <p>${risk_type}</p>
                                </td>
                                <td class="row-index">
                                    <p>${owner}</p>
                                </td>
                                <td class="row-index">
                                    <p>${corrective_action}</p>
                                </td>
                                <td class="row-index">
                                    <p>${level_impact}</p>
                                </td>
                                <td class="row-index">
                                    <p>${risk_status}</p>
                                </td>
                                <td class="text-center">
                                    <button class="btn btn-danger btn-circle btn-circle-sm m-1 remove">
                                        <i class="fa fa-trash-o"></i>
                                    </button>
                                </td>
                            </tr>`);
                        }
                    });
            }

            // // After adding to must clean the input(s).
            $("#risk_to_refresh").load(" #risk_to_refresh");
        
        },

        /**
         * @private
         */
        _onDeleteRow: function(event){
            thiqahUtils._deleteRow(event,'name-risk','risk-id',risk_names,risk_new_ids,'thiqah.project.risk','.project_risk_update #info_state');
            $('input[name="risk_new_ids"]').val("["+risk_new_ids+"]");
        }

    });


    publicWidget.registry.DeleteRisk = publicWidget.Widget.extend({
        selector: '#delete_risk_update_confirm_modal',
        events: {
            'click  .delete_risk': '_onDeleteRisk',
        },
        
        /**
         * @private
         */
        _deleteRisk: function () {
            var riskID = $('input[name="risk_value"]').val();

            ajax.jsonRpc("/my/risk/delete/" + riskID, 'call', {})
            .then(function (result) {
                if (result == 'unauthorized'){
                    $('#delete_risk_update_confirm_modal').hide();
                    $('.project_risk_update #details_info').text(_t('You cannot delete this risk. Contact Your administrator.'));
                    $('.project_risk_update #info_state').removeClass('alert-success').addClass('alert-danger');
                }
                else if (result == true){
                    $('#'+riskID+'').remove();
                    $('#delete_risk_update_confirm_modal').modal('toggle');
                }
                else if (result == false){
                    $('#delete_risk_update_confirm_modal').hide();
                    $('.project_risk_update #details_info').text(_t('There is something wrong.'));
                    $('.project_risk_update #info_state').removeClass('alert-success').addClass('alert-danger');
                }
               
            })
            .guardedCatch(function (error) {
                $('#delete_risk_update_confirm_modal').hide();
                $('.project_risk_update #details_info').text(_t('An error occurred. Your changes have not been saved, try again later. Please refresh the page!'));
                $('.project_risk_update #info_state').removeClass('alert-info').addClass('alert-warning');
            });
            
        
            
        },
        
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
         _onDeleteRisk: function () {
            this._deleteRisk();
        },
        
    });

    publicWidget.registry.ChangeNameRisk = publicWidget.Widget.extend({
        selector: '#add_risk_update',
        events: {
            'change input[name="name_add_update"]' :'_onChangeRiskName'
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------


        /**
         * @private
         */
         _onChangeRiskName: function(){
            var $name_add_update  = this.$('input[name="name_add_update"]').val();
            var $add_project_risk_update = this.$('#add_project_risk_update');

            if(!$name_add_update){
                $add_project_risk_update.attr('disabled','disabled');
            }
            else{
                $add_project_risk_update.removeAttr('disabled');
            }
        },
        
        
        
    });

  
});

//////////////
// Resource Update
//////////////
odoo.define('thiqah.project.update.resource',function(require){
    'use strict';

    var publicWidget = require('web.public.widget');
    var thiqahUtils = require('thiqah.utils');
    var ajax = require('web.ajax');

    var core = require('web.core');
    var _t = core._t;

    var resource_id = 0;
    var rowIdx = 0;
    var resources_ = [];
    const resource_names = [];
    const resource_ids = [];
    var resource_new_ids = [];
    var user = '';

    publicWidget.registry.ThiqahResourceUpdate = publicWidget.Widget.extend({
        selector : '.project_resource_update',
        events : {
            'click #add_resource_update':'_onAddRow',
            'click #update_resource_button': '_onClickUpdateResource',
            'click #resource_body_update .remove':'_onDeleteRow', // Event Delegation.
            'click  .open_modal_resource': '_onOpenModal',
        },
        
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onOpenModal: function(e){
            var resource_id = $(e.target).closest('tr').attr('id');
            this.$('input[name="resource_value"]').val(resource_id);
            $('#delete_resource_update_modal').show();
        },

        /**
         * @private
         */
        _onClickUpdateResource: function(){
            //Injection of Adding new rows
            var resources = this.$('input[name="resources"]').val();
 
            var project_id = this.$('input[name="project_id"]').val();
            
            // in case new lines have been added.
            var resources_new= $('input[name="resource_new_ids"]').val();

            var parameters_add = {
                'resources_new': resources_new,
                'project_id':project_id
            }

            ajax.jsonRpc('/project/resource/new','call',parameters_add).then(function(result){
                if (result == 'unauthorized'){
                    $('.project_resource_update #details_info').text(_t('You cannot add the resource. Contact your administrator.'));
                    $('.project_resource_update #info_state').removeClass('alert-success').addClass('alert-danger');
                    return false;
                }
                else if(result == false){
                    $('.project_resource_update #info_state').addClass('d-none');
                    $('.project_resource_update #details_info').text(_t('You cannot update the resource. Contact your administrator.'));
                    $('.project_resource_update #info_state').removeClass('alert-success').addClass('alert-danger');
                    return false;
                }
                else{
                    $('#update_resource_modal').modal('toggle');
                    $("#resource_body_update").load(" #resource_body_update");
                }

            });
            // TODO : make this resources_new string and merge it with the resources
            const resources_ids_ = resources.split(",");
            const resources_ids = $.merge(resources_ids_,resources_);

            if(resources_ids){
                $.each( resources_ids, function( index, element ){
                    // Gathering new data.
                    resource_id = parseInt(element);

                    if (element){
                        var department_id_update = $('#resources_tbody_update #'+element+' .department_id_update').val();
                        var user_id_update = $('#resources_tbody_update #'+element+' .user_id_update').val();
                        var other_update = $('#resources_tbody_update #'+element+' .other_resource_update').val();
                        if (department_id_update || user_id_update){
                            // Update each resource_id
                            var parameters = {
                                'resource_id': resource_id,
                                'department_id_update':department_id_update,
                                'user_id_update':user_id_update,
                                'other_update':other_update,
                                'resources_new':resources_new
                            }
    
                            ajax.jsonRpc('/project/resource/update','call',parameters).then(function(result){
                                if (result == 'unauthorized'){
                                    $('.project_resource_update #details_info').text(_t('You cannot update the resource. Contact your administrator.'));
                                    $('.project_resource_update #info_state').removeClass('alert-success').addClass('alert-danger');
                                    return false;
                                }
                                else if (result == true){
                                    // location.reload();
                                    $("#resource_body_update").load(" #resource_body_update");
                                }
                                else if(result == false){
                                    $('.project_resource_update #info_state').addClass('d-none');
                                    $('.project_resource_update #details_info').text(_t('You cannot update the risk. Contact your administrator.'));
                                    $('.project_resource_update #info_state').removeClass('alert-success').addClass('alert-danger');
                                    return false;
                                }
                            });
                        }
                    }
                });

            }

            // if there is not something wrong.
            // location.reload();
            // window.location.href = '/my/projects/'
            // window.location.href = '/my/projects/'+parseInt(project_id)+'?mode=view'
            

        },


        /**
         * @private
         */
        _onAddRow: function(){
            // Gathering data            
            var department  = this.$('select[name="resource_department_id_update"] option:selected').text();
            var department_id  = this.$('select[name="resource_department_id_update"]').val();

            user  = this.$('select[name="resource_user_id_update"] option:selected').text();
            var user_id  = this.$('select[name="resource_user_id_update"]').val();

            var other = this.$('input[name="resource_other_update"]').val();


            if(department_id && user_id){
                
                if (!resource_names.includes(user)){
                    $('.project_resource_update #info_state').removeClass('alert-danger').addClass('d-none');
                }
    
                 // Ensure that the resource was added once.
                 if (resource_names.includes(user)){
                    $('.project_resource_update #details_info').text(_t('You have already added this resource.'));
                    $('.project_resource_update #info_state').removeClass('d-none alert-success').addClass('alert-danger');
                    return false;
                }

                // Need to insert this.record into thiqah.project.resource
                this._rpc({
                    model: 'thiqah.project.resource',
                    method: 'create',
                    args: [{
                        'name': user,
                        'department_id': parseInt(department_id),
                        'user_id': parseInt(user_id),
                        'other_resource': other,
                        'resource_type':'user',
                    }]})
                    .then(function (result) {
                        if (result > 0){
                            // fill resource_names to avoid duplcated resource.
                            resource_names.push(user);
                            
                            // set resource_ids value
                            resource_ids.push(parseInt(result))
                            
                            resources_.push(parseInt(result))

                            // separate this process even if same data recorded only in risk_ids for clarity.
                            resource_new_ids.push(parseInt(result))
                            
                            $('input[name="resource_new_ids"]').val("["+resource_new_ids+"]");

                            // Adding a row inside the tbody.
                            $('#resource_body_update').append(`
                            <tr style="background-color:#a1d683;" id="R${++rowIdx}" user="${user}" resource-id="${parseInt(result)}">
                                <td class="row-index">
                                    <p>${department}</p>
                                </td>
                                <td class="row-index">
                                    <p>${user}</p>
                                </td>
                                <td class="row-index">
                                    <p>${other}</p>
                                </td>
                                <td class="text-center">
                                    <button class="btn btn-danger btn-circle btn-circle-sm m-1 remove">
                                        <i class="fa fa-trash-o"></i>
                                    </button>
                                </td>
                            </tr>`);
                        }
                    });
            }

            // // After adding to must clean the input(s).
            $("#resource_to_refresh").load(" #resource_to_refresh");
        
        },

        /**
         * @private
         */
        _onDeleteRow: function(event){
            thiqahUtils._deleteRow(event,'user','resource-id',resource_names,resource_new_ids,'thiqah.project.resource','.project_resource_update #info_state');
            $('input[name="resource_new_ids"]').val("["+resource_new_ids+"]");
        }

    });


    publicWidget.registry.DeleteResource = publicWidget.Widget.extend({
        selector: '#delete_resource_update_modal',
        events: {
            'click  .delete_resource': '_deleteResource',
        },
        
        /**
         * @private
         */
        _deleteResource: function (e) {
            var resourceID = $('input[name="resource_value"]').val();
           
            ajax.jsonRpc("/my/resource/delete/" + resourceID, 'call', {})
            .then(function (result) {
                if (result == 'unauthorized'){
                    $('#delete_resource_update_modal').hide();
                    $('.project_resource_update #details_info').text(_t('You cannot delete this risk. Contact Your administrator.'));
                    $('.project_resource_update #info_state').removeClass('alert-success').addClass('alert-danger');
                }
                else if (result == true){
                    $('#'+resourceID+'').remove();
                    $('#delete_resource_update_modal').modal('toggle');
                                                      
                }
                else if (result == false){
                    $('#delete_resource_update_modal').hide();
                    $('.project_resource_update #details_info').text(_t('There is something wrong.'));
                    $('#info_state').removeClass('alert-success').addClass('alert-danger');
                }
               
            })
            .guardedCatch(function (error) {
                $('#delete_risk_update_confirm_modal').hide();
                $('.project_resource_update #details_info').text(_t('An error occurred. Your changes have not been saved, try again later. Please refresh the page!'));
                $('.project_resource_update #info_state').removeClass('alert-info').addClass('alert-warning');
            });
            
            
        },
        
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
         _onDeleteRisk: function () {
            this._deleteRisk();
        },
        
    });

    // publicWidget.registry.ChangeNameRisk = publicWidget.Widget.extend({
    //     selector: '#add_risk_update',
    //     events: {
    //         'change input[name="name_add_update"]' :'_onChangeRiskName'
    //     },

    //     //--------------------------------------------------------------------------
    //     // Private
    //     //--------------------------------------------------------------------------


    //     /**
    //      * @private
    //      */
    //      _onChangeRiskName: function(){
    //         var $name_add_update  = this.$('input[name="name_add_update"]').val();
    //         var $add_project_risk_update = this.$('#add_project_risk_update');

    //         if(!$name_add_update){
    //             $add_project_risk_update.attr('disabled','disabled');
    //         }
    //         else{
    //             $add_project_risk_update.removeAttr('disabled');
    //         }
    //     },
        
        
        
    // });

  
});


odoo.define('thiqah.project.update.basic',function(require){
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.ThiqahProjectUpdate = publicWidget.Widget.extend({
        selector:'#basic_update_selector',
        events:{
            'click  .basic_confirm_update': '_onSubmitUpdateBasic',
        },

        /**
         * @override
         */
         start: function () {
            var def = this._super.apply(this, arguments);
            this.$project_id = parseInt($("input[name='project_id']").val());
            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _onSubmitUpdateBasic: function(e){
           
            // ------ Gathering data ------
            // name
            var $name = this.$('input[name="name_update"]');

            // name_arabic_update
            var $name_arabic = this.$('input[name="name_arabic_update"]');

            // contract_type_id_update
            var $contract_type = this.$('select[name="contract_type_id_update"]');
            var $contract_type_id = ($contract_type.val() || 0);

            // basic_date_start_update
            var $basic_date_start = this.$('input[name="basic_date_start_update"]');

            // basic_date_update
            var $basic_date = this.$('input[name="basic_date_update"]');

            // project_value_update
            var $project_value = this.$('input[name="project_value_update"]');

            // user_id_update
            var $user = this.$('select[name="user_id_update"]');
            var $user_id = ($user.val() || 0);

            var parameters = {
                'project_id': this.$project_id,
                'name': $name.val(),
                'name_arabic': $name_arabic.val(),
                'contract_type_id': $contract_type_id,
                'date_start': $basic_date_start.val(),
                'date': $basic_date.val(),
                'project_value': $project_value.val(),
                'user_id': $user_id,
            }


            ajax.jsonRpc('/project/update/action','call',parameters).then(function(result){
                if (result == true){
                    //$("#basic_update_selector").load(" #basic_update_selector");
                    $('#update_basic_modal').modal('toggle');


                }
                // else{
                //     console.log("result",result)
                // }
            });

        }

    });
});



//////////////
// REVENUE PLANS 
//////////////
odoo.define('thiqah.project.update.revenue',function(require){
    'use strict';

    var publicWidget = require('web.public.widget');
    var thiqahUtils = require('thiqah.utils');
    var ajax = require('web.ajax');

    var core = require('web.core');
    var _t = core._t;

    var revenue_id = 0;
    var rowIdx = 0;
    var revenues_ = [];
    const revenue_names = [];
    const revenue_ids = [];
    const invoice_dates = [];
    var revenue_new_ids = [];
    var invoice_date = '';

    publicWidget.registry.ThiqahRevenueUpdate = publicWidget.Widget.extend({
        selector : '.project_revenue_update',
        events : {
            'click #add_revenue_update':'_onAddRow',
            'click #update_revenue_button': '_onClickUpdateRevenue',
            'click #revenue_body_update .remove':'_onDeleteRow', // Event Delegation.
            'click  .open_modal_revenue': '_onOpenModal',
        },
        
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onOpenModal: function(e){
            var revenue_id = $(e.target).closest('tr').attr('id');
            this.$('input[name="revenue_value"]').val(revenue_id);
            $('#delete_revenue_update_modal').show();
        },

        /**
         * @private
         */
         _onClickUpdateRevenue: function(){
            //Injection of Adding new rows
            var revenues = this.$('input[name="revenues"]').val();
 
            var project_id = this.$('input[name="project_id"]').val();
            
            // in case new lines have been added.
            var revenues_new= $('input[name="revenue_new_ids"]').val();

            var parameters_add = {
                'resources_new': revenues_new,
                'project_id':project_id
            }

            ajax.jsonRpc('/project/revenue/new','call',parameters_add).then(function(result){
                if (result == 'unauthorized'){
                    $('.project_revenue_update #details_info').text(_t('You cannot add the resource. Contact your administrator.'));
                    $('.project_revenue_update #info_state').removeClass('alert-success').addClass('alert-danger');
                    return false;
                }
                else if(result == false){
                    $('.project_revenue_update #info_state').addClass('d-none');
                    $('.project_revenue_update #details_info').text(_t('You cannot update the resource. Contact your administrator.'));
                    $('.project_revenue_update #info_state').removeClass('alert-success').addClass('alert-danger');
                    return false;
                }
                else{
                    $('#update_revenue_modal').modal('toggle');
                    $("#revenue_body_update").load(" #revenue_body_update");
                }

            });

            // TODO : make this resources_new string and merge it with the resources
            const revenues_ids_ = resources.split(",");
            const revenues_ids = $.merge(revenues_ids_,revenues_);

            if(revenues_ids){
                $.each( revenues_ids, function( index, element ){
                    // Gathering new data.
                    revenue_id = parseInt(element);

                    if (element){
                        var invoice_date_update = $('#revenues_tbody_update #'+element+' .invoice_date_update').val();
                        var payment_date_update = $('#revenues_tbody_update #'+element+' .payment_date_update').val();
                        var amount_billed_update = $('#revenues_tbody_update #'+element+' .amount_billed_update').val();
                        var amount_received_update = $('#revenues_tbody_update #'+element+' .amount_received_update').val();
                        var amount_due_update = $('#revenues_tbody_update #'+element+' .amount_due_update').val();
                        var revenue_status_update = $('#revenues_tbody_update #'+element+' .revenue_status_update').val();
                        
                        if (invoice_date_update || payment_date_update || amount_billed_update || amount_received_update || amount_due_update || revenue_status_update){
                            // Update each revenue
                            var parameters = {
                                'revenue_id': revenue_id,
                                'invoice_date':invoice_date_update,
                                'payment_date':payment_date_update,
                                'amount_billed':amount_billed_update,
                                'amount_received':amount_received_update,
                                'amount_due':amount_due_update,
                                'status':revenue_status_update,
                                'resources_new':resources_new
                            }
    
                            ajax.jsonRpc('/project/revenue/update','call',parameters).then(function(result){
                                if (result == 'unauthorized'){
                                    $('.project_revenue_update #details_info').text(_t('You cannot update the resource. Contact your administrator.'));
                                    $('.project_revenue_update #info_state').removeClass('alert-success').addClass('alert-danger');
                                    return false;
                                }
                                else if (result == true){
                                    // location.reload();
                                    $("#resource_body_update").load(" #resource_body_update");
                                }
                                else if(result == false){
                                    $('.project_revenue_update #info_state').addClass('d-none');
                                    $('.project_revenue_update #details_info').text(_t('You cannot update the risk. Contact your administrator.'));
                                    $('.project_revenue_update #info_state').removeClass('alert-success').addClass('alert-danger');
                                    return false;
                                }
                            });
                        }
                    }
                });

            }

            // if there is not something wrong.
            // location.reload();
            // window.location.href = '/my/projects/'
            // window.location.href = '/my/projects/'+parseInt(project_id)+'?mode=view'
            

        },


        /**
         * @private
         */
        _onAddRow: function(){
            // Gathering data
            invoice_date = this.$('input[name="invoice_date_update"]').val();
            var payment_date = this.$('input[name="payment_date_update"]').val();
            var amount_billed = this.$('input[name="amount_billed_update"]').val();
            var amount_received = this.$('input[name="amount_received_update"]').val();
            var amount_due = this.$('input[name="amount_due_update"]').val();

            var revenue_plan_status  = this.$('select[name="revenue_plan_status_update"] option:selected').text();
            var revenue_plan_status_key  = this.$('select[name="revenue_plan_status_update"]').val();
            

            if(invoice_date && payment_date && amount_billed && amount_received && amount_due && revenue_plan_status){
                
                if (!invoice_dates.includes(invoice_date)){
                    $('.project_revenue_plans #info_state').removeClass('alert-danger').addClass('d-none');
                }
    
                 // Ensure that the resource was added once.
                 if (invoice_dates.includes(invoice_date)){
                    $('.project_revenue_plans #details_info').text(_t('You have already added this revenue plan.'));
                    $('.project_revenue_plans #info_state').removeClass('d-none alert-success').addClass('alert-danger');
                    return false;
                }

                // Need to insert this.record into thiqah.project.resource
                this._rpc({
                    model: 'thiqah.revenue.plan',
                    method: 'create',
                    args: [{
                        'invoice_date': invoice_date,
                        'payment_date': payment_date,
                        'amount_billed': amount_billed,
                        'amount_received': amount_received,
                        'amount_due': amount_due,
                        'status': revenue_plan_status_key,
                    }]})
                    .then(function (result) {
                        if (result > 0){
                            // fill resource_names to avoid duplcated resource.
                            invoice_dates.push(invoice_date);
                            
                            // set resource_ids value
                            revenue_ids.push(parseInt(result))

                            var test = $('input[name="revenue_plan_ids"]').val("[(6,0,["+revenue_ids+"])]");
                            // Adding a row inside the tbody.              
                            $('#table_revenue_body').append(`
                            <tr id="R${++rowIdx}" invoice-date="${invoice_date}" revenue-plan-id="${parseInt(result)}">
                                <td class="row-index">
                                    <p>${invoice_date}</p>
                                </td>
                                <td class="row-index">
                                    <p>${payment_date}</p>
                                </td>
                                <td class="row-index">
                                    <p>${amount_billed}</p>
                                </td>
                                <td class="row-index">
                                    <p>${amount_received}</p>
                                </td>
                                <td class="row-index">
                                    <p>${amount_due}</p>
                                </td>
                                <td class="row-index">
                                    <p>${revenue_plan_status}</p>
                                </td>
                            
                                <td class="text-center">
                                    <button class="btn btn-danger remove" type="button">Remove</button>
                                </td>
                            </tr>`);
                        }
                    });



            }


            // // After adding to must clean the input(s).
            $("#revenue_to_refresh").load(" #revenue_to_refresh");
        
        },

        /**
         * @private
         */
        _onDeleteRow: function(event){
            thiqahUtils._deleteRow(event,'user','resource-id',resource_names,resource_new_ids,'thiqah.project.resource','.project_revenue_update #info_state');
            $('input[name="resource_new_ids"]').val("["+resource_new_ids+"]");
        }

    });


    publicWidget.registry.DeleteResource = publicWidget.Widget.extend({
        selector: '#delete_revenue_update_modal',
        events: {
            'click  .delete_revenue': '_deleteRevenue',
        },
        
        /**
         * @private
         */
         _deleteRevenue: function (e) {
            var revenueID = $('input[name="revenue_value"]').val();
           
            ajax.jsonRpc("/my/resource/delete/" + revenueID, 'call', {})
            .then(function (result) {
                if (result == 'unauthorized'){
                    $('#delete_revenue_update_modal').hide();
                    $('.project_revenue_update #details_info').text(_t('You cannot delete this risk. Contact Your administrator.'));
                    $('.project_revenue_update #info_state').removeClass('alert-success').addClass('alert-danger');
                }
                else if (result == true){
                    $('#'+resourceID+'').remove();
                    $('#delete_revenue_update_modal').modal('toggle');
                                                      
                }
                else if (result == false){
                    $('#delete_revenue_update_modal').hide();
                    $('.project_revenue_update #details_info').text(_t('There is something wrong.'));
                    $('#info_state').removeClass('alert-success').addClass('alert-danger');
                }
               
            })
            .guardedCatch(function (error) {
                $('#delete_revenue_update_modal').hide();
                $('.project_revenue_update #details_info').text(_t('An error occurred. Your changes have not been saved, try again later. Please refresh the page!'));
                $('.project_revenue_update #info_state').removeClass('alert-info').addClass('alert-warning');
            });
            
            
        },
        
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
         _onDeleteRisk: function () {
            this._deleteRisk();
        },
        
    });

    // publicWidget.registry.ChangeNameRisk = publicWidget.Widget.extend({
    //     selector: '#add_risk_update',
    //     events: {
    //         'change input[name="name_add_update"]' :'_onChangeRiskName'
    //     },

    //     //--------------------------------------------------------------------------
    //     // Private
    //     //--------------------------------------------------------------------------


    //     /**
    //      * @private
    //      */
    //      _onChangeRiskName: function(){
    //         var $name_add_update  = this.$('input[name="name_add_update"]').val();
    //         var $add_project_risk_update = this.$('#add_project_risk_update');

    //         if(!$name_add_update){
    //             $add_project_risk_update.attr('disabled','disabled');
    //         }
    //         else{
    //             $add_project_risk_update.removeAttr('disabled');
    //         }
    //     },
        
        
        
    // });

  
});

