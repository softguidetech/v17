odoo.define("thiqah.service.request.form", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var processForm = require("thiqah.Utils").processForm;

  publicWidget.registry.ServiceRequestForm = publicWidget.Widget.extend({
    selector: ".service_request",
    events: {
      'change select[name="partner_id"]': "_onPartnerChange",
      'change select[name="department_id"]': "_onDepartmentChange",
      'change input[name="date_from"]': "_onRequestDate",
      "submit #service_request_form": "_onCreateRequest",
    },

    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments);

      // styling the select field
      this.$(".selectpicker").selectpicker();
      var listOfOptions = this.$("#partner_id option").filter(function (i, e) {
        return $(e).attr("value") != null;
      });
      if (listOfOptions.length >= 1) {
        this.$("#partner_id").val($(listOfOptions[0]).attr("value"));
      }
      //val(data);
      $("#date_from").datepicker({
        format: "yyyy-mm-d",
        setDate: new Date(),
        todayHighlight: true,
        autoclose: true,
      });
      // Process for project_id
      this.$project = this.$('select[name="project_id"]');

      this.$projectOptions = this.$project
        .filter(":enabled")
        .find("option:not(:first)");
      this._adaptProjectField();

      // Process for department_id
      this.$department = this.$('select[name="catalog_id"]');
      this.$departmentOptions = this.$department
        .filter(":enabled")
        .find("option:not(:first)");
      this._adaptDepartmentField();

      return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _adaptProjectField: function () {
      var $partner = this.$('select[name="partner_id"]');
      var partnerID = $partner.val() || 0;
      this.$projectOptions.detach();
      var $displayedProject = this.$projectOptions.filter(
        "[data-partner_id=" + partnerID + "]"
      );
      $displayedProject.appendTo(this.$project).show();
      this.$(".selectpicker").selectpicker("refresh");
      // var nb = $displayedProject.appendTo(this.$project).show().length;
      // this.$project.parent().toggle(nb >= 1);
    },

    /**
     * @private
     */
    _adaptDepartmentField: function () {
      var $department = this.$('select[name="department_id"]');
      var departmentID = $department.val() || 0;
      this.$departmentOptions.detach();
      var $displayedDepartment = this.$departmentOptions.filter(
        "[data-department_id=" + departmentID + "]"
      );
      $displayedDepartment.appendTo(this.$department).show();
      this.$(".selectpicker").selectpicker("refresh");
      // var nb = $displayedDepartment.appendTo(this.$department).show().length;
      // this.$department.parent().toggle(nb >= 1);
    },
    /**
     * @private
     */
    _inputControlDateRequest: function (event) {
      var $SelectedDate = new Date(this.$('input[name="date_from"]').val());
      var CurrentDate = new Date();

      if ($SelectedDate > CurrentDate) {
        $("#later_date_error").removeClass("d-none");
        $(".submit_add_request").addClass("disabled");
      } else {
        $("#later_date_error").addClass("d-none");
        $(".submit_add_request").removeClass("disabled");
      }
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onPartnerChange: function () {
      this._adaptProjectField();
    },

    /**
     * @private
     */
    _onDepartmentChange: function () {
      this._adaptDepartmentField();
    },
    /**
     * @private
     */

    _onRequestDate: function () {
      this._inputControlDateRequest();
    },
    /**
     * @private
     */
    _onCreateRequest: function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (e.target.checkValidity() !== false) {
        let form_values = processForm("#service_request_form");
        ajax
          .post("/website/form/thiqah.project.service.request", form_values)
          .then(
            function (response) {
              $("#createServiceRequest").hide();
              $("#requestAddSuccessModal").modal({
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

odoo.define("thiqah.service.request.table", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  var thiqahUtils = require("thiqah.utils");
  var ajax = require("web.ajax");
  var session = require("web.session");
  var is_admin = session.is_admin;

  var core = require("web.core");
  var _t = core._t;
  var pass = false;
  var pass_update = false;

  publicWidget.registry.ServiceRequestTable = publicWidget.Widget.extend({
    selector: ".request_action_buttons",
    events: {
      "click  .read_request": "_onReadRequest",
      "click  .update_request": "_onUpdateRequest",
      "click  .open_modal": "_onOpenModal",
      "click  ._change_status": "_onChangeStatus",
    },

    /**
     * @override
     */
    start: function () {
      var def1 = this._super.apply(this, arguments);

      // $('.delete_request').addClass('d-none');
      // $('._change_status').addClass('d-none');

      // initialize data
      this.$requestID = $(this)[0].$el.closest("tr").attr("request_id");

      // get the current state of the service request.
      this.$current_state = $(this)[0].$el.closest("tr").attr("state");

      // get the current assigned to
      this.$user_id = $(this)[0].$el.closest("tr").attr("user_id");

      // if (this.$user_id == session.user_id){
      //     $('._change_status').removeClass('d-none');
      //     pass = true;
      // }

      // If the current user  have the groups (base.group_erp_manager,thiqah_crm.group_thiqah_sp_manager) or is a superuser
      // var def2 = session.user_has_group('project.group_project_manager').then(function(has_group){
      //     if ( has_group || is_admin){
      //         $('#delete_request').removeClass('d-none');
      //         // $('._change_status').removeClass('d-none');
      //         pass = true;
      //     }
      // });
      // var def3 = session.user_has_group('thiqah_base.group_change_status_service_request').then(function(has_group){
      //     if ( has_group || is_admin){
      //         $('._change_status').removeClass('d-none');
      //         pass = true;
      //     }
      // });

      // var def4 = session.user_has_group('thiqah_base.group_update_service_request').then(function(has_group){
      //     if ( has_group || is_admin){
      //         pass_update = true;
      //     }
      // });

      // return Promise.all([def1,def2,def3,def4]);
      return Promise.all([def1]);
      // return Promise.all([def1,def2,self._updateRequest()]);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onOpenModal: function () {
      // $('input[name="request_value"]').val($(this)[0].$el.closest('tr').attr('request_id'));
      // $('#delete_confirm_modal').show();
      thiqahUtils._onOpenModal(
        this,
        'input[name="request_value"]',
        "#delete_confirm_modal",
        "tr",
        "request_id"
      );
    },

    /**
     * @private
     */
    _readRequest: function (e) {
      window.location.href = "/my/requests/" + this.$requestID + "/?mode=view";
    },

    /**
     * @private
     */
    _updateRequest: function () {
      // if (pass_update == true){
      window.location.href =
        "/web#model=thiqah.project.service.request&id=" +
        this.$requestID +
        "&view_type=form";
      // window.location.href = '/my/project/update/'+this.$projectID+'/?mode=edit';
      // }
      // window.location.href = '/my/requests/'+this.$requestID+'/?mode=edit';
    },

    /**
     * @private
     */
    _deleteRequest: function () {
      // ajax.jsonRpc("/my/request/delete/" + this.$requestID, 'call', {})
      // .then(function (result) {
      //     if (result == 'unauthorized'){
      //         $('#delete_confirm_modal').hide();
      //         $('#subscription_info').text(_t('You cannot delete the request because it has already been discussed in the replies area.'));
      //         $('#info_state').removeClass('alert-success').addClass('alert-danger');
      //     }
      //     else if (result == true){
      //         location.reload();
      //         // Inplace Reload
      //         // $('.o_portal_my_doc_table').load(document.URL +  ' .o_portal_my_doc_table');
      //     }
      // })
      // .guardedCatch(function (error) {
      //     $('#delete_confirm_modal').hide();
      //     $('#subscription_info').text(_t('An error occurred. Your changes have not been saved, try again later.'));
      //     $('#info_state').removeClass('alert-info').addClass('alert-warning');
      // });
    },

    /**
     * @private
     */
    _ChangeStatus: function (e) {
      // if (pass == true){
      window.location.href =
        "/my/requests/" + this.$requestID + "/?mode=change_status";
      // }
      return false;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onReadRequest: function () {
      this._readRequest();
    },

    /**
     * @private
     */
    _onChangeStatus: function () {
      this._ChangeStatus();
    },

    /**
     * @private
     */
    _onUpdateRequest: function () {
      this._updateRequest();
    },

    /**
     * @private
     */
    _onDeleteRequest: function () {
      this._deleteRequest();
    },
  });
});

// The separation of the deletion process is to avoid the duplicate of the modal

odoo.define("thiqah.portal.delete.request", function (require) {
  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var session = require("web.session");
  var is_admin = session.is_admin;

  var core = require("web.core");
  var _t = core._t;
  var pass = false;

  publicWidget.registry.DeleteServiceRequest = publicWidget.Widget.extend({
    selector: "#delete_confirm_modal",
    events: {
      "click  #delete_request": "_onDeleteRequest",
    },

    /**
     * @private
     */
    _deleteRequest: function () {
      var $requestID = $('input[name="request_value"]').val();
      ajax
        .jsonRpc("/my/request/delete/" + $requestID, "call", {})
        .then(function (result) {
          if (result == true) {
            location.reload();
            // Inplace Reload
            // $('.o_portal_my_doc_table').load(document.URL +  ' .o_portal_my_doc_table');
          } else if (result == "unauthorized") {
            $("#delete_confirm_modal").hide();
            $("#details_info").text(
              _t(
                "You cannot delete the request because it has already been discussed in the replies area."
              )
            );
            $("#info_state")
              .removeClass("alert-success")
              .addClass("alert-danger");
          } else if (result == "refresh") {
            $("#delete_confirm_modal").hide();
            $("#details_info").text(_t("Please refresh and try again."));
            $("#info_state")
              .removeClass("alert-success")
              .addClass("alert-danger");
          }
        })
        .guardedCatch(function (error) {
          $("#delete_confirm_modal").hide();
          $("#details_info").text(
            _t(
              "An error occurred. Your changes have not been saved, try again later.Please refresh and try again."
            )
          );
          $("#info_state").removeClass("alert-info").addClass("alert-warning");
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

odoo.define("thiqah.service.request.followup", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var _t = core._t;

  publicWidget.registry.ServiceRequestFollowUp = publicWidget.Widget.extend({
    selector: "#request_followup",
    events: {
      "submit  #request_update_form": "_onSubmitUpdateRequest",
      "change form": "_onChangeForm",
    },

    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments);
      this.$request_id = parseInt($("input[name='request_id']").val());
      return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _submitUpdateRequest: function (e) {
      // The objective is to stop the propagation of the action coming from the form to the controller
      // in order to override the type of the request (http) to json,so that we can encapsulate the parameters in json format.
      e.preventDefault();

      //partner_id
      var $partner = this.$('select[name="partner_id"]');
      var $partner_id = $partner.val() || 0;

      //project_id
      var $project = this.$('select[name="project_id"]');
      var $project_id = $project.val() || 0;
      // //department_id
      // var $department = this.$('select[name="department_id"]');
      // var $department_id = ($department.val() || 0);
      // //catalog_id
      // var $catalog = this.$('select[name="catalog_id"]');
      // var $catalog_id = ($catalog.val() || 0);
      //description
      var $description = this.$('textarea[name="description"]');
      var $description_new = $description.val();

      if ($partner_id == 0 || $project_id == 0) {
        $("#details_info").text(_t("Please fill in the form correctly."));
        $("#info_state")
          .removeClass("alert-success")
          .removeClass("alert-info")
          .removeClass("alert-error")
          .addClass("alert-danger");

        // Disable Sign Up Button
        var $btn = this.$('button[type="submit"]');
        $btn.attr("disabled", "disabled");
      } else {
        var parameters = {
          request_id: this.$request_id,
          partner_id: $partner_id,
          project_id: $project_id,
          // 'department_id': $department_id,
          // 'catalog_id': $catalog_id,
          description: $.trim($description_new),
        };

        ajax
          .jsonRpc("/my/request/update", "call", parameters)
          .then(function (result) {
            // $('#request_followup').load(document.URL +  ' #request_followup');
            if (result == true) {
              window.location.href = "/my/requests";
            }
          });
      }
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      //partner_id
      var $partner = this.$('select[name="partner_id"]');
      var $partner_id = $partner.val() || 0;
      //project_id
      var $project = this.$('select[name="project_id"]');
      var $project_id = $project.val() || 0;
      // //department_id
      // var $department = this.$('span[id="department"]');
      // var $department_id = ($department.val() || 0);
      // //catalog_id
      // var $catalog = this.$('select[name="catalog_id"]');
      // var $catalog_id = ($catalog.val() || 0);

      if ($partner_id == 0 || $project_id == 0) {
        $("#details_info").text(_t("Please fill in the form correctly."));
        $("#info_state").removeClass("alert-success").addClass("alert-danger");

        // Disable Sign Up Button
        //    var $btn = this.$('button[type="submit"]');
        var $btn = $(".open_update_confirm_modal");
        $btn.addClass("disabled");
      } else if (!$partner_id == 0 && !$project_id == 0) {
        $("#details_info").text(_t("The form seems correct.."));
        $("#info_state").removeClass("alert-danger").addClass("alert-success");
        // Disable Sign Up Button
        // var $btn = this.$('button[type="submit"]');
        var $btn = $(".open_update_confirm_modal");
        $btn.removeClass("disabled");
      }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * #private
     */
    _onSubmitUpdateRequest: function (e) {
      this._submitUpdateRequest(e);
    },
  });
});

odoo.define("thiqah.control.request.textarea", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.ThiqahControlTextarea = publicWidget.Widget.extend({
    selector: ".notes_request_class",

    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments);

      // delete whitespace from :
      this.$description = this.$('textarea[name="description"]');
      var trimStr = $.trim(this.$description.val());
      this.$description.val(trimStr);

      return def;
    },
  });
});

odoo.define("thiqah.table2excel", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.Table2Excel = publicWidget.Widget.extend({
    selector: ".header_actions",
    events: {
      "click ._generate_excel": "onClickGenerateExcel",
    },

    /**
     * @private
     */
    onClickGenerateExcel: function () {
      $("#service_requests_table").table2excel({
        filename: "excel_sheet-name.xls",
      });
    },
  });
});

odoo.define("thiqah.service_request.actions", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var session = require("web.session");

  var core = require("web.core");
  var _t = core._t;

  publicWidget.registry.ServiceRequestActions = publicWidget.Widget.extend({
    selector: ".service_request_action_selector",
    events: {
      "click  .change_status": "_onChangeStatus",
      "click  .change_status_modal": "_onChangeStatusModal",
      "click .display_always": "_onDisplayAlways",
      "click .display_always_modal": "_onDisplayAlwaysReject",
      'keyup textarea[name="approve_description"]':
        "_onJustificationApproveControl",
      'change input[name="approve_attachments"]':
        "_onJustificationApproveControl",
      'keyup textarea[name="reject_description"]':
        "_onJustificationRejectControl",
      'change input[name="reject_attachments"]':
        "_onJustificationRejectControl",
    },

    /**
     * @override
     */
    start: function () {
      $(".change_status_modal").attr("disabled", true);
      $(".display_always_modal").attr("disabled", true);
      return this._super.apply(this, arguments);
    },

    /**
     * @private
     */
    _onOpenModal: function () {
      // $('input[name="request_value"]').val($(this)[0].$el.closest('tr').attr('request_id'));
      // $('#delete_confirm_modal').show();
      thiqahUtils._onOpenModal(
        this,
        'input[name="request_value"]',
        "#delete_confirm_modal",
        "tr",
        "request_id"
      );
    },

    // TODO: Merge into one function _onJustificationChange()
    /**
     * @private
     */
    _onJustificationApproveControl: function () {
      let approve_description = $('textarea[name="approve_description"]').val();
      let approve_attachments = document.getElementById(
        "approve_attachments"
      ).files;

      if (approve_description || approve_attachments.length > 0) {
        $(".change_status_modal").attr("disabled", false);
      } else {
        $(".change_status_modal").attr("disabled", true);
      }
    },
    /**
     * @private
     */
    _onJustificationRejectControl: function () {
      let reject_description = $('textarea[name="reject_description"]').val();
      let reject_attachments =
        document.getElementById("reject_attachments").files;

      if (reject_description || reject_attachments.length > 0) {
        $(".display_always_modal").attr("disabled", false);
      } else {
        $(".display_always_modal").attr("disabled", true);
      }
    },

    // TODO: Merge into one prive function _onChangeStatus
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * @private
     */
    _onChangeStatus: function (e) {
      $("body").css("cursor", "progress");
      var buttonKey = $(e.target).attr("id");
      var requestId = $(e.target).closest("div").attr("request_id");
      var userId = $(e.target).closest("div").attr("user_id");

      if (requestId && buttonKey) {
        let parameters = {
          request_id: requestId,
          button_key: buttonKey,
          user_id: userId,
        };
        ajax
          .jsonRpc("/service/change/status", "call", parameters)
          .then(function (result) {
            $(".change_status").attr("disabled", "disabled");
            if (typeof result !== "undefined") {
              var these_data = jQuery.parseJSON(result);
              if (these_data["error"] == "true") {
                $("body").css("cursor", "not-allowed");
                $(".change_status").css("cursor", "not-allowed");
                $("#change_status_info").text(_t(these_data["message"]));
                $("#info_status")
                  .removeClass("alert-success")
                  .addClass("alert-danger");
                setInterval(function () {
                  $("body").css("cursor", "auto");
                }, 3000);
              } else if (these_data["error"] == "false") {
                location.reload();
              } else if (result == false) {
                $(".change_status").prop("disabled", false);
                $("body").css("cursor", "default");
                $("#justification_div").removeClass("d-none");
                $("#message_justification").addClass(
                  "message_justification_ badge badge-danger"
                );
              }
            }
          });
      }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * @private
     */
    _onChangeStatusModal: function (e) {
      $("body").css("cursor", "progress");
      var buttonKey = $(e.target).attr("id");
      var requestId = $(e.target).closest("div").attr("request_id");
      var userId = $(e.target).closest("div").attr("user_id");

      let description = $('textarea[name="approve_description"]').val();

      let attachments = document.getElementById("approve_attachments").files;

      for (let i = 0; i < attachments.length; i++) {
        var reader = new FileReader();
        reader.readAsDataURL(attachments[i]);
        reader.onload = function (e) {
          ajax
            .jsonRpc("/upload_attachment", "call", {
              attachments: e.target.result,
              attachment_name: attachments[i].name,
              requestId: requestId,
            })
            .then(function (data) {});
        };
      }

      if (requestId && buttonKey) {
        let parameters = {
          request_id: requestId,
          button_key: buttonKey,
          user_id: userId,
          justification: description,
        };
        ajax
          .jsonRpc("/service/change/status", "call", parameters)
          .then(function (result) {
            // $('#request_followup').load(document.URL +  ' #request_followup');
            // return false;
            $(".change_status").attr("disabled", "disabled");
            if (typeof result !== "undefined") {
              var these_data = jQuery.parseJSON(result);
              if (these_data["error"] == "true") {
                $("body").css("cursor", "not-allowed");
                $(".change_status").css("cursor", "not-allowed");
                $("#change_status_info").text(_t(these_data["message"]));
                $("#info_status")
                  .removeClass("alert-success")
                  .addClass("alert-danger");
                setInterval(function () {
                  $("body").css("cursor", "auto");
                }, 3000);
              } else if (these_data["error"] == "false") {
                location.reload();
              } else if (result == false) {
                $(".change_status").prop("disabled", false);
                $("body").css("cursor", "default");
                $("#justification_div").removeClass("d-none");
                $("#message_justification").addClass(
                  "message_justification_ badge badge-danger"
                );
              }
            }
          });
      }
    },

    /**
     * @private
     */
    _onDisplayAlwaysReject: function (e) {
      // not always, except in some cases | after the last customization.
      var activeState = $(e.target).attr("active_state");
      var requestId = $(e.target).closest("div").attr("request_id");

      let description = $('textarea[name="reject_description"]').val();

      let attachments = document.getElementById("reject_attachments").files;

      for (let i = 0; i < attachments.length; i++) {
        var reader = new FileReader();
        reader.readAsDataURL(attachments[i]);
        reader.onload = function (e) {
          ajax
            .jsonRpc("/upload_attachment", "call", {
              attachments: e.target.result,
              attachment_name: attachments[i].name,
              requestId: requestId,
            })
            .then(function (data) {});
        };
      }

      if (requestId) {
        let parameters = {
          request_id: requestId,
          justification: description,
        };
        // if user.has_group(project_manager)
        ajax
          .jsonRpc("/service/reject/status", "call", parameters)
          .then(function (result) {
            // $('#request_followup').load(document.URL +  ' #request_followup');
            if (result == "AccessError") {
              $("#change_status_info").text(
                _t("Sorry, you are not allowed to do this action.")
              );
              $("#info_status")
                .removeClass("alert-success")
                .addClass("alert-danger");
            } else if (result == true) {
              location.reload();
            } else if (result == false) {
              $("#justification_div").removeClass("d-none");
              $("#message_justification").addClass(
                "message_justification_ badge badge-danger"
              );
              // $('#message_justification').text(_t('Sorry, this stage need a justification.'));
            }
          });
      }
    },

    /**
     * @private
     */
    _onDisplayAlways: function (e) {
      var activeState = $(e.target).attr("active_state");
      var requestId = $(e.target).closest("div").attr("request_id");

      let description = $('textarea[name="reject_description"]').val();

      let attachments = document.getElementById("reject_attachments").files;

      for (let i = 0; i < attachments.length; i++) {
        var reader = new FileReader();
        reader.readAsDataURL(attachments[i]);
        reader.onload = function (e) {
          ajax
            .jsonRpc("/upload_attachment", "call", {
              attachments: e.target.result,
              attachment_name: attachments[i].name,
              requestId: requestId,
            })
            .then(function (data) {});
        };
      }

      if (requestId) {
        let parameters = {
          request_id: requestId,
          justification: description,
        };
        // if user.has_group(project_manager)
        ajax
          .jsonRpc("/service/reject/status", "call", parameters)
          .then(function (result) {
            // $('#request_followup').load(document.URL +  ' #request_followup');
            if (result == "AccessError") {
              $("#change_status_info").text(
                _t("Sorry, you are not allowed to do this action.")
              );
              $("#info_status")
                .removeClass("alert-success")
                .addClass("alert-danger");
            } else if (result == true) {
              location.reload();
            } else if (result == false) {
              $("#justification_div").removeClass("d-none");
              $("#message_justification").addClass(
                "message_justification_ badge badge-danger"
              );
              // $('#message_justification').text(_t('Sorry, this stage need a justification.'));
            }
          });
      }
    },
  });
});

odoo.define("thiqah.projects.details.requests", function (require) {
  "use strict";
  var session = require("web.session");
  var core = require("web.core");
  var _t = core._t;
  function format(d) {
    // `d` is the original data object for the row
    return (
      '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
      "<tr>" +
      "<td>Actions</td>" +
      '<td><a href="/my/requests/' +
      d[9] +
      '?mode=change_status" class="fa fa-eye"></a></td>' +
      "</tr>" +
      "<tr>" +
      "<td>Current Step:</td>" +
      "<td>" +
      d[5] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Request status:</td>" +
      "<td>" +
      d[4] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Last Step:</td>" +
      "<td>" +
      d[6] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Last Step created By:</td>" +
      "<td>" +
      d[7] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Last Step creation Date Time:</td>" +
      "<td>" +
      d[8] +
      "</td>" +
      "</tr>" +
      "</table>"
    );
  }
  
  // this is called even we don't need to fetch ==> need to fix this
  if (session.user_id) {
    $(document).ready(function () {
      // thanks to https://jsfiddle.net/sii_side/2w3hxqg6/
      var now = new Date();
      var y = now.getFullYear();
      var m = now.getMonth() + 1;
      var d = now.getDate();

      m = m < 10 ? "0" + m : m;
      d = d < 10 ? "0" + d : d;
      $("tbody").addClass("table-wrapper");
      var projects_details;
      $.ajax({
        async: false,
        type: "GET",
        url: "/get/projects/details",
        success: function (data) {
          projects_details = data;
        },
        error: function (data) {},
      });

      var these_data = jQuery.parseJSON(projects_details);
      var htmlLang = $("html").attr("lang");
      // Gathering
      var projects_details_data = these_data["projects_details_data"];
      $.extend($.fn.dataTable.defaults, {
        autoWidth: true,
        dom: '<"datatable-header"fl><"datatable-scroll"t><"datatable-footer"ip>',
        language: {
          search:
            '<div class="form-control-feedback form-control-feedback-end flex-fill"><div class="form-control-feedback-icon"><i class="fa fa-search opacity-50"></i></div>_INPUT_</div>',
          searchPlaceholder: htmlLang.includes("ar")? "بحث...":"Search...",
          lengthMenu: `<span class="body2" style="color: #798793 !important">Enties Shown:</span> _MENU_`,
          paginate: {
            first: _t("First"),
            last: _t("Last"),
            next: _t("Next"),
            previous: _t("Previous"),
          },
        },
      });
     
      var projects_details_ = $("#projects_details_table").DataTable({
        language: htmlLang.includes("ar")?{
          "sLengthMenu": "أظهر _MENU_ مدخلات",
          "sZeroRecords": "لم يعثر على أية سجلات",
          "sInfo": "إظهار _START_ إلى _END_ من أصل _TOTAL_ مدخل",
          "sInfoEmpty": "يعرض 0 إلى 0 من أصل 0 سجل",
          "sInfoPostFix": "",
          "oPaginate": {
              "sFirst": "الأول",
              "sPrevious": "السابق",
              "sNext": "التالي",
              "sLast": "الأخير"
          }}:'',
        responsive: true,
        data: projects_details_data,
        columns: [
          { title: htmlLang.includes("ar")?"رقم المشروع":"Project Number" },
          { title: htmlLang.includes("ar")?"اسم المشروع":"Project Name" },
          { title: htmlLang.includes("ar")?"مدير المشروع":"Project Manager" },
          { title: htmlLang.includes("ar")?"عدد الطلبات":"Requests Count" },
        ],
      });
     
    });
  }
});


$(document).ready(function () {
  var htmlLang = $("html").attr("lang");
  !(function (a) {
    a.fn.datepicker.dates.ar = {
      days: [
        "الأحد",
        "الاثنين",
        "الثلاثاء",
        "الأربعاء",
        "الخميس",
        "الجمعة",
        "السبت",
        "الأحد",
      ],
      daysShort: [
        "أحد",
        "اثنين",
        "ثلاثاء",
        "أربعاء",
        "خميس",
        "جمعة",
        "سبت",
        "أحد",
      ],
      daysMin: ["ح", "ن", "ث", "ع", "خ", "ج", "س", "ح"],
      months: [
        "يناير",
        "فبراير",
        "مارس",
        "أبريل",
        "مايو",
        "يونيو",
        "يوليو",
        "أغسطس",
        "سبتمبر",
        "أكتوبر",
        "نوفمبر",
        "ديسمبر",
      ],
      monthsShort: [
        "يناير",
        "فبراير",
        "مارس",
        "أبريل",
        "مايو",
        "يونيو",
        "يوليو",
        "أغسطس",
        "سبتمبر",
        "أكتوبر",
        "نوفمبر",
        "ديسمبر",
      ],
      today: "هذا اليوم",
      rtl: !0,
    };
  })(jQuery);
  $(".selectpicker").selectpicker();
  $(".input-group.date").each((i, el) => {
    $($(el).parent()).attr("id",Math.trunc(Math.random()*20) + 1);
    $(el).datepicker({
      format: "yyyy-mm-dd",
      todayHighlight: true,
      autoclose: true,
      rtl: htmlLang.includes("ar") ? true : false,
      language: htmlLang.includes("ar") ? "ar" : "en",
      orientation: "auto left",
      container: htmlLang.includes("ar")?"div#"+$($(el).parent()).attr("id"):'body'
    })
  });
});