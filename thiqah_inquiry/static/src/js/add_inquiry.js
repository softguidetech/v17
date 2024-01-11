odoo.define("thiqah.inquiry.request.form", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var processForm = require("thiqah.Utils").processForm;

  publicWidget.registry.InquiryRequestForm = publicWidget.Widget.extend({
    selector: ".inquiry_request",
    events: {
      "submit #inquiry_request_form": "_onCreateRequest",
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onCreateRequest: function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (e.target.checkValidity() !== false) {
        let form_values = processForm("#inquiry_request_form");
        ajax.post("/website/form/inquiry.request", form_values).then(
          function () {
              $("#createInquiryRequest").hide();
              $("#inquiryRequestAddSuccessModal").modal({
                show: true,
                keyboard: false,
                backdrop: "static",
              });
          },
          function (error) {
            // Handle error here
            console.log(error);
          }
        );
      }
      $(e.target).addClass("was-validated");
    },
  });
});

odoo.define("thiqah.inquiry.request.workflow.engine", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var ajax = require("web.ajax");
  var _t = core._t;

  publicWidget.registry.InquiryRequestWorkflowEngine = publicWidget.Widget.extend({
    selector: ".inquiry_action_selector",
    events: {
      "click .irequest_approve_action": "_onApproveInquiryRequest",
      "change #userAssignModal select[name='user_id']": "_onChangeAssignUser",
      "click .irequest_assign_user_action": "_onClickConfirmAssignUser"
    },

    _onChangeAssignUser: function (e) {
      var user_id = $("select[name='user_id']").val();
          user_id ? $(".irequest_assign_user_action").removeClass('disabled')
            : $(".irequest_assign_user_action").addClass('disabled');
        },
      
    _onClickConfirmAssignUser: function (e) {
      $("body").css("cursor", "progress");
      let requestId = $(e.target).attr("irequest_id");
      let user_id = $("select[name='user_id']").val();
      let note = $("textarea[name='note']").val();
      if (requestId && user_id) {
        let parameters = {
          request_id: requestId,
          user_id: user_id,
          note: note,
        };
        // $(".irequest_approve_action").attr("disabled", "disabled");
        $("#userAssignModal").hide();
        $("#userAssignModal select[name='user_id']").val("")
        $("#userAssignModal textarea[name='note']").val("")
        ajax.jsonRpc("/inquiry/assignUser", "call", parameters)
          .then(function (result) {
              const { status, message } = JSON.parse(result);
              if (status == "success") {
                location.reload();
              } else {
                $(".request-error").removeClass("d-none").text(message);
              }
            });
      };
    },


    _onApproveInquiryRequest: function (e) {
      $("body").css("cursor", "progress");
      var buttonKey = $(e.target).attr("id");
      var requestId = $(e.target).attr("Irequest_id");
      if (requestId && buttonKey) {
        let parameters = {
          request_id: requestId,
          button_key: buttonKey,
          model_name: "inquiry.request",
        };
        $(".irequest_approve_action").attr("disabled", "disabled");
        ajax.jsonRpc("/inquiry/change/status", "call", parameters)
          .then(function (result) {
              const { status, message } = JSON.parse(result);
              if (status == "success") {
                location.reload();
              } else {
                $(".request-error").removeClass("d-none").text(message);
              }
            });
      };
    },
  });
});