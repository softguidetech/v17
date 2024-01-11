odoo.define("thiqah.portal.layout.events", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  console.log("this");
  publicWidget.registry.SidebarAndSearchToggler = publicWidget.Widget.extend({
    selector: "#wrapwrap",
    events: {
      "click #sidebarToggle": "_onSidebarTogglerClick",
      "click #toggleSearch": "_onSearchTogglerClick",
    },
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onSidebarTogglerClick: function (event) {
      event.preventDefault();
      $("body").toggleClass("sb-sidenav-toggled");
    },
    _onSearchTogglerClick: function () {
      $("#searchForm").toggleClass("d-none");
      $("#searchForm").toggleClass("search-collapsed");
    },
    /**
     * @override
     */
    start: function () {
      this._super.apply(this, arguments);
      $("body").addClass("sb-nav-fixed");
      $(".o_main_navbar").addClass("o_hidden");
      $(".preloader").fadeOut();
    },
  });
});
