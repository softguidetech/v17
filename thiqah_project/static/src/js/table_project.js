odoo.define('thiqah.table.project',function(require){
    'use strict';


    var publicWidget = require('web.public.widget');
    var thiqahUtils  = require('thiqah.utils');
    var session = require('web.session');

    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;
    var is_admin = session.is_admin;
    var pass = false;

    publicWidget.registry.ThiqahTableProject = publicWidget.Widget.extend({
        selector : '.project_action_buttons',
        events : {
            'click  .read_request': '_onReadProject',
            'click  .update_project': '_onUpdateProject',
            'click  .open_modal': '_onOpenModal',
            'click  ._project_change_status': '_onChangeStatus',
        },

        /**
         * @override
         */
        start: function(){
            var def1 = this._super.apply(this,arguments);

            // initialize data 
            this.$projectID = $(this)[0].$el.closest('tr').attr('project_id');

            // If the current user  have the groups (base.group_erp_manager,thiqah_crm.group_thiqah_sp_manager) or is a superuser
            var def2 = session.user_has_group('project.group_project_manager').then(function(has_group){
                if ( has_group || is_admin){
                    $('.delete_request').removeClass('d-none');
                    $('._project_change_status').removeClass('d-none');
                    pass = true;
                } 
            });

            var def3= session.user_has_group('thiqah_project.project_manager_group').then(function(has_group){
                if ( has_group || is_admin){
                    $('.delete_request').removeClass('d-none');
                    $('._project_change_status').removeClass('d-none');
                    pass = true;
                } 
            });

            return Promise.all([def1,def2,def3]);

        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onOpenModal: function(){
            thiqahUtils._onOpenModal(this,'input[name="project_value"]','#delete_project_confirm_modal','tr','project_id');
        },

        /**
         * @private
         */
        _readProject: function (e) {   
            window.location.href = '/my/projects/'+this.$projectID+'/?mode=view';
        },

        /**
          * @private
          */
        _updateProject: function () {
            if (pass == true){
            window.location.href = '/web#model=project.project&id='+this.$projectID+'&view_type=form';
            // window.location.href = '/my/project/update/'+this.$projectID+'/?mode=edit';
            }
        },

         /**
         * @private
         */
        _deleteRequest: function () {
            var $requestID = $('input[name="request_value"]').val();
            ajax.jsonRpc("/my/request/delete/" + $requestID, 'call', {})
            .then(function (result) {
                if (result == 'unauthorized'){
                    $('#delete_confirm_modal').hide();
                    $('#subscription_info').text(_t('You cannot delete the request because it has already been discussed in the replies area.'));
                    $('#info_state').removeClass('alert-success').addClass('alert-danger');
                }
                else if (result == true){
                    location.reload();
                    // Inplace Reload
                    // $('.o_portal_my_doc_table').load(document.URL +  ' .o_portal_my_doc_table');
                }
               
            })
            .guardedCatch(function (error) {
                $('#delete_confirm_modal').hide();
                $('#subscription_info').text(_t('An error occurred. Your changes have not been saved, try again later.'));
                $('#info_state').removeClass('alert-info').addClass('alert-warning');
            });
            
        
            
        },

        /**
         * @private
         */
         _onChangeStatus:function(e){
            if (pass == true){
                window.location.href = '/my/projects/'+this.$projectID+'/?mode=change_status';
            }
            return false;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onReadProject: function () {
            this._readProject();
        },

        /**
         * @private
         */
        _onUpdateProject: function () {
            this._updateProject();
        },
        

        
    });



     // The separation of the deletion process is to avoid the duplicate of the modal

     publicWidget.registry.DeleteProject = publicWidget.Widget.extend({
        selector: '#delete_project_confirm_modal',
        events: {
            'click  .delete_request': '_onDeleteRequest',
        },
        
        /**
         * @private
         */
        _deleteRequest: function () {
            var $projectID = $('input[name="project_value"]').val();
            ajax.jsonRpc("/my/project/delete/" + $projectID, 'call', {})
            .then(function (result) {
                if (result == 'unauthorized'){
                    $('#delete_project_confirm_modal').hide();
                    $('#details_info').text(_t('You cannot delete the project. Contact Your administrator.'));
                    $('#info_state').removeClass('alert-success').addClass('alert-danger');
                }
                else if (result == true){
                    location.reload();
                    // Inplace Reload
                    // $('.o_portal_my_doc_table').load(document.URL +  ' .o_portal_my_doc_table');
                }
                else if (result == false){
                    $('#delete_project_confirm_modal').hide();
                    $('#details_info').text(_t('There is something wrong.'));
                    $('#info_state').removeClass('alert-success').addClass('alert-danger');
                }
               
            })
            .guardedCatch(function (error) {
                $('#delete_project_confirm_modal').hide();
                $('#details_info').text(_t('An error occurred. Your changes have not been saved, try again later. Please refresh the page!'));
                $('#info_state').removeClass('alert-info').addClass('alert-warning');
            });
            
        
            
        },
        
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
         _onDeleteRequest: function () {
            this._deleteRequest();
        },
        
    });


   

});


odoo.define('thiqah.project.status.actions',function(require){
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var session = require('web.session');

    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.ProjectStatusActions = publicWidget.Widget.extend({
        selector:'.projects_status_action_selector',
        events : {
            'click  .project_change_status': '_onChangeStatus',
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * @private
         */
        _onChangeStatus: function(e){
            var buttonKey = $(e.target).attr('id');
            var project_id = $(e.target).closest('div').attr('project_id');
            // var userId = $(e.target).closest('div').attr('user_id');
            console.log("buttonKey",buttonKey);
            console.log("project_id",project_id);

            if(project_id && buttonKey){
                let parameters = {
                    'project_id':project_id,
                    'button_key':buttonKey,
                    // 'user_id': userId
                }
                ajax.jsonRpc('/project/change/status','call',parameters).then(function(result){
                    if (result == 'AccessError'){
                        $('#project_status_info').text(_t('Sorry, you are not allowed to do this action.'));
                        $('#info_status').removeClass('alert-success').addClass('alert-danger');
                    }
                    else if (result == 'NullPointerError'){
                        $('#project_status_info').text(_t('there is no data to send to the server.'));
                        $('#info_status').removeClass('alert-success').addClass('alert-danger');
                    }
                    else if(result == true){
                        location.reload()
                    }
                });
            }
           
            
        },

    });

});