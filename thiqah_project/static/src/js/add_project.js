// TODO : This file need more optimization
// Explanation

//--------------------------------------------------
// Basic Data
//--------------------------------------------------
odoo.define("thiqah.project.basic.data", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var _t = core._t;
  var htmlLang = $("html").attr("lang");

  publicWidget.registry.ProjectBasicData = publicWidget.Widget.extend({
    selector: ".basic_data_selector",
    events: {
      "change #basic_date": "_onChangeDate",
      "change .basic_change_selector": "_onChangeForm",
      'keypress input[name="name_arabic"]': "_onControlInputName",
      'paste input[name="name_arabic"]': "_onPreventPasteName",
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onControlInputName: function (event) {
      var arabicAlphabetDigits =
        /[\u0600-\u06ff]|[\u0750-\u077f]|[\ufb50-\ufc3f]|[\ufe70-\ufefc]|[\u0200]|[\u00A0]/g;
      /* Retrieving the key from the char code passed in event.which
                For more info on even.which, look here: http://stackoverflow.com/q/3050984/114029
                var key = String.fromCharCode(event.which); */
      var key = String.fromCharCode(event.which);

      if (
        event.keyCode == 8 ||
        event.keyCode == 37 ||
        event.keyCode == 39 ||
        key == " " ||
        arabicAlphabetDigits.test(key)
      ) {
        return true;
      }
      return false;
    },

    /**
     * @private
     */
    _onPreventPasteName: function (e) {
      e.preventDefault();
    },

    /**
     * @private
     */
    _onChangeForm: function () {
      //partner_id
      var $partner = this.$('select[name="partner_id"]');
      var $partner_id = $partner.val() || 0;

      //name(s)
      var $name = this.$('input[name="name"]').val();
      var $name_arabic = this.$('input[name="name_arabic"]').val();

      //department_id
      var $contract_type = this.$('select[name="contract_type_id"]');
      var $contract_type_id = $contract_type.val() || 0;

      //date(s)
      var $date_start = this.$('input[name="date_start"]').val();
      var $basic_date = this.$('input[name="basic_date"]').val();

      //duration
      var $duration = this.$('input[name="duration"]');
      var $duration_data = $duration.val() || 0;

      // project value
      var $project_value = this.$('input[name="project_value"]').val();

      //manager
      var $manager = this.$('select[name="user_id"]');
      var $manager_id = $manager.val() || 0;

      // if (!$partner_id == 0 && $name && $name_arabic  && $date_start && $basic_date && $duration_data && $project_value > 0){
      if (
        !$partner_id == 0 &&
        $name &&
        $name_arabic &&
        !$contract_type_id == 0 &&
        $date_start &&
        $basic_date &&
        $project_value > 0 &&
        !$manager_id == 0
      ) {
        /**Why this ???  */
        $('a[role="tab"]').removeClass("disabled");
        // $('a[role="tab"]').parent().addClass("done");
        $("a.state_next_step").removeClass("disabled");
      } else {
        $('a[role="tab"]').addClass("disabled");
        $("a.state_next_step").addClass("disabled");
      }
    },

    /**
     * @private
     */
    _onChangeDate: function () {
      var date_start = $('input[name="date_start"]').val();
      var date_end = $('input[name="basic_date"]').val();
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

          // Depending in the dates values , we will compute the duration.
          // var hourDiff = date_end - date_start;

          const date_end_ = new Date(date_end);
          const date_start_ = new Date(date_start);

          const duration = new Date(date_end).getTime() - new Date(date_start);

          const year = date_end_.getFullYear() - date_start_.getFullYear();
          const month =
            date_end_.getMonth() -
            date_start_.getMonth() +
            12 * (date_end_.getFullYear() - date_start_.getFullYear());
          // var month = date_end_.getMonth() - date_start_.getMonth()
          // var days = date_end_.getDay() - date_start_.getDay()
          $("#duration").val("Year : " + year + " Month : " + month);
        }
      }

      this._onChangeForm();
    },
  });
});

//--------------------------------------------------
// Overall Summary
//--------------------------------------------------
odoo.define("thiqah.project.overall.summary", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var _t = core._t;

  publicWidget.registry.OverallSummary = publicWidget.Widget.extend({
    selector: ".add_project_box",
    events: {
      'keypress input[name="actual_margin_percent"]':
        "_onChangeActualMarginPercent",
      'keypress input[name="margin_percent"]': "_onChangePercent",
    },

    _onChangeActualMarginPercent: function () {
      var actual_margin = $('input[name="actual_margin_percent"]').val();
      var actual_margin_percent = parseInt(actual_margin);

      if (actual_margin_percent == 10) {
        return true;
      }

      if (actual_margin_percent > 9) {
        return false;
      }
    },

    _onChangePercent: function () {
      var margin = $('input[name="margin_percent"]').val();
      var margin_percent = parseInt(margin);

      if (margin_percent == 10) {
        return true;
      } else if (margin_percent > 9) {
        return false;
      }
    },
  });
});

// odoo.define('thiqah.input.control',function(require){
//     	'use strict';

//         var publicWidget = require('web.public.widget');

//     	publicWidget.registry.TabbedForms =  publicWidget.Widget.extend({
//     		'selector' : '.tabbed-form',
//     		'events':{
//     			'keypress input[name="name_arabic"]': '_onControlInputName',
//     			'paste input[name="name_arabic"]': '_onPreventPasteName',
//     		},

//     		//--------------------------------------------------------------------------
//             // Private
//             //--------------------------------------------------------------------------

//     		/**
//     		 * @private
//     		 */
//     		_onControlInputName : function(event){
//     			var $name = $("input[name='name_arabic']").val();

//     			var arabicAlphabetDigits = /[\u0600-\u06ff]|[\u0750-\u077f]|[\ufb50-\ufc3f]|[\ufe70-\ufefc]|[\u0200]|[\u00A0]/g;
//     			/* Retrieving the key from the char code passed in event.which
//     				For more info on even.which, look here: http://stackoverflow.com/q/3050984/114029
//     				var key = String.fromCharCode(event.which); */
//     				var key = String.fromCharCode(event.which);

//     			if (event.keyCode == 8 || event.keyCode == 37 || event.keyCode == 39 || arabicAlphabetDigits.test(key)) {
//     				return true;
//     			}
//     			return false;
//     		},

//     		/**
//     		 * @private
//     		 */
//     		 _onPreventPasteName : function(e){
//     			e.preventDefault();
//     		},

//     	});

//     });

//--------------------------------------------------
// Project Resources
//--------------------------------------------------

odoo.define("thiqah.resources", function (require) {
  "use strict";

  // Event Delegation : Event delegation allows us to attach a single event listener, to a parent element,
  // that will fire for all descendants matching a selector, whether those descendants exist now or are added in the future.
  // https://learn.jquery.com/events/event-delegation/

  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var _t = core._t;

  var rowIdx = 0;
  const resource_names = [];
  const resource_ids = [];

  publicWidget.registry.ResourcesProjectWIdget = publicWidget.Widget.extend({
    selector: ".project_resources",
    events: {
      "click #add_project_resource": "_onAddRow",
      "click #table_resources_body .remove": "_onDeleteRow", // Event Delegation.
      'change select[name="resource_user_id"]': "_onChangeUser",
    },
    /**
     * @override
     */
    start: function () {
      var result = this._super.apply(this, arguments);
      this.$("#add_project_resource").attr("disabled", "disabled");
      $("#resourcesDiv").hide();
      return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onChangeUser: function () {
      var $user_id = this.$('select[name="resource_user_id"]').val();
      var $add_resource_button = this.$("#add_project_resource");
      if (!$user_id) {
        $add_resource_button.attr("disabled", "disabled");
      } else {
        $add_resource_button.removeAttr("disabled");
      }
    },

    /**
     * @private
     */
    _onAddRow: function () {
      var self = this;
      var $btn = this.$(".project_resources #add_project_resource");
      $btn.removeAttr("disabled");
      // Gathering data
      var resource_number = this.$('input[name="resource_number"]').val();
      var department = this.$(
        'select[name="resource_department_id"] option:selected'
      ).text();
      var department_id = this.$('select[name="resource_department_id"]').val();
      var dep_select = this.$('select[name="resource_department_id"]');
      var user = this.$(
        'select[name="resource_user_id"] option:selected'
      ).text();
      var user_select = this.$('select[name="resource_user_id"]');
      var user_id = this.$('select[name="resource_user_id"]').val();

      var other = this.$('input[name="resource_other"]').val();
      if (department_id && user_id) {
        if (!resource_names.includes(user)) {
          $(".project_resources #info_state")
            .removeClass("alert-danger")
            .addClass("d-none");
        }

        // Ensure that the resource was added once.
        else if (resource_names.includes(user)) {
          $(".project_resources #details_info").text(
            _t("You have already added this resource.")
          );
          $(".project_resources #info_state")
            .removeClass("d-none alert-success")
            .addClass("text-danger heading-7");
          $("#addResourceModal").on("hidden.bs.modal", function () {
            $(".project_resources #info_state").addClass("d-none");
          });
          return false;
        }

        // Need to insert this.record into thiqah.project.resource
        this._rpc({
          model: "thiqah.project.resource",
          method: "create",
          args: [
            {
              name: user,
              resource_number: resource_number,
              department_id: parseInt(department_id),
              user_id: parseInt(user_id),
              other_resource: other,
              resource_type: "user",
            },
          ],
        }).then(function (result) {
          if (result > 0) {
            // fill resource_names to avoid duplcated resource.
            resource_names.push(user);
            self.$(".placeholder-card").hide();
            $("#resourcesDiv").show();
            // set resource_ids value
            resource_ids.push(parseInt(result));
            self.$("#addResourceModal input").each(function () {
              $(this).val("");
            });
            $("#addResourceModal").modal("hide");
            $('input[name="resource_ids"]').val(
              "[(6,0,[" + resource_ids + "])]"
            );

            user_select.val(false).trigger("change");
            dep_select.val(false).trigger("change");

            // Adding a row inside the tbody.
            $("#table_resources_body").append(`
                            <tr id="R${++rowIdx}" user="${user}" resource-id="${parseInt(
              result
            )}">
                                <td class="row-index">
                                    <p>${resource_number}</p>
                                </td>
                                <td class="row-index">
                                    <p>${department}</p>
                                </td>
                                <td class="row-index">
                                    <p>${user}</p>
                                </td>
                                <td class="row-index">
                                    <p>${other}</p>
                                </td>
                                <td class="td-actions text-center">
                                    <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
                                    <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
                                  </svg></button>
                                </td>
                            </tr>`);
          }
        });
      } else {
        // Disable ADD Button
        $btn.attr("disabled", "disabled");
      }
    },

    /**
     * @private
     */
    _onDeleteRow: function (event) {
      var user = $(event.target).closest("tr").attr("user");
      var resource_id = $(event.target).closest("tr").attr("resource-id");
      var user_index = resource_names.indexOf(user);
      var resource_index = resource_ids.indexOf(resource_id);

      // delete the current data from resource names and resource ids to avoid the previous test without any need.
      resource_names.splice(user_index, 1);
      resource_ids.splice(resource_index, 1);

      $(event.target).closest("tr").remove();
      if (resource_ids.length == 0) {
        this.$(".placeholder-card").show();
        $("#resourcesDiv").hide();
      }
    },
  });
});

//--------------------------------------------------
// Risk and issues
//--------------------------------------------------
odoo.define("thiqah.risk.issues", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var thiqahUtils = require("thiqah.utils");
  var core = require("web.core");
  var _t = core._t;

  var rowIdx = 0;
  const risk_names = [];
  const risk_ids = [];
  var name_risk = "";

  publicWidget.registry.RiskProjectWidget = publicWidget.Widget.extend({
    selector: ".project_risk",
    events: {
      "click #add_project_risk": "_onAddRow",
      "click #table_risk_body .remove": "_onDeleteRow", // Event Delegation.
      'change input[name="name_risk"]': "onChangeRiskName",
    },

    /**
     * @override
     */
    start: function () {
      var result = this._super.apply(this, arguments);
      this.$("#add_project_risk").attr("disabled", "disabled");
      $("#riskIssuesDiv").hide();
      return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    onChangeRiskName: function () {
      var $name_risk = this.$('input[name="name_risk"]').val();
      var $add_risk_button = this.$("#add_project_risk");

      if (!$name_risk) {
        $add_risk_button.attr("disabled", "disabled");
      } else {
        $add_risk_button.removeAttr("disabled");
      }
    },

    /**
     * @private
     */
    _onAddRow: function () {
      var self = this;
      // Gathering data
      var risk_number = this.$('input[name="risk_number"]').val();
      name_risk = this.$('input[name="name_risk"]').val();
      var description_risk = this.$('textarea[name="description_risk"]').val();
      var risk_type = this.$(
        'select[name="risk_type_id"] option:selected'
      ).text();
      var risk_type_id = this.$('select[name="risk_type_id"]').val();

      var owner = this.$('input[name="owner"]').val();
      var corrective_action = this.$(
        'textarea[name="corrective_action"]'
      ).val();

      var level_impact = this.$(
        'select[name="level_impact"] option:selected'
      ).text();
      var level_impact_key = this.$('select[name="level_impact"]').val();

      var risk_status = this.$(
        'select[name="risk_status"] option:selected'
      ).text();
      var risk_status_key = this.$('select[name="risk_status"]').val();

      if (
        name_risk &&
        description_risk &&
        risk_type_id &&
        owner &&
        corrective_action &&
        level_impact_key &&
        risk_status_key
      ) {
        if (!risk_names.includes(name_risk)) {
          $(".project_risk #info_state")
            .removeClass("alert-danger")
            .addClass("d-none");
        }

        // Ensure that the resource was added once.
        if (risk_names.includes(name_risk)) {
          $(".project_risk #details_info").text(
            _t("You have already added this risk.")
          );
          $(".project_risk #info_state")
            .removeClass("d-none alert-success")
            .addClass("text-danger heading-7");
          $("#addRiskIssuesModal").on("hidden.bs.modal", function () {
            $(".project_resources #info_state").addClass("d-none");
          });
          return false;
        }

        // Need to insert this.record into thiqah.project.risk
        this._rpc({
          model: "thiqah.project.risk",
          method: "create",
          args: [
            {
              risk_number: risk_number,
              name: name_risk,
              description: description_risk,
              owner: owner,
              corrective_action: corrective_action,
              level_impact: level_impact_key,
              risk_status: risk_status_key,
              risk_type_id: parseInt(risk_type_id),
            },
          ],
        }).then(function (result) {
          if (result > 0) {
            self.$(".placeholder-card").hide();
            $("#riskIssuesDiv").show();
            // fill resource_names to avoid duplcated risks.
            risk_names.push(name_risk);

            // set resource_ids value
            risk_ids.push(parseInt(result));

            self
              .$(
                "#addRiskIssuesModal input,#addRiskIssuesModal textarea,#addRiskIssuesModal select"
              )
              .each(function () {
                $(this).val("");
              });
            $('input[name="risk_ids"]').val("[(6,0,[" + risk_ids + "])]");
            $("#addRiskIssuesModal").modal("hide");
            // Adding a row inside the tbody.
            $("#table_risk_body").append(`
                            <tr id="R${++rowIdx}" name-risk="${name_risk}" risk-id="${parseInt(
              result
            )}">
                                <td class="row-index">
                                    <p>${risk_number}</p>
                                </td>
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
                                <td class="td-actions text-center">
                                    <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
                                    <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
                                  </svg></button>
                                </td>
                            </tr>`);
          }
        });
      }
    },

    /**
     * @private
     */
    _onDeleteRow: function (event) {
      thiqahUtils._deleteRow(
        event,
        "name-risk",
        "risk-id",
        risk_names,
        risk_ids,
        "thiqah.project.risk",
        ".project_risk #info_state"
      );
      if (risk_ids.length == 0) {
        this.$(".placeholder-card").show();
        $("#riskIssuesDiv").hide();
      }
    },
  });
});

//--------------------------------------------------
// Revenue Plans
//--------------------------------------------------
odoo.define("thiqah.revenue.plans", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var thiqahUtils = require("thiqah.utils");
  var core = require("web.core");
  var _t = core._t;

  var rowIdx = 0;
  const invoice_dates = [];
  const revenue_ids = [];
  var invoice_date = "";

  publicWidget.registry.RevenuePlanProjectWidget = publicWidget.Widget.extend({
    selector: ".project_revenue_plans",
    events: {
      "click #add_revenue_plan": "_onAddRow",
      "click #table_revenue_body .remove": "_onDeleteRow", // Event Delegation.
      'change input[name="invoice_date"]': "onChangeInvoiceDate",
    },

    // TODO : set ADD | next buttons disabled if the fields are empty.

    /**
     * @override
     */
    start: function () {
      var result = this._super.apply(this, arguments);
      this.$("#add_revenue_plan").attr("disabled", "disabled");
      $("#revenueDiv").hide();
      return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    onChangeInvoiceDate: function () {
      var $invoice_date = this.$('input[name="invoice_date"]').val();
      var $add_revenue_button = this.$("#add_revenue_plan");
      if (!$invoice_date) {
        $add_revenue_button.attr("disabled", "disabled");
      } else {
        $add_revenue_button.removeAttr("disabled");
      }
    },

    /**
     * @private
     */
    _onAddRow: function () {
      var self = this;
      // Gathering data
      var invoice_number = this.$('input[name="invoice_number"]').val();
      var invoice_date = this.$('input[name="invoice_date"]').val();
      var payment_date = this.$('input[name="payment_date"]').val();
      var amount_billed = this.$('input[name="amount_billed"]').val();
      var amount_received = this.$('input[name="amount_received"]').val();
      // var amount_due = this.$('input[name="amount_due"]').val();
      var revenue_plan_status = this.$(
        'select[name="revenue_plan_status"] option:selected'
      ).text();
      var revenue_plan_status_key = this.$(
        'select[name="revenue_plan_status"]'
      ).val();

      if (
        invoice_date &&
        payment_date &&
        amount_billed &&
        amount_received &&
        // amount_due &&
        revenue_plan_status
      ) {
        if (!invoice_dates.includes(invoice_date)) {
          $(".project_revenue_plans #info_state")
            .removeClass("alert-danger")
            .addClass("d-none");
        }

        // Ensure that the resource was added once.
        if (invoice_dates.includes(invoice_date)) {
          $(".project_revenue_plans #details_info").text(
            _t("You have already added this revenue plan.")
          );
          $(".project_revenue_plans #info_state")
            .removeClass("d-none alert-success")
            .addClass("text-danger heading-7");
          $("#addRvenueModal").on("hidden.bs.modal", function () {
            $(".project_resources #info_state").addClass("d-none");
          });
          return false;
        }

        // Need to insert this.record into thiqah.project.resource
        this._rpc({
          model: "thiqah.revenue.plan",
          method: "create",
          args: [
            {
              invoice_number: invoice_number,
              invoice_date: invoice_date,
              payment_date: payment_date,
              amount_billed: amount_billed,
              amount_received: amount_received,
              // amount_due: amount_due,
              status: revenue_plan_status_key,
            },
          ],
        }).then(function (result) {
          if (result > 0) {
            // fill resource_names to avoid duplcated resource.
            self.$(".placeholder-card").hide();
            $("#revenueDiv").show();
            invoice_dates.push(invoice_date);
            // set resource_ids value
            revenue_ids.push(parseInt(result));

            self.$("#addRvenueModal input").each(function () {
              $(this).val("");
            });
            $('input[name="revenue_plan_ids"]').val(
              "[(6,0,[" + revenue_ids + "])]"
            );

            $("#addRvenueModal").modal("hide");
            // Adding a row inside the tbody.
            $("#table_revenue_body").append(`
                            <tr id="R${++rowIdx}" invoice-date="${invoice_date}" revenue-plan-id="${parseInt(
              result
            )}">
                                <td class="row-index">
                                    <p>${invoice_number}</p>
                                </td>
                                <td class="row-index">
                                    <p>${invoice_date}</p>
                                </td>
                                <td class="row-index">
                                    <p>${payment_date}</p>
                                </td>
                                <td class="row-index text-right">
                                    <p>${amount_billed}</p>
                                </td>
                                <td class="row-index text-right">
                                    <p>${amount_received}</p>
                                </td>
                               
                                <td class="row-index">
                                    <p>${revenue_plan_status}</p>
                                </td>
                                <td class="td-actions text-center">
                                    <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
                                    <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
                                  </svg></button>
                                </td>
                            </tr>`);
          }
        });
      }
    },

    /**
     * @private
     */
    _onDeleteRow: function (event) {
      thiqahUtils._deleteRow(
        event,
        "invoice-date",
        "revenue-plan-id",
        invoice_dates,
        revenue_ids,
        "thiqah.revenue.plan",
        ".project_revenue_plans #info_state"
      );
      if (revenue_ids.length == 0) {
        this.$(".placeholder-card").show();
        $("#revenueDiv").hide();
      }
    },
  });
});

//--------------------------------------------------
// Deliverables
//--------------------------------------------------

odoo.define("thiqah.project.deliverables", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var thiqahUtils = require("thiqah.utils");
  var core = require("web.core");
  var _t = core._t;

  var rowIdx = 0;
  const deliverable_names = [];
  const deliverable_ids = [];

  publicWidget.registry.DeliverablestWidget = publicWidget.Widget.extend({
    selector: ".project_deliverable",
    events: {
      "click #add_deliverable": "_onAddRow",
      "click #table_deliverable_body .remove": "_onDeleteRow", // Event Delegation.
      'change input[name="deliverable_name"]': "_onChangeDeliverableName",
      'change select[name="deliverable_progress"]':
        "_onChangeDeliverableProgress",
    },

    /**
     * @override
     */
    start: function () {
      var result = this._super.apply(this, arguments);
      this.$("#add_deliverable").attr("disabled", "disabled");

      var $currentValue = $("#deliverable_progress").val();
      $("#deliverableValueOutput").text($currentValue + "%");
      $("#deliverablesDiv").hide();
      return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onChangeDeliverableProgress: function () {
      var $currentValue = $("#deliverable_progress").val();
      $("#deliverableValueOutput").text($currentValue + "%");
      var $deliverable_name = this.$('input[name="deliverable_name"]').val();
      var $add_deliverable = this.$("#add_deliverable");

      if (!$deliverable_name) {
        $add_deliverable.attr("disabled", "disabled");
      } else {
        $add_deliverable.removeAttr("disabled");
      }
    },

    /**
     * @private
     */
    _onChangeDeliverableName: function () {
      var $deliverable_name = this.$('input[name="deliverable_name"]').val();
      var $add_deliverable = this.$("#add_deliverable");

      if (!$deliverable_name) {
        $add_deliverable.attr("disabled", "disabled");
      } else {
        $add_deliverable.removeAttr("disabled");
      }
    },

    /**
     * @private
     */
    _onAddRow: function () {
      var self = this;
      // Gathering data
      var deliverable_number = this.$('input[name="deliverable_number"]').val();
      var deliverable_name = this.$('input[name="deliverable_name"]').val();
      var deliverable_progress = this.$(
        'select[name="deliverable_progress"]'
      ).val();
      var deliverable_due_date = this.$(
        'input[name="deliverable_due_date"]'
      ).val();
      var deliverable_status_key = this.$(
        'select[name="deliverable_status"]'
      ).val();
      var deliverable_status = this.$(
        'select[name="deliverable_status"] option:selected'
      ).text();
      var deliverable_delivered_date = this.$(
        'input[name="deliverable_delivered_date"]'
      ).val();
      console.log(deliverable_progress);
      if (
        deliverable_name &&
        deliverable_due_date &&
        deliverable_status &&
        deliverable_delivered_date
      ) {
        if (!deliverable_names.includes(deliverable_name)) {
          $(".project_deliverable #info_state")
            .removeClass("alert-danger")
            .addClass("d-none");
        }

        // Ensure that the resource was added once.
        else if (deliverable_names.includes(deliverable_name)) {
          $(".project_deliverable #details_info").text(
            _t("You have already added this deliverable.")
          );
          $(".project_deliverable #info_state")
            .removeClass("d-none alert-success")
            .addClass("text-danger heading-7");
          $("#addDeliverablesModal").on("hidden.bs.modal", function () {
            $(".project_resources #info_state").addClass("d-none");
          });
          return false;
        }

        // Need to insert this.record into thiqah.project.resource
        this._rpc({
          model: "thiqah.project.deliverable",
          method: "create",
          args: [
            {
              deliverable_number: deliverable_number,
              name: deliverable_name,
              progress_percent: parseInt(deliverable_progress),
              due_date: deliverable_due_date,
              delivered_date: deliverable_delivered_date,
              status: deliverable_status_key,
            },
          ],
        }).then(function (result) {
          if (result > 0) {
            // fill resource_names to avoid duplcated resource.
            deliverable_names.push(deliverable_name);
            self.$(".placeholder-card").hide();
            $("#deliverablesDiv").show();
            // set resource_ids value
            deliverable_ids.push(parseInt(result));

            self.$("#addDeliverablesModal input").each(function () {
              $(this).val("");
            });
            $('input[name="deliverable_ids"]').val(
              "[(6,0,[" + deliverable_ids + "])]"
            );
            $("#addDeliverablesModal").modal("hide");
            // Adding a row inside the tbody.
            $("#table_deliverable_body").append(`
                            <tr id="R${++rowIdx}" deliverable_name="${deliverable_name}" deliverable-id="${parseInt(
              result
            )}">>
                                
                                <td class="row-index">
                                    <p>${deliverable_number}</p>
                                </td>
                                <td class="row-index">
                                    <p>${deliverable_name}</p>
                                </td>
                                <td class="row-index">
                                    <p>${deliverable_progress}%</p>
                                </td>
                                <td class="row-index">
                                    <p>${deliverable_due_date}</p>
                                </td>
                                <td class="row-index">
                                    <p>${deliverable_delivered_date}</p>
                                </td>
                                <td class="row-index">
                                    <p>${deliverable_status}</p>
                                </td>
                                <td class="td-actions text-center">
                                  <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
                                    <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
                                    </svg>
                                  </button>
                                </td>
                            </tr>`);
          }
        });
      }
    },

    /**
     * @private
     */
    _onDeleteRow: function (event) {
      thiqahUtils._deleteRow(
        event,
        "deliverable_name",
        "deliverable-id",
        deliverable_names,
        deliverable_ids,
        "thiqah.project.deliverable",
        ".project_deliverable #info_state"
      );
      if (deliverable_ids.length == 0) {
        this.$(".placeholder-card").show();
        $("#deliverablesDiv").hide();
      }
    },
  });
});

// --------------------------------------------------
// Utilizations
// --------------------------------------------------
odoo.define("thiqah.project.utilizations", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var thiqahUtils = require("thiqah.utils");
  var core = require("web.core");
  var _t = core._t;

  var rowIdx = 0;
  const utilization_names = [];
  const utilization_ids = [];

  publicWidget.registry.ProjectUtilizationstWidget = publicWidget.Widget.extend(
    {
      selector: ".project_utilization",
      events: {
        "click #add_project_utilization": "_onAddRow",
        "click #table_utilizations_body .remove": "_onDeleteRow", // Event Delegation.
        'change input[name="planned_hours"]': "_onChangePlannedHours",
      },

      /**
       * @override
       */
      start: function () {
        var result = this._super.apply(this, arguments);
        this.$("#add_project_utilization").attr("disabled", "disabled");
        $("#utilizationDiv").hide();
        return result;
      },

      //--------------------------------------------------------------------------
      // Private
      //--------------------------------------------------------------------------

      /**
       * @private
       */
      _onChangePlannedHours: function () {
        var $planned_hours = this.$('input[name="planned_hours"]').val();
        var $add_project_utilization = this.$("#add_project_utilization");

        if (!$planned_hours) {
          $add_project_utilization.attr("disabled", "disabled");
        } else {
          $add_project_utilization.removeAttr("disabled");
        }
      },

      /**
       * @private
       */
      _onAddRow: function () {
        var self = this;
        // Gathering data
        var utilization_number = this.$(
          'input[name="utilization_number"]'
        ).val();
        var planned_hours = this.$('input[name="planned_hours"]').val();
        var actual_hours = this.$('input[name="actual_hours"]').val();
        var forecasted_hours = this.$('input[name="forecasted_hours"]').val();

        if (planned_hours && actual_hours && forecasted_hours) {
          if (!utilization_names.includes(planned_hours)) {
            $(".project_utilization #info_state")
              .removeClass("alert-danger")
              .addClass("d-none");
          }

          // Ensure that the resource was added once.
          else if (utilization_names.includes(planned_hours)) {
            $(".project_utilization #details_info").text(
              _t("You have already added this utilization.")
            );
            $(".project_utilization #info_state")
              .removeClass("d-none alert-success")
              .addClass("text-danger heading-7");
            $("#addUtilizationModal").on("hidden.bs.modal", function () {
              $(".project_resources #info_state").addClass("d-none");
            });
            return false;
          }
          this._rpc({
            model: "thiqah.project.utilization",
            method: "create",
            args: [
              {
                utilization_number: utilization_number,
                planned_hours: planned_hours,
                actual_hours: actual_hours,
                forecasted_hours: forecasted_hours,
              },
            ],
          }).then(function (result) {
            if (result > 0) {
              // fill resource_names to avoid duplcated utilization.
              utilization_names.push(planned_hours);

              // set resource_ids value
              utilization_ids.push(parseInt(result));
              self.$("#addUtilizationModal input").each(function () {
                $(this).val("");
              });
              $('input[name="utilization_ids"]').val(
                "[(6,0,[" + utilization_ids + "])]"
              );
              self.$(".placeholder-card").hide();
              $("#utilizationDiv").show();

              $("#addUtilizationModal").modal("hide");
              // Adding a row inside the tbody.
              $("#table_utilizations_body").append(`
                            <tr id="R${++rowIdx}" deliverable_name="${planned_hours}" utilization-id="${parseInt(
                result
              )}">>
                                <td class="row-index">
                                    <p>${utilization_number}</p>
                                </td>
                                <td class="row-index">
                                    <p>${planned_hours}</p>
                                </td>
                                <td class="row-index">
                                    <p>${actual_hours}</p>
                                </td>
                                <td class="row-index">
                                    <p>${forecasted_hours}</p>
                                </td>
                                <td class="td-actions text-center">
                                  <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
                                    <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
                                    </svg>
                                  </button>
                                </td>
                            </tr>`);
            }
          });
        }
      },

      /**
       * @private
       */
      _onDeleteRow: function (event) {
        thiqahUtils._deleteRow(
          event,
          "planned_hours",
          "utilization-id",
          utilization_names,
          utilization_ids,
          "thiqah.project.utilization",
          ".project_utilization #info_state"
        );
        if (utilization_ids.length == 0) {
          this.$(".placeholder-card").show();
          $("#utilizationDiv").hide();
        }
      },
    }
  );
});

// --------------------------------------------------
// Documents
// --------------------------------------------------
odoo.define("thiqah.project.documents", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var thiqahUtils = require("thiqah.utils");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var _t = core._t;

  var rowIdx = 0;
  const document_names = [];
  const document_ids = [];

  publicWidget.registry.UtilizationstWidget = publicWidget.Widget.extend({
    selector: ".project_documents",
    events: {
      "click #add_project_document": "_onAddRow",
      "click #table_documents_body .remove": "_onDeleteRow", // Event Delegation.
      'change select[name="document_type_id"]': "_onChangeDocumentType",
    },

    /**
     * @constructor
     */
    init: function (parent, options) {
      this._super.apply(this, arguments);
      this.options = _.defaults(options || {}, {
        csrf_token: odoo.csrf_token,
        token: false,
        res_model: false,
        res_id: false,
      });
    },

    /**
     * @override
     */
    start: function () {
      var result = this._super.apply(this, arguments);

      this.$fileInput = this.$(".o_portal_file_input");
      this.$add_project_document = this.$("#add_project_document");
      this.$add_project_document.prop("disabled", true);
      this.$(".project_details_table").hide();

      return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _prepareDocumentData: function (file) {
      return {
        name: file.name,
        file: file,
        res_id: this.options.res_id,
        res_model: this.options.res_model,
        access_token: this.options.token,
      };
    },

    /**
     * @private
     */
    _onChangeDocumentType: function () {
      var $document_type = this.$('select[name="document_type_id"]').val();
      var $add_project_document = this.$("#add_project_document");

      if (!$document_type) {
        $add_project_document.attr("disabled", "disabled");
      } else {
        $add_project_document.removeAttr("disabled");
      }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onAddRow: function () {
      var self = this;
      // Gathering data
      var document_type_id = this.$('select[name="document_type_id"]').val();
      var document_type = this.$(
        'select[name="document_type_id"] option:selected'
      ).text();
      var document_name = this.$('input[name="document_name"]').val();
      var document_description = this.$(
        'textarea[name="document_description"]'
      ).val();

      if (document_type_id && document_name && document_description) {
        if (!document_names.includes(document_name)) {
          $(".project_documents #info_state")
            .removeClass("alert-danger")
            .addClass("d-none");
        }

        // Ensure that the resource was added once.
        else if (document_names.includes(document_name)) {
          $(".project_documents #details_info").text(
            _t("You have already added this document.")
          );
          $(".project_documents #info_state")
            .removeClass("d-none alert-success")
            .addClass("text-danger heading-7");
          $("#addDocumentsModal").on("hidden.bs.modal", function () {
            $(".project_resources #info_state").addClass("d-none");
          });
          return false;
        }

        return Promise.all(
          _.map(this.$fileInput[0].files, function (file) {
            return new Promise(function (resolve, reject) {
              var data = self._prepareDocumentData(file);
              ajax
                .post("/project/document/add", data)
                .then(function (result) {
                  if (result == "unauthorized") {
                    $(".project_documents #details_info").text(
                      _t(
                        "you don't have permission. Contact your administrator."
                      )
                    );
                    $(".project_documents #info_state")
                      .removeClass("d-none alert-success")
                      .addClass("text-danger heading-7");
                  } else if (result) {
                    // fill resource_names to avoid duplcated document.
                    document_names.push(document_name);
                    document_ids.push(parseInt(result["id"]));
                    self
                      .$('select[name="document_type_id"]')
                      .val(false)
                      .trigger("change");
                    $('input[name="documents_ids"]').val(document_ids);
                    self
                      .$("#addDocumentsModal input,#addDocumentsModal textarea")
                      .each(function () {
                        $(this).val("");
                      });
                    self.$(".placeholder-card").hide();
                    self.$(".project_details_table").show();
                    $('input[name="documents_ids"]').val(
                      "[(6,0,[" + document_ids + "])]"
                    );

                    $("#addDocumentsModal").modal("hide");
                    // Adding a row inside the tbody.
                    $("#table_documents_body").append(`
                                <tr id="R${++rowIdx}" document-name="${document_name}" document-id="${parseInt(
                      result["id"]
                    )}">>
                                    <td class="row-index">
                                      ${data["name"]}
                                    </td>
                                    <td class="row-index">
                                      ${document_type}
                                    </td>
                                    <td class="row-index">
                                        ${document_description}
                                    </td>
                                    <td class="td-actions text-center">
                                    <button class="btn btn-circle p-0 remove t-custom-bg-dark-gray" style="width:32px;height:32px" type="button"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="15" fill="none">
                                      <path fill="#fff" d="M3.853 3.04h1.058V1.617c0-.38.266-.626.665-.626h2.382c.4 0 .665.246.665.626V3.04h1.058V1.55C9.681.585 9.056 0 8.031 0H5.503c-1.024 0-1.65.585-1.65 1.55v1.49Zm-3.02.533h11.889a.503.503 0 0 0 0-1.005H.832a.507.507 0 0 0-.498.499c0 .28.233.506.499.506Zm2.894 11.243h6.1c.952 0 1.59-.619 1.637-1.57l.466-9.8h-1.071l-.446 9.687c-.013.399-.3.678-.692.678h-5.9c-.38 0-.666-.286-.686-.678l-.473-9.687H1.618l.472 9.806c.047.952.672 1.564 1.637 1.564Zm1.078-2.142c.252 0 .419-.16.412-.393l-.206-7.118c-.007-.233-.173-.386-.413-.386-.252 0-.419.16-.412.392l.2 7.112c.006.24.173.393.419.393Zm1.969 0c.253 0 .432-.16.432-.393V5.17c0-.233-.18-.392-.432-.392-.253 0-.426.16-.426.392v7.112c0 .233.173.393.426.393Zm1.976 0c.24 0 .406-.153.412-.393l.2-7.112c.007-.233-.16-.392-.413-.392-.24 0-.405.153-.412.392l-.2 7.112c-.006.233.16.393.413.393Z"/>
                                      </svg>
                                    </button>
                                  </td>
                                </tr>`);

                    resolve();
                  }
                })
                .guardedCatch(function (error) {
                  self.displayNotification({
                    message: _.str.sprintf(
                      _t("Could not save file : %s"),
                      _.escape(file.name)
                    ),
                    type: "warning",
                    sticky: true,
                  });
                  resolve();
                });
            });
          })
        ).then(function () {
          self.$add_project_document.prop("disabled", false);
        });
      }
    },

    /**
     * @private
     */
    _onDeleteRow: function (event) {
      thiqahUtils._deleteRow(
        event,
        "document-name",
        "document-id",
        document_names,
        document_ids,
        "documents.document",
        ".project_documents #details_info"
      );
      if (document_ids.length == 0) {
        this.$(".placeholder-card").show();
        this.$(".project_details_table").hide();
      }
    },
  });
});

odoo.define("thiqah.project.form.submit", function (require) {
  "use strict";

  $("#project_add_form").on("submit", function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (this.checkValidity() !== false) {
      $.ajax({
        url: "/project/form/add",
        method: "POST",
        data: $(this).serialize(),
        success: function (response) {
          const res = JSON.parse(response);
          if(res["status"] == "success"){
            $(".proj-name").text(res["Message"]);
            $("#projectAddSuccessModal").modal({
              show: true,
              keyboard: false,
              backdrop: "static",
            });
          } else{
            
          }
          
        },
        error: function (error) {
          // Handle error here
          console.log(error);
        },
      });
    }
    $(this).addClass("was-validated");
  });
});
