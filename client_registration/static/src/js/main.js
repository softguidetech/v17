odoo.define("client.registration.request", function (require) {
  "use strict";
  var core = require("web.core");
  var _t = core._t;
  var publicWidget = require("web.public.widget");
  var htmlLang = $("html").attr("lang");
  var Utils = require("thiqah.Utils");
  var ajax = require("web.ajax");

  publicWidget.registry.ClientRegistartionForm = publicWidget.Widget.extend({
    selector: "#registerClientInfoModal",
    events: {
      "keyup #client_name": "_onKeyupClientName",
      "click .create_client": "_onCreateClientForm",
      "change #bank_country": "_onChangeBankCountry",
      "change #bank": "_onchangeBank",
      "click .create_client_bank": "_onClickCreateBank",
      "click input[name='pay_category']": "_onClickChoosePayCategory",
      "click button[data-dismiss='modal']": "_onModalClose",
      "change #iban": "_onchangeIBAN",
    },
    /**
     * @private
     */
    _onKeyupClientName: function (e) {
      if ($(e.target).val().length == 15) {
        $("#clientNameLength").removeClass("text-muted");
        $("#clientNameLength").addClass("text-danger");
      } else {
        $("#clientNameLength").removeClass("text-danger");
        $("#clientNameLength").addClass("text-muted");
      }
    },

    /**
     * @private
     */
    _onModalClose: function (e) {
      $("#registerClientInfoModal").on("hidden.bs.modal", function (e) {
        $(".categ").attr(
          "style",
          "transform: translateX(0%) !important;trasition: all 0.5s"
        );
        $("input[name='client_payment_category']").val("");
        $(".emazad-individual").addClass("d-none");
        $(".emazad-company").addClass("d-none");
        $(".to-be-modif").addClass("col-sm-4").removeClass("col-sm-6");
        $("form.needs-validation").removeClass("was-validated");
        $(".custom-input-file").removeClass("border-danger");
        $("#client_register_attach_error").addClass("d-none");
        $(".legal").removeClass("d-none");
      });
    },

    /**
     * @private
     */
    _onCreateClientForm: async function (e) {
      e.preventDefault();
      e.stopPropagation();
      let vals = {};
      $("#create_client_form input")
        .not("[type='file']")
        .not("[type='hidden']")
        .not("[type='search']")
        .each(function (idx, el) {
          vals[$(el).attr("name")] = $(el).val();
        });
      var isAttchmentsValid = false,
        clientPaymentCategory = $(
          "input[name='client_payment_category']"
        ).val();

      if (
        clientPaymentCategory == "saso" &&
        $("#client_register_attachments")[0].files.length >= 3
      ) {
        isAttchmentsValid = true;
      }
      if (
        clientPaymentCategory == "emazad_company" &&
        $("#client_register_attachments")[0].files.length >= 1
      ) {
        isAttchmentsValid = true;
      }
      if (
        clientPaymentCategory == "emazad_individual" &&
        $("#client_register_attachments")[0].files.length >= 1
      ) {
        isAttchmentsValid = true;
      }

      if (
        document.querySelector("#create_client_form").checkValidity() &&
        isAttchmentsValid
      ) {
        var client_register_attachments = $("#create_client_form input[name='client_register_attachments']")[0]
          .files;

        vals["client_register_attachments"] = await this.convert2DataUrl(client_register_attachments);
        vals["client_payment_category"] = $(
          "input[name='client_payment_category']"
        ).val();
        $("#create_client_form").removeClass("was-validated");
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        this._rpc({
          route: "/client_registration/create",
          params: vals,
        }).then(function (res) {
          const { status, client_registration_id } = res;
          if (status === "success") {
            $.unblockUI();
            $("#create_client_form").addClass("d-none");
            $(".bank_creation").removeClass("d-none");
            // $(".finish").removeClass("d-none");
            // $(".client-info").addClass("d-none");
            $(".create_client_error").addClass("d-none");
            $("input[name='client_reg_id']").val(client_registration_id);
          } else {
            $.unblockUI();
            const { message } = JSON.parse(res);
            $(".create_client_error").removeClass("d-none").text(message);
          }
        });
      } else {
        $("#create_client_form").addClass("was-validated");
        $(".custom-input-file").addClass("border-dashed border-danger");
        if (
          $("#client_payment_category").val() == "saso" &&
          $("#client_register_attachments")[0].files.length < 6
        ) {
          $("#client_register_attach_error")
            .removeClass("d-none")
            .text(
              htmlLang.includes("ar")
                ? "يرجى تحميل كافة المرفقات المطلوبة (3 ملفات)!"
                : "Please upload all required attachments (3 files)!"
            );
          $(".custom-input-file").addClass("border-dashed border-danger");
        }
        if (
          $("#client_payment_category").val() == "emazad_company" &&
          $("#client_register_attachments")[0].files.length < 2
        ) {
          $("#client_register_attach_error")
            .removeClass("d-none")
            .text(
              htmlLang.includes("ar")
                ? "يرجى تحميل جميع المرفقات المطلوبة (ملف واحد)!"
                : "Please upload all required attachments (1 file)!"
            );
          $(".custom-input-file").addClass("border-dashed border-danger");
        }
        if (
          $("#client_payment_category").val() == "emazad_individual" &&
          $("#client_register_attachments")[0].files.length < 1
        ) {
          $("#client_register_attach_error")
            .removeClass("d-none")
            .text(
              htmlLang.includes("ar")
                ? "يرجى تحميل جميع المرفقات المطلوبة (ملف واحد)!"
                : "Please upload all required attachments (1 file)!"
            );
          $(".custom-input-file").addClass("border-dashed border-danger");
        }
      }
    },

    /**
     * @private
     */
    _onClickChoosePayCategory: function (e) {
      $("input[name='client_payment_category']").val(e.target.value);
      $(".categ").attr(
        "style",
        "transform: translateX(-100%) !important; transition: all 0.5s"
      );
      var saso_attachments_list = [
        htmlLang.includes("ar") ? "إعتراف" : "Acknowledgement",
        // htmlLang.includes("ar") ? "فواتير" : "Invoices",
        htmlLang.includes("ar")
          ? "شهادة ضريبية أو إعفاء ضريبي"
          : "Tax certificate or tax exemption",
        htmlLang.includes("ar") ? "السجل التجاري" : "Commercial registration",
        htmlLang.includes("ar")
          ? "نسخة من نموذج معلومات الحساب البنكي"
          : "A copy of the bank account information form",
        // htmlLang.includes("ar")
        //   ? "ملف Excel للعمليات"
        //   : "The Excel file for operations",
      ],
        emazad_company_attachments_list = [
          // htmlLang.includes("ar") ? "فاتورة" : "Invoice",
          htmlLang.includes("ar") ? "شهادة الآيبان" : "Iban certificate",
        ],
        emazad_individual_attachments_list = [
          htmlLang.includes("ar") ? "شهادة الآيبان" : "IBAN certificate",
        ];
      console.log('e target value', e.target.value);
      switch (e.target.value) {
        case "saso":
          $(".to-be-modif").removeClass("col-sm-4").addClass("col-sm-6");
          $(".client_name").text('CB Name')
          // $(".emazad-company input[name='mazad_number']").attr("required", false);
          $(".emazad-individual input").each(function (idx, el) {
            $(el).attr("required", false);
          });
          $("#client_register_attach_list")
            .empty()
            .append(
              saso_attachments_list.map(function (item, i) {
                return `<div class="float-left mr-2" style="list-style:auto;font-size:22px"><span>${i + 1
                  }</span>. ${item}</div>`;
              })
            );
          break;
        case "emazad_company":
          $(".to-be-modif").removeClass("col-sm-4").addClass("col-sm-6");
          $(".emazad-company").removeClass("d-none");
          $(".legal").addClass("d-none");
          $(".client_name").text('Client Name')
          // $(".emazad-company input[name='mazad_number']").attr("required", true);
          $(".emazad-individual input").each(function (idx, el) {
            $(el).attr("required", false);
          });
          $("#client_register_attach_list")
            .empty()
            .append(
              emazad_company_attachments_list.map(function (item, i) {
                return `<div class="float-left mr-2" style="list-style:auto;font-size:22px"><span>${i + 1
                  }</span>. ${item}</div>`;
              })
            );
          break;
        case "emazad_individual":
          $(".emazad-individual").removeClass("d-none");
          $(".legal").addClass("d-none");
          $("input[name='legal_representative']").attr("required", false);
          // $(".emazad-company input[name='mazad_number']").attr("required", false);
          $(".to-be-modif").removeClass("col-sm-4").addClass("col-sm-6");
          $("#client_register_attach_list")
            .empty()
            .append(
              emazad_individual_attachments_list.map(function (item, i) {
                return `<div class="float-left mr-2" style="list-style:auto;font-size:22px"><span>${i + 1
                  }</span>. ${item}</div>`;
              })
            );
          break;
        default:
          break;
      }
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
    /**
     * @private
     */
    _onClickCreateBank: async function (e) {
      e.preventDefault();
      e.stopPropagation();
      let vals = {};
      $(".bank_creation input, .bank_creation select")
        .not("[type='file']")
        .not("[type='hidden']")
        .not("[type='search']")
        .each(function (idx, el) {
          vals[$(el).attr("name")] = $(el).val();
        });
      if (document.querySelector("#create_bank_form").checkValidity()) {
        $("#create_bank_form").removeClass("was-validated");
        vals["bank_name"] = $("#bank option:selected").text();
        vals["branch_name"] = $("#branch option:selected").text();
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        this._rpc({
          route: "/client_registration/create_bank",
          params: vals,
        }).then(function (res) {
          const { status, message } = JSON.parse(res);
          if (status === "success") {
            $(".create_bank_error").addClass("d-none");
            $("#registerClientInfoModal").hide();
            location.href = location.pathname;
          } else {
            $.unblockUI();
            $(".create_bank_error").removeClass("d-none").text(message);
          }
        });
      } else {
        $("#create_bank_form").addClass("was-validated");
      }
    },
    /**
     * @private
     */
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
    /**
     * @private
     */
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

    _onchangeIBAN: function () {
      var $iban = $("input[name='iban']")
      if (!Utils.isValidIBANNumber($iban.val())) {
        $('.create_client_bank').attr('disabled', 'disabled');
        $(".invalid-ibancode").removeClass("d-none");
      } else {
        $(".invalid-ibancode").addClass("d-none");
        $('.create_client_bank').removeAttr('disabled');
      }
    },
  });

  publicWidget.registry.ClientRegistartionViewModePage = publicWidget.Widget.extend({
    selector: ".creg_view_mode_page_selector",
    events: {
      "click .creg_action_change_state": "_onClickChangeRegistrationState",
    },

    _onClickChangeRegistrationState: function (e) {
      $.blockUI({
        css: { backgroundColor: "transparent", border: "none" },
        message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
      });
      var creg_id = $(e.target).attr("creg_id"),
        direction = $(e.target).attr("direction");
      let parameters = { creg_id: creg_id, direction: direction };
      ajax.jsonRpc("/client_registration/change/status", "call", parameters)
        .then(function (result) {
          const { status, message } = JSON.parse(result);
          $(".creg_action_change_state").attr("disabled", "disabled");
          if (status == "success") {
            location.reload();
          } else {
            $.unblockUI();
            $(".request-error").removeClass("d-none").text(message);
            $(".creg_action_change_state").removeAttr("disabled");
          }
        })
    },
  });

  publicWidget.registry.ClientPaymentWidget = publicWidget.Widget.extend({
    selector: "#addClientPaymentModal",
    events: {
      "click .create_client_payment": "_onClickCreateClientPayment",
    },

    _onClickCreateClientPayment: async function(e){
      e.preventDefault();
      e.stopPropagation();
      
      // $.blockUI({
      //   css: { backgroundColor: "transparent", border: "none" },
      //   message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
      // });
      
      let params = {};
      $("#create_client_payment_form input").not("[type='file']").not("[type='hidden']").not("[type='search']").each(function (idx, el) {
          params[$(el).attr("name")] = $(el).val();
        });
      
      var isAttchmentsValid = false,
        clientPaymentCategory = $("input[name='client_payment_category']").val();

      if (clientPaymentCategory == "saso" && $("input[name='client_payment_attachments']")[0].files.length >= 2) {
        isAttchmentsValid = true;
      }
      if (clientPaymentCategory == "emazad_company" && $("input[name='client_payment_attachments']")[0].files.length >= 1) {
        isAttchmentsValid = true;
      }
      // if (clientPaymentCategory == "emazad_individual" && $("input[name='client_payment_attachments']")[0].files.length >= 1) {
        if (clientPaymentCategory == "emazad_individual") {
          isAttchmentsValid = true;
      }
      if (document.querySelector("#create_client_payment_form").checkValidity() && isAttchmentsValid) {
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        var client_payment_attachments = $("#create_client_payment_form input[name='client_payment_attachments']")[0].files;

        params["client_payment_attachments"] = await Utils.convert2DataUrl(client_payment_attachments);
        params["client_payment_category"] = $("input[name='client_payment_category']").val();
        $("#create_client_payment_form").removeClass("was-validated");

        this._rpc({
          route: "/client_payment/create",
          params: params,
        }).then(function (res) {
          const { status } = JSON.parse(res);
          if (status === "success") {
            $(".create_client_payment_error").addClass("d-none");
            $("#create_client_payment_form input[name='client_payment_attachments']").val(null);
            $("#create_client_payment_form input[name='legal_representative']").val(null);
            $("#create_client_payment_form input[name='mazad_number']").val(null);
            $("#create_client_payment_form input[name='total_amount']").val(null);
            // reload page
            location.reload();
          } else {
            $.unblockUI();
            const { message } = JSON.parse(res);
            $(".create_client_payment_error").removeClass("d-none").text(message);
          }
        });
      } else {
        $("#create_client_payment_form").addClass("was-validated");
        $(".custom-input-file").addClass("border-dashed border-danger");
        if (
          $("#client_payment_category").val() == "saso" &&
          $("#client_register_attachments")[0].files.length < 6
        ) {
          $("#client_register_attach_error")
            .removeClass("d-none")
            .text(
              htmlLang.includes("ar")
                ? "يرجى تحميل كافة المرفقات المطلوبة (3 ملفات)!"
                : "Please upload all required attachments (3 files)!"
            );
          $(".custom-input-file").addClass("border-dashed border-danger");
        }
        if (
          $("#client_payment_category").val() == "emazad_company" &&
          $("#client_register_attachments")[0].files.length < 2
        ) {
          $("#client_register_attach_error")
            .removeClass("d-none")
            .text(
              htmlLang.includes("ar")
                ? "يرجى تحميل جميع المرفقات المطلوبة (ملف واحد)!"
                : "Please upload all required attachments (1 file)!"
            );
          $(".custom-input-file").addClass("border-dashed border-danger");
        }
        if (
          $("#client_payment_category").val() == "emazad_individual" &&
          $("#client_register_attachments")[0].files.length < 1
        ) {
          $("#client_register_attach_error")
            .removeClass("d-none")
            .text(
              htmlLang.includes("ar")
                ? "يرجى تحميل جميع المرفقات المطلوبة (ملف واحد)!"
                : "Please upload all required attachments (1 file)!"
            );
          $(".custom-input-file").addClass("border-dashed border-danger");
        }
      }
    }
  });

  publicWidget.registry.updateClientRegistrationWidget = publicWidget.Widget.extend({
    selector: "#editRegisterClientInfoModal",
    events: {
      "click .update_client_registration": "_onClickUpdateClientRegistration",
    },

    _onClickUpdateClientRegistration: async function(e){
      e.preventDefault();
      e.stopPropagation();
      
      let params = {};
      $("#update_client_registration_form input").not("[type='file']").not("[type='hidden']").not("[type='search']").each(function (idx, el) {
          params[$(el).attr("name")] = $(el).val();
        });

      // var clientPaymentCategory = $("input[name='client_payment_category']").val();
      if (document.querySelector("#update_client_registration_form").checkValidity()) {
        $.blockUI({
          css: { backgroundColor: "transparent", border: "none" },
          message: '<img src="/web/static/img/spin.png" class="fa-pulse"/>',
        });
        var client_register_attachments = $("#update_client_registration_form input[name='client_register_attachments']")[0].files;

        params["client_register_attachments"] = await Utils.convert2DataUrl(client_register_attachments);
        params["client_payment_category"] = $("input[name='client_payment_category']").val();
        $("#update_client_registration_form").removeClass("was-validated");

        this._rpc({
          route: "/client_registration/update",
          params: params,
        }).then(function (res) {
          const { status } = JSON.parse(res);
          if (status === "success") {
            $(".update_client_reg_error").addClass("d-none");
            // reload page
            location.reload();
          } else {
            $.unblockUI();
            const { message } = JSON.parse(res);
            $(".update_client_reg_error").removeClass("d-none").text(message);
          }
        });
      }
    }
  });


});

odoo.define("thiqah.client.payment.workflow.engine", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");
  var core = require("web.core");
  var ajax = require("web.ajax");
  var _t = core._t;

  publicWidget.registry.clientPaymentWorkflowEngine =
    publicWidget.Widget.extend({
      selector: ".cpayment_action_selector",
      events: {
        "click .cpayment_approve_action": "_onApproveClientPayment",
      },

      _onApproveClientPayment: function (e) {
        $("body").css("cursor", "progress");
        var buttonKey = $(e.target).attr("id");
        var requestId = $(e.target).attr("cpayment_id");
        if (requestId && buttonKey) {
          let parameters = {
            request_id: requestId,
            button_key: buttonKey,
            model_name: "client.payment",
          };
          $(".cpayment_approve_action").attr("disabled", "disabled");
          ajax
            .jsonRpc("/client_payment/change/status", "call", parameters)
            .then(function (result) {
              const { status, message } = JSON.parse(result);
              if (status == "success") {
                location.reload();
              } else {
                $(".request-error").removeClass("d-none").text(message);
              }
            });
        }
      },
    });
});

odoo.define("client.registration.delete.document", function (require) {
  "use strict";
  var publicWidget = require("web.public.widget");

  publicWidget.registry.clientRegistrationDeleteDocument =
    publicWidget.Widget.extend({
      selector: ".documents_list",
      events: {
        "click #confirm_delete": "async _onAttachmentDeleteClick",
        "click .o_portal_attachment_delete": "_onShowDeleteModal",
      },

      _onShowDeleteModal: function (ev) {
        var attachmentId = $(ev.currentTarget)
          .closest(".cr_attachment")
          .data("id");
        $("input[name='doc_id']").val(attachmentId);
        ev.preventDefault();
        ev.stopPropagation();
        $("#docDeleteConfirmModal").modal("show");
      },

      _onAttachmentDeleteClick: function (ev) {
        var attachmentId = $("input[name='doc_id']").val();
        ev.preventDefault();
        ev.stopPropagation();

        return this._rpc({
          route: "/client_reg/attachment/remove",
          params: {
            attachment_id: attachmentId,
          },
        }).then(function () {
          $("#docDeleteConfirmModal").modal("hide");
          $(".cr_attachment").each(function (idx, el) {
            if ($(el).data("id") == attachmentId) {
              $(el).remove();
            }
          });
        });
      },
    });
});
