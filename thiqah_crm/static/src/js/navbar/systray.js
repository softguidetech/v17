/** @odoo-module **/

// var SystrayMenu = require('web.SystrayMenu');
// var Widget = require('web.Widget');
// var session = require('web.session');

import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';
import session from 'web.session';

var PortalSystrayWidget = Widget.extend({
   template: 'CalenderPortalSystray',

   /**
    * @ovveride
    */
   start: function () {
      var self = this;
      var is_admin = session.is_admin;
      // Initiliasation $el as hidden
      self.$el.css('display', 'flex');

      
      
      // If the current user  have the groups (base.group_erp_manager,thiqah_crm.group_thiqah_sp_manager) or is a superuser(is_admin)
      var def2 = session.user_has_group('thiqah_crm.group_thiqah_sp_manager').then(function(has_group){
         if ( has_group || is_admin){
            self.$el.css('display', 'flex');
         } 
      });

      var def3 = session.user_has_group('thiqah_project.project_manager_group').then(function(has_group){
         if ( has_group || is_admin){
            self.$el.css('display', 'flex')
         } 
      });


      return Promise.all([def2,def3]);
   }

});

PortalSystrayWidget.prototype.sequence = 9999999;

SystrayMenu.Items.push(PortalSystrayWidget);
export default PortalSystrayWidget;

$(document).on('click','.connect_calender',function(e){


    var calender_connect_modal = `<div class="modal fade" id="calender_connect_modal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
                                        <div class="modal-dialog">
                                        <div class="modal-content">
                                            <div class="modal-header">
                                            
                                            <h4 class="modal-title" id="myModalLabel">Connect To OutLook Calnder</h4>
                                            </div>
                                            <div class="modal-body">
                                            <div class="row">

                                                        <div class="col">
                                                                <img src="/thiqah_crm/static/src/img/6385470.png" />
                                                        </div>

                                                        <div class="col">


                                                                <h2><a href="https://microsoft.com/devicelogin" class="start_connect_link" target="_blank" ><span> Click TO Start Connect Calender </span></a></h2>
                                                                    <br/>
                                                                <h3> After Linke Open Check Code Here </h3>
                
                                                                <h2 class="user_code_show"></h2>

                                                        </div>

                                            </div>
                                                
                                                
                                            
                                            </div>
                                            <div class="modal-footer">
                                            
                                            <button type="button" data-user_code="" class="btn btn-primary create_token_after_finish">Finish</button>
                                            </div>
                                        </div>
                                        </div>
                                    </div>`

    if ($('#calender_connect_modal').length < 1){
        
        $("body").append(calender_connect_modal)
    }

    
   
    
    $('#calender_connect_modal').modal('show')
})

$(document).on('click','.start_connect_link',function(e){


    

    $.ajax({
        type: 'POST',
        url: '/add_user_code_calender',
        // data: formData,
        dataType: 'json',
        processData: false,
        contentType: false,
        success: function (data) {
            console.log(data.user_code)
            $('.user_code_show').html(data.user_code + " <br> Please Click Finish  After Allow API")
            $('.done_create_access_token').attr("data-user_code",data.user_code)

           

        },
        error: function (jqXHR, textStatus, errorMessage) {
           
            console.log(errorMessage); // Optional
        }
    });
})

$(document).on('click','.create_token_after_finish',function(e){

    $.ajax({
        type: 'POST',
        url: '/add_user_code_calender_token_create',
        
        dataType: 'json',
        processData: false,
        contentType: false,
        success: function (data) {
            $('#calender_connect_modal').modal('hide')
           

        },
        error: function (jqXHR, textStatus, errorMessage) {
           
            console.log(errorMessage); 
        }
    });


})