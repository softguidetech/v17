/** @odoo-module **/

// var SystrayMenu = require('web.SystrayMenu');
// var Widget = require('web.Widget');
// var session = require('web.session');

import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';
import session from 'web.session';

var pass_as_sp_manager = false;
var pass_as_project_manager = false;

var PortalSystrayWidget = Widget.extend({
   template: 'PortalSystray',
   events: {
      'click': '_onClick',
   },

   /**
    * @ovveride
    */
   start: function () {
      var self = this;
      var is_admin = session.is_admin;
      // Initiliasation $el as hidden
      self.$el.css('display', 'none');

      var def1 =  self._super.apply(self, arguments);

      // If the current user  have the groups (base.group_erp_manager,thiqah_crm.group_thiqah_sp_manager) or is a superuser(is_admin)
      var def2 = session.user_has_group('thiqah_crm.group_thiqah_sp_manager').then(function(has_group){
         if ( has_group || is_admin){
            self.$el.css('display', 'flex');
            pass_as_sp_manager = true;
         } 
      });

      var def3 = session.user_has_group('thiqah_project.project_manager_group').then(function(has_group){
         if ( has_group || is_admin){
            self.$el.css('display', 'flex')
            pass_as_project_manager = true;
         } 
      });


      return Promise.all([def1,def2,def3]);
   },

   _onClick: function(){
      if(pass_as_sp_manager == true){
         console.log("pass_as_sp_manager");
         window.location.href = '/my/home';
      }
      else if(pass_as_project_manager == true){
         console.log("pass_as_project_manager");
         window.location.href = '/my/projects';
      }

      

   }

});

PortalSystrayWidget.prototype.sequence = 9999999;

SystrayMenu.Items.push(PortalSystrayWidget);
export default PortalSystrayWidget;