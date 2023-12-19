odoo.define("thiqah_portal.dashboard_user", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.ThiqahDashboardUser = publicWidget.Widget.extend({
    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments);

      var heightSlider = $("main").height();

      $("#content").css({ paddingTop: heightSlider + 30 + "px" });
      return def;
    },
  });
});

odoo.define("thiqah_portal.financial_dashboard", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var _t = core._t;

  publicWidget.registry.DeleteRequest = publicWidget.Widget.extend({
    selector: "#by_client_modal",
    events: {
      "click  .financial_filter": "_onClickClientFilter",
      'change select[name="client_id"]': "_onPartnerChange",
    },

    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments);
      // Process for project_id
      this.$project = this.$('select[name="project_id"]');
      this.$projectOptions = this.$project
        .filter(":enabled")
        .find("option:not(:first)");
      this._adaptProjectField();
      return def;
    },

    /**
     * @private
     */
    _onClickClientFilter: function () {
      var client_id = $('select[name="client_id"]').val() || 0;
      var project_id = $('select[name="project_id"]').val() || 0;
      var params = client_id + "and" + project_id;
      if (client_id) {
        window.location.href = "/my/financial/dashboard?filter_by_id=" + params;
      }
    },

    /**
     * @private
     */
    _adaptProjectField: function () {
      var $partner = this.$('select[name="client_id"]');
      var partnerID = $partner.val() || 0;
      this.$projectOptions.detach();
      var $displayedProject = this.$projectOptions.filter(
        "[data-partner_id=" + partnerID + "]"
      );
      $displayedProject.appendTo(this.$project).show();
      // var nb = $displayedProject.appendTo(this.$project).show().length;
      // this.$project.parent().toggle(nb >= 1);
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

    /**
     * @private
     */
    _onPartnerChange: function () {
      this._adaptProjectField();
    },
  });
});
