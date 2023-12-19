odoo.define("thiqah.tabbed.forms", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.TabbedForms = publicWidget.Widget.extend({
    selector: ".tabbed-form",
    events: {
      "click .next": "_onClickNextTab",
      "click .previous": "_onClickPreviousTab",
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickNextTab: function () {
      var backLink = $(".back-top");
      $(".nav-tabs .active").parent().next("li").find("a").trigger("click");
      backLink.addClass("previous");
      backLink.attr("href", "#");
      backLink.off("click").on("click", this._onClickPreviousTab);
      $(".nav-tabs .active").parent().prev("li").addClass("done");
      $(".nav-tabs .active")
        .parent()
        .prev("li")
        .find("a")
        .html(
          `<svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
          >
            <g clip-path="url(#a)">
              <path
                fill="#fff"
                d="M7.77 19.018c.458 0 .82-.203 1.076-.596L18.9 2.589c.191-.309.266-.543.266-.787 0-.586-.383-.969-.969-.969-.425 0-.66.139-.915.543L7.728 16.602l-4.958-6.49c-.266-.373-.532-.522-.915-.522-.607 0-1.022.415-1.022 1 0 .245.107.522.309.777l5.522 7.034c.32.414.65.617 1.107.617Z"
              />
            </g>
            <defs>
              <clipPath id="a">
                <path fill="#fff" d="M0 0h20v20H0z" />
              </clipPath>
            </defs>
          </svg>`
        );
    },

    /**
     * @private
     */
    _onClickPreviousTab: function () {
      if ($(".nav-tabs .active").attr("href") === "#step1") {
        var backLink = $(".back-top");
        backLink.off("click");
        backLink.removeClass("previous");
        backLink.attr("href", "/my/projects");
      }
      $(".nav-tabs .active").parent().prev("li").find("a").trigger("click");
      $(".nav-tabs .active").parent().next("li").removeClass("done");
    },
  });
});

