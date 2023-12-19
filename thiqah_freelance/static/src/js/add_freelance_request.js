odoo.define("thiqah.freelance.workforce.request", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  var htmlLang = $("html").attr("lang");

  publicWidget.registry.FreelanceRequestForm = publicWidget.Widget.extend({
    selector: ".freelancer_request",
    events: {
      "change #project_end_date": "_onChangeDate",
      "change .basic_change_selector": "_onChangeForm",
    },

    start: function () {
      var def = this._super.apply(this, arguments);
      $("#request_date").datepicker({
        format: "yyyy-mm-d",
      });
      return def;
    },

    _onChangeDate: function () {
      var date_start = $('input[name="project_start_date"]').val();
      var date_end = $('input[name="project_end_date"]').val();
      if (date_start) {
        if (new Date(date_start) > new Date(date_end)) {
          $(".state_next_step").prop("disabled", true);
          $("#details_info").text(
            htmlLang.includes("ar")
              ? "يجب أن يكون تاريخ الانتهاء بعد تاريخ البدء بترتيب زمني."
              : "The end date must be later than the start date chronologically."
          );
          $("#info_state")
            .removeClass("d-none alert-success")
            .addClass("text-danger heading-7");
          $('a[role="tab"]').addClass("disabled");
          return false;
        } else {
          $(".state_next_step").prop("disabled", false);
          $("#info_state")
            .removeClass("text-danger heading-7")
            .addClass("d-none");
        }
      }
      this._onChangeForm();
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      var $project_start_date = this.$el
        .find('input[name="project_start_date"]')
        .val();
      var $project_end_date = this.$el
        .find('input[name="project_end_date"]')
        .val();
      var $expected_total_cost = this.$el
        .find('input[name="expected_total_cost"]')
        .val();

      //Sector
      var $sector = this.$el.find('input[name="sector"]').val();

      //department_id
      var $department_id = this.$el.find('select[name="department_id"]');
      var $department = $department_id.val() || 0;
      //request date
      var $request_date = this.$el.find('input[name="request_date"]').val();
      // section
      var $section = this.$el.find('input[name="section"]').val();

      //description
      var $request_description = this.$el
        .find('textarea[name="request_description"]')
        .val();

      //Entity
      var $entity_id = this.$el.find('select[name="entity"]');
      var $entity = $entity_id.val() || "";
      //request type
      var $request_type_id = this.$el.find('select[name="request_type"]');
      var $request_type = $request_type_id.val() || "";

      if (
        $department != 0 &&
        $sector &&
        $expected_total_cost &&
        $project_start_date &&
        $project_end_date &&
        $request_date &&
        $section &&
        $entity != "" &&
        $request_type != "" &&
        $request_description
      ) {
        /**Why this ???  */
        $('a[role="tab"]').removeClass("disabled");
        $("a.state_next_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.state_next_step").addClass("disabled");
      }
    },
  });
});

odoo.define("thiqah.freelance.justification.request", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var _t = core._t;
  var session = require("web.session");
  var ajax = require("web.ajax");

  publicWidget.registry.RequestJustificationForm = publicWidget.Widget.extend({
    selector: ".justification_list",
    events: {
      "change .basic_change_selector": "_onChangeForm",
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      //description
      var $company_strategy_justif = this.$el
          .find('textarea[name="company_strategy_justif"]')
          .val(),
        $sector_goal_justif = this.$el
          .find('textarea[name="sector_goal_justif"]')
          .val(),
        $request_achievement = this.$el
          .find('textarea[name="request_achievement"]')
          .val();

      if (
        $company_strategy_justif &&
        $sector_goal_justif &&
        $request_achievement
      ) {
        $('a[role="tab"]').removeClass("disabled");
        $("a.justif_next_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.justif_next_step").addClass("disabled");
      }
    },
  });
});
odoo.define("thiqah.freelance.implications.form", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  publicWidget.registry.organizationalImplicationsForm =
    publicWidget.Widget.extend({
      selector: ".freelance_implications",
      events: {
        "change .basic_change_selector": "_onChangeForm",
      },

      /**
       * @private
       */
      _onChangeForm: function () {
        //description
        var $current_manpower_limit = this.$el
            .find('textarea[name="current_manpower_limit"]')
            .val(),
          $current_manpower_weakness = this.$el
            .find('textarea[name="current_manpower_weakness"]')
            .val(),
          $table_implications_body = this.$el.find(
            "#table_implications_body tr"
          ).length;

        if (
          $current_manpower_limit &&
          $current_manpower_weakness &&
          $table_implications_body > 0
        ) {
          $('a[role="tab"]').removeClass("disabled");
          $("a.implications_next_step").removeClass("disabled");
        } else {
          $('a[role="tab"]').addClass("disabled");
          $("a.implications_next_step").addClass("disabled");
        }
      },
    });
});

odoo.define("thiqah.freelance.functions", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  publicWidget.registry.functionsBreackdownForm = publicWidget.Widget.extend({
    selector: ".function_breakdown",
    events: {
      "change .basic_change_selector": "_onChangeForm",
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      //description
      var $function = this.$el.find('textarea[name="function"]').val(),
        $unit_kpi = this.$el.find('textarea[name="unit_kpi"]').val(),
        $deliverable = this.$el.find('textarea[name="deliverable"]');
      length;

      if ($function && $unit_kpi && $deliverable) {
        $('a[role="tab"]').removeClass("disabled");
        $("a.function_next_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.function_next_step").addClass("disabled");
      }
    },
  });
});

odoo.define("thiqah.freelance.outcome", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  publicWidget.registry.deliverableOutcomenForm = publicWidget.Widget.extend({
    selector: ".deliverable_outcome",
    events: {
      "change .basic_change_selector": "_onChangeForm",
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      //description
      var $deliverable_outcome = this.$el
        .find('textarea[name="deliverable_outcome"]')
        .val();

      if ($deliverable_outcome) {
        $('a[role="tab"]').removeClass("disabled");
        $("a.outcome_next_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.outcome_next_step").addClass("disabled");
      }
    },
  });
});
odoo.define("thiqah.freelance.implications", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.FreelanceImplications = publicWidget.Widget.extend({
    selector: ".freelance_wizard",
    events: {
      "click #add_implication": "_onAddRow",
      "click #table_implications_body .remove": "_onDeleteRow",
    },
    /**
     * @override
     */
    start: function () {
      var result = this._super.apply(this, arguments);
      $("#implicationsDiv").hide();
      return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onAddRow: function () {
      var $btn = $("#add_implication"),
        $unit = $("select[name='modal_department_id']"),
        $operation = $("input[name='modal_operation']");
      $("#table_implications_body").append(`
      <tr>
          
          <td class="row-index">
              <p>${$unit.find(":selected").text()}</p>
          </td>
          <td class="row-index">
              <p>${$operation.val()}</p>
          </td>
          <td class="td-actions">
              <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
              <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
            </svg></button>
          </td>
          <td class="d-none">
              <p>${$unit.val()}</p>
          </td>
      </tr>`);
      this.$(".placeholder-card").hide();
      this.$("#implicationsDiv").show();
      $unit.val("");
      $operation.val("");
      $("#addImplicationModal").modal("hide");
      $("#current_manpower_limit").trigger("change");
    },

    /**
     * @private
     */
    _onDeleteRow: function (event) {
      $(event.target).closest("tr").remove();
      $("#current_manpower_limit").trigger("change");
      if ($("#table_implications tbody tr").length == 0) {
        this.$(".placeholder-card").show();
        $("#implicationsDiv").hide();
      }
    },
  });
});
odoo.define("thiqah.freelance.form.submit", function (require) {
  "use strict";

  $("#freelance_add_form").on("submit", function (e) {
    e.preventDefault();
    e.stopPropagation();
    let implication_ids = [];
    let $entity = $("select[name='entity']").val();
    $("input[name='entity_id']").val($entity);
    $("#table_implications_body tr").each(function (idx, elem) {
      $("#freelance_add_form").append(
        `<input type="hidden" name="unit_${idx + 1}" value="${$(elem)
          .find("td:last-child() p")
          .text()}" /> `
      );
      $("#freelance_add_form").append(
        `<input type="hidden" name="operation_${idx + 1}" value="${$(elem)
          .find("td:nth-child(2) p")
          .text()}" /> `
      );
      implication_ids.push({
        unit: $(elem).find("td:nth-child(1) p").text(),
        operation: $(elem).find("td:nth-child(2) p").text(),
      });
    });
    implication_ids = JSON.stringify(implication_ids);
    $("#freelance_add_form").append(
      `<input type="hidden" name="implication_ids" value=${
        $("#table_implications_body tr").length
      } />`
    );
    if (this.checkValidity() !== false) {
      $.blockUI({
        css: { backgroundColor: "transparent", border: "none" },
        message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
      });
      $.ajax({
        url: "/freelance/form/add",
        method: "POST",
        data: $(this).serialize(),
        success: function (data) {
          $.unblockUI();
          const { status, Message } = JSON.parse(data);
          if (status == "success") {
            $("#freelanceAddSuccessModal").modal({
              show: true,
              keyboard: false,
              backdrop: "static",
            });
          } else {
            $(".request-error").removeClass("d-none").text(Message);
          }
        },
      });
    }
    $(this).addClass("was-validated");
  });
});
odoo.define("thiqah.freelance.application.form.submit", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var _t = core._t;
  var QWeb = core.qweb;
  var htmlLang = $("html").attr("lang");

  var htmlLang = $("html").attr("lang");

  publicWidget.registry.FreelancerApplicationRequestForm =
    publicWidget.Widget.extend({
      selector: "#addFreelancerDetailsModal",
      events: {
        "change #end_date": "_onChangeDate",
        "change #bank_country": "_onChangeBankCountry",
        "change #bank": "_onchangeBank",
        "change input[name='withholding_tax']": "_onChangeWithholding",
        "click .create_freelancer": "_onClickCreateFreelancer",
        "click .create_bank": "_onClickCreateBank",
      },
      init: function (parent) {
        this._super.apply(this, arguments);
        this.banksList = [];
      },

      _onChangeDate: function () {
        var date_start = $('input[name="start_date"]').val();
        var date_end = $('input[name="end_date"]').val();
        if (date_start) {
          if (new Date(date_start) > new Date(date_end)) {
            $("#details_info").text(
              htmlLang.includes("ar")
                ? "يجب أن يكون تاريخ الانتهاء بعد تاريخ البدء بترتيب زمني."
                : "The end date must be later than the start date chronologically."
            );
            $("#info_state")
              .removeClass("d-none alert-success")
              .addClass("text-danger heading-7");
            $('a[role="tab"]').addClass("disabled");
            return false;
          } else {
            $("#info_state")
              .removeClass("text-danger heading-7")
              .addClass("d-none");
          }
        }
      },
      _onChangeBankCountry: function (e) {
        var self = this;
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        var def = this._rpc({
          route: "/freelance/get_banks_branches",
          params: { country_code: $(e.target).val() },
        }).then(function (banksdData) {
          self.banksList = banksdData["Banks"];
          if (self.banksList) {
            $(".invalid-code").addClass("d-none");
            $("#bank").attr("disabled", false);
            $("#bank")
              .selectpicker("refresh")
              .empty()
              .append(
                self.banksList.map(function (bank) {
                  return $("<option/>", {
                    value: bank.BANKIDENTIFIER,
                    text: bank.BANKNAME,
                  });
                })
              )
              .selectpicker("refresh")
              .trigger("change");
          } else {
            $(".invalid-code").removeClass("d-none");
            $("#bank").attr("disabled", true).empty().selectpicker("refresh");
            $("#branch").attr("disabled", true).empty().selectpicker("refresh");
          }
          $.unblockUI();
        });
        return def;
      },
      _onchangeBank: function (e) {
        var branches = _.filter(this.banksList, function (i) {
          if (i.BANKIDENTIFIER == e.target.value) return i.Branches;
        });
        $("#branch").attr("disabled", false);
        $("#branch")
          .selectpicker("refresh")
          .empty()
          .append(
            branches[0].Branches.map(function (branch) {
              return $("<option/>", {
                value: branch.BANKBRANCHIDENTIFIER,
                text: branch.BANKBRANCHNAME,
              });
            })
          )
          .selectpicker("refresh")
          .trigger("change");
      },
      _onClickCreateFreelancer: function (e) {
        e.preventDefault();
        e.stopPropagation();
        let vals = {};
        var frequest = $(e.target).attr("frequest");
        vals["frequest"] = frequest;
        $("#create_freelancer_form input,#create_freelancer_form textarea, #create_freelancer_form select")
          .not("[type='file']")
          .not("[type='hidden']")
          .not("[type='search']")
          .each(function (idx, el) {
            vals[$(el).attr("name")] = $(el).val();
            if($(el).attr("type") == "checkbox"){
              vals[$(el).attr("name")] = $(el).is(":checked");
            }
          });
        if (document.querySelector("#create_freelancer_form").checkValidity()) {
          $("#create_freelancer_form").removeClass("was-validated");
          $.blockUI({
            css: { backgroundColor: "transparent", border: "none" },
            message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
          });
          this._rpc({
            route: "/freelance/create_freelancer",
            params: vals,
          }).then(function (res) {
            const { status, freelancer_id, message } = JSON.parse(res);
            $.unblockUI();
            $("#freelancer_details_form").removeClass("was-validated");
            if (status === "success") {
              $(".frequest_creation").addClass("d-none");
              $(".bank_creation").removeClass("d-none");
              $("#freelancer_id").val(freelancer_id);
            } else {
              $(".create_freelancer_error").text(message);
            }
          });
        } else {
          $("#create_freelancer_form").addClass("was-validated");
        }
      },
      _onChangeWithholding: function(e){
        $(".withholding-tax-comment").toggleClass("d-none")
      },

      convert2DataUrl: async function (attachments) {
        var freelance_attach = [];
        for (let i = 0; i < attachments.length; i++) {
          var reader = new FileReader();
          reader.readAsDataURL(attachments[i]);
          await new Promise((resolve) => (reader.onload = () => resolve()));
          freelance_attach.push({
            fileName: attachments[i].name,
            fileData: reader.result,
          });
        }
        return freelance_attach;
      },

      _onClickCreateBank: async function (e) {
        e.preventDefault();
        e.stopPropagation();
        let vals = {};
        var frequest = $(e.target).attr("frequest");
        vals["frequest"] = frequest;
        vals["freelancer_id"] = $("#freelancer_id").val();
        $(".bank_creation input, .bank_creation select")
          .not("[type='file']")
          .not("[type='hidden']")
          .not("[type='search']")
          .each(function (idx, el) {
            vals[$(el).attr("name")] = $(el).val();
          });
        if (
          document.querySelector("#create_bank_form").checkValidity() &&
          $("#freelancer_attachments")[0].files.length > 1
        ) {
          $(".custom-input-file").removeClass("border-danger");
          $("#attach_error").addClass("d-none");
          $("#create_bank_form").removeClass("was-validated");
          vals["bank_name"] = $("#bank option:selected").text();
          vals["branch_name"] = $("#branch option:selected").text();
          var attachments = $("input[name='attachments']")[0].files;
          vals["attachments"] = await this.convert2DataUrl(attachments);
          $.blockUI({
            css: { backgroundColor: "transparent", border: "none" },
            message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
          });
          this._rpc({
            route: "/freelance/create_bank",
            params: vals,
          }).then(function (res, xhr) {
            $.unblockUI();
            const { status, message } = JSON.parse(res);
            if (status === "success") {
              $("#addFreelancerDetailsModal").hide();
              location.href = location.pathname;
            } else {
              $(".create_bank_error").text(message);
            }
          });
        } else {
          $("#create_bank_form").addClass("was-validated");
          if ($("#freelancer_attachments")[0].files.length <= 1) {
            $("#attach_error")
              .removeClass("d-none")
              .text(htmlLang.includes("ar")?"يرجى تحميل جميع المرفقات المطلوبة (ملفين)!":"Please upload all required attachments (2 files)!");
            $(".custom-input-file").addClass("border-danger");
          }
        }
      },
    });
});

odoo.define("thiqah.freelance.request.view.mode", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var ajax = require("web.ajax");
  var _t = core._t;
  var Utils = require("thiqah.Utils");

  publicWidget.registry.FreelanceRequestViewMode = publicWidget.Widget.extend({
    selector: ".frequest_action_selector",
    events: {
      "click .frequest_reject_modal": "_onRejectFreelanceRequest",
      "click .frequest_approve_action": "_onApproveFreelanceRequest",
      "change .s_website_form_input": "_onChangeODInputs",
      "change #contract_document_input": "_onChangeContractDocument",
    },
    _onRejectFreelanceRequest: function (e) {
      var frequestId = $(e.target).attr("frequest_id");
      let description = $('textarea[name="reject_description"]').val();

      if (frequestId) {
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        let parameters = {
          frequest_id: frequestId,
          justification: description,
          model_name: "freelance.request",
        };
        ajax
          .jsonRpc("/freelance/reject", "call", parameters)
          .then(function (result) {
            $.unblockUI();
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
            }
          });
      }
    },

    _onChangeContractDocument: function (e) {
      let contract_document = document.getElementById("contract_document_input").files;
      if (contract_document.length > 0) {
        $(".change_status_modal").attr("disabled", false);
      } else {
        $(".change_status_modal").attr("disabled", true);
      }
    },

    _onApproveFreelanceRequest: async function (e) {
      $.blockUI({
        css: { backgroundColor: "transparent", border: "none" },
        message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
      });
      var od_recommendation = "",
        od_duration,
        od_cost;
      var buttonKey = $(e.target).attr("id");
      var requestId = $(e.target).attr("frequest_id");
      var state = $(e.target).attr("state_name");
      
      if (requestId && buttonKey) {
        if (state == "od_approval") {
          od_recommendation = $("#od_recommendation").val();
          od_duration = parseInt($("#od_duration").val());
          od_cost = parseInt($("#od_cost").val());
        }
        else if (state == "hr_ops_approval"){
          var attachment = $("#contract_document_input")[0].files;
          attachment = await Utils.convert2DataUrl(attachment);
          }
        let parameters = {
          request_id: requestId,
          button_key: buttonKey,
          od_recommendation: od_recommendation,
          od_duration: od_duration,
          od_cost: od_cost,
          state: state,
          attachment: attachment,
          model_name: "freelance.request",
        };
        ajax
          .jsonRpc("/freelance/change/status", "call", parameters)
          .then(function (result) {
            $(".frequest_approve_action").attr("disabled", "disabled");
            // TODO PLEASE FIX THE BELOW CODE
            if (typeof result !== "undefined") {
              var these_data = jQuery.parseJSON(result);
              if (these_data["error"] == "true") {
                $.unblockUI();
                $("body").css("cursor", "not-allowed");
                $(".frequest_approve_action").css("cursor", "not-allowed");
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
                $(".frequest_approve_action").prop("disabled", false);
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

    _onChangeODInputs: function (e) {
      var od_recommendation = $("#od_recommendation").val();
      var od_duration = parseInt($("#od_duration").val());
      var od_cost = parseInt($("#od_cost").val());
      if (od_recommendation && od_duration && od_cost) {
        $("#ODapprovalModalID .frequest_approve_action").attr("disabled",false).removeClass("disabled");
      } else {
        $("#ODapprovalModalID .frequest_approve_action").attr("disabled",true).addClass("disabled");
      }
    },
  });
});

odoo.define("thiqah.freelance.workorder", function (require) {
  "use-strict";

  var ajax = require("web.ajax");
  var Utils = require("thiqah.Utils");
  var formatCurrency = Utils.formatCurrency;
  var htmlLang = $("html").attr("lang");
  $(document).ready(function () {
    $(".adjust-amount-modal .s_website_form_input").on("change", function (e) {
      var workorderID = $($($('.adjust-amount-modal.show')[0]).find("input[type='hidden'][name='workorder_id']")).val();
      console.log($(e.target));
      var adjust_justif = $(`textarea[name='adjust_amount_justif_${workorderID}']`).val(),
        amount = $(`input[name='amount_${workorderID}']`).val();
      adjust_justif && amount
        ? $(".adjust_amount_button").attr("disabled", false)
        : $(".adjust_amount_button").attr("disabled", true);
    });
    // Adjust Amount Justification
    $(".adjust_amount_button").on("click", function (e) {
      var workorderID = $(e.target).attr("workorderID");
      var adjust_justif = $(`textarea[name='adjust_amount_justif_${workorderID}']`).val(),
        amount = $(`input[name='amount_${workorderID}']`).val();

      if (workorderID) {
        let parameters = {
          workorderID: workorderID,
          adjust_justif: adjust_justif,
          amount: amount,
          model_name: "freelance.workorder",
        };
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        ajax
          .jsonRpc("/freelance_workorder/adjust/amount", "call", parameters)
          .then(function (result) {
            $.unblockUI();
            const { status } = JSON.parse(result);
            if (status == "success") {
              $(
                `tr[freelance_workorder_id='${workorderID}'] td.workOrderAmount span`
              ).text(formatCurrency(amount));
              $(`#adjustAmountModal_${workorderID}`).modal("hide");
            }
          });
      }
    });

    //Select and deselect all checkboxes
    $("#checkAll").click(function () {
      $(".orderChk").prop("checked", this.checked);
      if (location.search.split("=")[1] == "draft") {
        $(".confirm_workorder").toggleClass("d-none");
      }
      if (location.search.split("=")[1] == "confirmed") {
        $(".pay_workorder").toggleClass("d-none");
      }
    });

    //If one item deselect then checkbox 'checkAll' is UnCheck
    //If all items select individually then checkbox 'checkAll' is Check
    $(".orderChk").click(function () {
      // Show/Hide the pay button if at least one checkbox is checked
      if ($(".orderChk:checked").length > 0) {
        if (location.search.split("=")[1] == "draft") {
          $(".confirm_workorder").removeClass("d-none");
        }
        if (location.search.split("=")[1] == "confirmed") {
          $(".pay_workorder").removeClass("d-none");
        }
        // $(".pay_workorder").removeClass("d-none");
      } else {
        if (location.search.split("=")[1] == "draft") {
          $(".confirm_workorder").addClass("d-none");
        }
        if (location.search.split("=")[1] == "confirmed") {
          $(".pay_workorder").addClass("d-none");
        }
        // $(".pay_workorder").addClass("d-none");
      }
      $("#checkAll").prop(
        "checked",
        $(".orderChk:checked").length == $(".orderChk").length ? true : false
      );
    });
    var ordersIDs = [];
    $(".pay_workorder").on("click", function () {
      $("#workorderPayModal").modal("show");
    });
    $(".confirm_workorder").on("click", function () {
      $("#workorderConfirmModal").modal("show");
    });

    $("#pay_orders").on("click", function () {
      $("#pay_orders").attr("disabled", true);
      if ($(".orderChk:checked").length > 0) {
        $(".orderChk:checked").each(function () {
          ordersIDs.push(
            parseInt($(this).closest("tr").attr("freelance_workorder_id"))
          );
        });
      }
      $.blockUI({
        css: { backgroundColor: "transparent", border: "none" },
        message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
      });
      ajax
        .jsonRpc("/freelance/validate_invoice", "call", { orderIDs: ordersIDs })
        .then(function (res) {
          $.unblockUI();
          const { status, message } = JSON.parse(res);
          if (status == "success") {
            $("#workorderPayModal h4")
              .addClass("text-success")
              .text(htmlLang.includes("ar")?"تم دفع الطلب (ات) المحدد (ة) بنجاح!":"The selected order(s) are successfully paid!");

            window.location.href = "/my/freelance_workorder?filterby=paid";
          } else if (status == "failed") {
            $("#workorderPayModal h4").addClass("text-danger").text(message);
            $("#workorderPayModal").on("hide.bs.modal", function () {
              $("#pay_orders").attr("disabled", false);
              $("#workorderPayModal h4")
                .removeClass("text-danger")
                .text("Are you sure to proceed payment?");
            });
          } else {
            var { success_req, failed_req } = JSON.parse(res);
            var success_msg = "The below order(s) are  paid:",
              fail_msg = "The below order(s) are not paid:";
            success_req.forEach(function (elm) {
              success_msg += ` ${elm},`;
            });
            failed_req.forEach(function (elm) {
              fail_msg += ` ${elm},`;
            });
            $("#workorderPayModal h4").html(
              `<div class="text-success">${success_msg}</div> </br> <div class="text-danger">${fail_msg}</div>`
            );
            $("#workorderPayModal").on("hide.bs.modal", function () {
              window.location.href =
                "/my/freelance_workorder?filterby=confirmed";
            });
          }
        });
    });
    $("#confirm_orders").on("click", function () {
      $("#confirm_orders").attr("disabled", true);
      if ($(".orderChk:checked").length > 0) {
        $(".orderChk:checked").each(function () {
          ordersIDs.push(
            parseInt($(this).closest("tr").attr("freelance_workorder_id"))
          );
        });
      }
      $.blockUI({
        css: { backgroundColor: "transparent", border: "none" },
        message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
      });
      ajax
        .jsonRpc("/freelance/create_invoice", "call", { orderIDs: ordersIDs })
        .then(function (res) {
          $.unblockUI();
          const { status, message } = JSON.parse(res);

          if (status == "success") {
            $("#workorderConfirmModal h4")
              .addClass("text-success")
              .text(htmlLang.includes("ar")?"تم تأكيد الطلب (ات) المحدد (ة) بنجاح!":"The selected order(s) are successfully confirmed!");

            window.location.href = "/my/freelance_workorder?filterby=confirmed";
          } else if (status == "failed") {
            $("#workorderConfirmModal h4")
              .addClass("text-danger")
              .text(message);
            $("#workorderConfirmModal").on("hide.bs.modal", function () {
              $("#confirm_orders").attr("disabled", false);
              $("#workorderConfirmModal h4")
                .removeClass("text-danger")
                .text("Are you sure to confirm?");
            });
          } else {
            var { success_req, failed_req } = JSON.parse(res);
            var success_msg = htmlLang.includes("ar")?"الطلب (ات) التالية مؤكدة:":"The below order(s) are  confirmed:",
              fail_msg = htmlLang.includes("ar")?"الطلب (ات) التالية غير مؤكدة:":"The below order(s) are not confirmed:";
            success_req.forEach(function (elm) {
              success_msg += ` ${elm},`;
            });
            failed_req.forEach(function (elm) {
              fail_msg += ` ${elm},`;
            });
            $("#workorderConfirmModal h4").html(
              `<div class="text-success">${success_msg}</div> </br> <div class="text-danger">${fail_msg}</div>`
            );
            $("#workorderConfirmModal").on("hide.bs.modal", function () {
              window.location.href = "/my/freelance_workorder?filterby=draft";
            });
          }
        });
    });
  });
});

odoo.define("thiqah.freelance.ahad.request", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var core = require("web.core");

  publicWidget.registry.ahadRequestForm = publicWidget.Widget.extend({
    selector: ".ahad_freelancer_request",
    events: {
      "change .basic_change_selector": "_onChangeForm",
      "change #accept_terms": "_onChangeAcceptTerms",
      "click button[type='submit']": "_onSubmitForm",
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      //description
      var $client_name = this.$el.find('input[name="ahad_client_name"]').val(),
        $project_number = this.$el
          .find('input[name="ahad_project_number"]')
          .val(),
        $project_name = this.$el.find('input[name="ahad_project_name"]').val(),
        $request_description = this.$el
          .find('textarea[name="request_description"]')
          .val();

      if (
        $project_name &&
        $client_name &&
        $project_number &&
        $project_name &&
        $request_description
      ) {
        $('a[role="tab"]').removeClass("disabled");
        $("a.state_next_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.state_next_step").addClass("disabled");
      }
    },
    /**
     * @private
     */
    _onChangeAcceptTerms: function () {
      //description
      var $accept_terms = this.$el.find('input[name="accept_terms"]')[0]
        .checked;
      if ($accept_terms) {
        $('a[role="tab"]').removeClass("disabled");
        $("a.last_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.last_step").addClass("disabled");
      }
    },
    _onSubmitForm: function (e) {
      e.preventDefault();
      e.stopPropagation();
      
      let $entity = $("select[name='entity']").val();
      var formAhad = document.getElementById("ahad_freelance_add_form");
      $("input[name='entity_id']").val($entity);
      if (formAhad.checkValidity() !== false) {
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message:
            '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        $.ajax({
          url: "/freelance/form/add",
          method: "POST",
          data: $(formAhad).serialize(),
          success: function (response) {
            const { status, Message } = JSON.parse(response);
            if (status == "success") {
              location.href = `/my/freelance/${Message}`;
            } else {
              $.unblockUI();
              $(".request-error").removeClass("d-none").text(Message);
            }
          },
        });
      }
      $(formAhad).addClass("was-validated");
    },
  });
});
