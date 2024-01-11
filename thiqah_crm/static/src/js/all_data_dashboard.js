odoo.define("thiqah_crm.crmDashboardAll", function (require) {
  "use strict";

  var AbstractAction = require("web.AbstractAction");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var rpc = require("web.rpc");
  var session = require("web.session");
  var Utils = require("thiqah.Utils");
  var _t = core._t;
  var QWeb = core.qweb;

  var ThiqahCRMDashboardAllData = AbstractAction.extend({
    template: "thiqah_crm_dashboard_all",
    jsLibs: ["/thiqah_base/static/libs/Chart.js"],
    hasControlPanel: false,
    events: {
      // Open views Odoo
      "click .all_aahd_opportunities": "all_aahd_opportunities",
      "click .all_bd_opportunities": "all_bd_opportunities",
      //lost
      "click .lost_bd_opportunities": "lost_bd_opportunities",
      "click .lost_aahd_opportunities": "lost_aahd_opportunities",
      //won
      "click .won_aahd_opportunities": "won_aahd_opportunities",
      "click .won_bd_opportunities": "won_bd_opportunities",
      "click .card_more_button": "card_more_button",
      "click .tickets_stages": "open_tickets_stages",
      "click .total_tickets": "open_total_tickets",
      "click .total_sla": "open_total_sla",
      "click .tickets_sla": "open_tickets_sla",

      //filters
      "change #choose_partner": function (e) {
        e.stopPropagation();
        var $target = $(e.target);
        var partner = $target.val();
        var account_manager = $("#choose_account_manager").val();
        var product = $("#choose_product").val();
        this.change_template_by_filter(partner, product, account_manager);
        this.change_tickets_template_by_filter(partner);
      },
      "change #choose_product": function (e) {
        e.stopPropagation();
        var $target = $(e.target);
        var product = $target.val();
        var account_manager = $("#choose_account_manager").val();
        var partner = $("#choose_partner").val();
        this.change_template_by_filter(partner, product, account_manager);
      },
      "change #choose_account_manager": function (e) {
        e.stopPropagation();
        var $target = $(e.target);
        var account_manager = $target.val();
        var product = $("#choose_product").val();
        var partner = $("#choose_partner").val();
        this.change_template_by_filter(partner, product, account_manager);
      },
    },
    init: function (parent, context) {
      this._super(parent, context);
      this.dashboards_templates = ["thiqah_crm_dashboard_document_all"];
      this.list_partners = [];
      this.list_account_managers = [];
      this.list_products = [];
      this.stages_tickets = [];
    },

    start: function () {
      var self = this;
      this.set("title", "Dashboard");
      return this._super().then(function () {
        self.render_dashboards();
        self.get_opp_dashboard_data();
        self.renderDounutOppChart();
        self.renderDounutLostOppChart();
        self.renderDounutWonOppChart();
        self.get_tickets_dashboard_data();
      });
    },

    willStart: function () {
      var self = this;
      return $.when(ajax.loadLibs(this), this._super()).then(function () {
        var dash1 = self.get_opp_dashboard_data();
        return $.when(dash1);
      });
    },
    render_dashboards: function () {
      var self = this;
      _.each(this.dashboards_templates, function (template) {
        self
          .$(".CRM_dashboardAll")
          .append(QWeb.render(template, { widget: self }));
      });
    },
    card_more_button: function (e) {
      /*$(this).parent().closest('.card').toggleClass('card_full');     
    $(this).parent().siblings('.stats_row').slideToggle('fast');
    $(this).toggleClass('flipY');*/
    },

    //get tickets helpdesk data
    get_tickets_dashboard_data: function () {
      var self = this;

      var data = this._rpc({
        model: "helpdesk.stage",
        method: "get_tickets_dashboard_data",
        args: [],
      }).then(function (result) {
        self.all_tickets = result["all_tickets"];
        self.stages_tickets = result["stages_tickets"];
        self.total_sla = result["total_sla"];
        self.all_sla = result["all_sla"];
        var ticketsSatgesLabels = _.map(self.stages_tickets, function (l, i) {
          return `${l[1]} (${l[2]})`;
        });
        var ticketsSatgesData = _.map(self.stages_tickets, function (l, i) {
          return l[2];
        });
        var ctx = self.$("#spAllTickets");
        new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: ticketsSatgesLabels,
            datasets: [
              {
                data: ticketsSatgesData,
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var listOfColor = [
                    ["#3C85C1", "#00BCB6"],
                    ["#00BCB4", "#00BCB4"],
                    ["#00BCB6", "#A7D7CE"],
                    ["#A7D7CE", "#EDF6F5"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    ticketsSatgesLabels,
                    ctx,
                    chartArea
                  );
                },
              },
            ],
          },
          options: {
            maintainAspectRatio: false,
            cutout: "70%",
            responsive: true,
            plugins: {
              legend: {
                position: "right",
                labels: {
                  boxWidth: 16,
                  boxHeight: 16,
                  borderRadius: 4,
                },
              },
            },
          },
          plugins: [
            {
              beforeDatasetsDraw(chart, args, options) {
                const { ctx, data } = chart;
                ctx.save();
                const xCoord = chart.getDatasetMeta(0).data[0].x,
                  yCoord = chart.getDatasetMeta(0).data[0].y;
                ctx.font = "400 75px TanseekModernProArabic";
                ctx.fillStyle = "#0A0A0A";
                ctx.textAlign = "center";
                ctx.textBaseLine = "middle";
                ctx.fillText(self.all_tickets, xCoord, yCoord);
                ctx.font = "400 18px TanseekModernProArabic";
                ctx.fillStyle = "#798793";
                ctx.fillText("TOTAL", xCoord, yCoord + 35);
              },
            },
          ],
        });
      });
      return $.when(data);
    },
    // Get Dashboard Data
    get_opp_dashboard_data: function () {
      var self = this;
      var data = this._rpc({
        model: "crm.lead",
        method: "get_opp_dashboard_data",
        args: [],
      }).then(function (result) {
        self.currency = result.currency;
        self.all_opportunities = result["all_opportunities"];
        self.all_opportunities_bd = result["all_opportunities_bd"];
        self.all_opportunities_aahd = result["all_opportunities_aahd"];
        self.total_opp_revenue = Utils.formatCurrency(
          result["total_opp_revenue"]
        );
        self.total_opp_expected_revenue = Utils.formatCurrency(
          result["total_opp_expected_revenue"]
        );
        //lost
        self.all_opportunities_lost = result["all_opportunities_lost"];
        self.all_opportunities_lost_aahd =
          result["all_opportunities_lost_aahd"];
        self.all_opportunities_lost_bd = result["all_opportunities_lost_bd"];
        self.total_lost_revenue = Utils.formatCurrency(
          result["total_lost_revenue"]
        );
        //won
        self.all_opportunities_won = result["all_opportunities_won"];
        self.all_opportunities_won_aahd = result["all_opportunities_won_aahd"];
        self.all_opportunities_won_bd = result["all_opportunities_won_bd"];
        self.total_won_revenue = Utils.formatCurrency(
          result["total_won_revenue"]
        );
        self.list_partners = result["list_partners"];
        self.list_account_managers = result["list_account_managers"];
        self.list_products = result["list_products"];
      });
      return $.when(data);
    },
    renderDounutOppChart: function () {
      var self = this;
      var oppSatgesLabels = [
        `Thiqah (${self.all_opportunities_bd})`,
        `Aahd (${self.all_opportunities_aahd})`,
      ];
      var ctx = self.$("#spTotalOpp");
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: oppSatgesLabels,
          datasets: [
            {
              data: [self.all_opportunities_bd, self.all_opportunities_aahd],
              backgroundColor: function (context) {
                const chart = context.chart;
                const { ctx, chartArea } = chart;

                if (!chartArea) {
                  // This case happens on initial chart load
                  return;
                }
                var listOfColor = [["#5B508D", "#00BCB4"]];
                return Utils.generateGradients(
                  listOfColor,
                  oppSatgesLabels,
                  ctx,
                  chartArea
                );
              },
            },
          ],
        },
        options: {
          maintainAspectRatio: false,
          cutout: "70%",
          responsive: true,
          plugins: {
            legend: {
              position: "right",
              labels: {
                boxWidth: 16,
                boxHeight: 16,
                borderRadius: 4,
              },
            },
          },
        },
        plugins: [
          {
            beforeDatasetsDraw(chart, args, options) {
              const { ctx, data } = chart;
              ctx.save();
              const xCoord = chart.getDatasetMeta(0).data[0].x,
                yCoord = chart.getDatasetMeta(0).data[0].y;
              ctx.font = "400 75px TanseekModernProArabic";
              ctx.fillStyle = "#0A0A0A";
              ctx.textAlign = "center";
              ctx.textBaseLine = "middle";
              ctx.fillText(self.all_opportunities, xCoord, yCoord);
              ctx.font = "400 18px TanseekModernProArabic";
              ctx.fillStyle = "#798793";
              ctx.fillText("TOTAL", xCoord, yCoord + 35);
            },
          },
        ],
      });
    },
    renderDounutWonOppChart: function () {
      var self = this;
      var oppSatgesLabels = [
        `Thiqah (${self.all_opportunities_won_bd})`,
        `Aahd (${self.all_opportunities_won_aahd})`,
      ];
      var ctx = self.$("#spTotalWonOpp");
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: oppSatgesLabels,
          datasets: [
            {
              data: [
                self.all_opportunities_won_bd,
                self.all_opportunities_won_aahd,
              ],
              backgroundColor: function (context) {
                const chart = context.chart;
                const { ctx, chartArea } = chart;

                if (!chartArea) {
                  // This case happens on initial chart load
                  return;
                }
                var listOfColor = [["#5B508D", "#00BCB4"]];
                return Utils.generateGradients(
                  listOfColor,
                  oppSatgesLabels,
                  ctx,
                  chartArea
                );
              },
            },
          ],
        },
        options: {
          maintainAspectRatio: false,
          cutout: "70%",
          responsive: true,
          plugins: {
            legend: {
              position: "right",
              labels: {
                boxWidth: 16,
                boxHeight: 16,
                borderRadius: 4,
              },
            },
          },
        },
        plugins: [
          {
            beforeDatasetsDraw(chart, args, options) {
              const { ctx, data } = chart;
              ctx.save();
              const xCoord = chart.getDatasetMeta(0).data[0].x,
                yCoord = chart.getDatasetMeta(0).data[0].y;
              ctx.font = "400 75px TanseekModernProArabic";
              ctx.fillStyle = "#0A0A0A";
              ctx.textAlign = "center";
              ctx.textBaseLine = "middle";
              ctx.fillText(self.all_opportunities_won, xCoord, yCoord);
              ctx.font = "400 18px TanseekModernProArabic";
              ctx.fillStyle = "#798793";
              ctx.fillText("TOTAL", xCoord, yCoord + 35);
            },
          },
        ],
      });
    },
    renderDounutLostOppChart: function () {
      var self = this;
      var oppSatgesLabels = [
        `Thiqah (${self.all_opportunities_lost_bd})`,
        `Aahd (${self.all_opportunities_lost_aahd})`,
      ];
      var ctx = self.$("#spTotalLostOpp");
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: oppSatgesLabels,
          datasets: [
            {
              data: [
                self.all_opportunities_lost_bd,
                self.all_opportunities_lost_aahd,
              ],
              backgroundColor: function (context) {
                const chart = context.chart;
                const { ctx, chartArea } = chart;

                if (!chartArea) {
                  // This case happens on initial chart load
                  return;
                }
                var listOfColor = [["#5B508D", "#00BCB4"]];
                return Utils.generateGradients(
                  listOfColor,
                  oppSatgesLabels,
                  ctx,
                  chartArea
                );
              },
            },
          ],
        },
        options: {
          maintainAspectRatio: false,
          cutout: "70%",
          responsive: true,
          plugins: {
            legend: {
              position: "right",
              labels: {
                boxWidth: 16,
                boxHeight: 16,
                borderRadius: 4,
              },
            },
          },
        },
        plugins: [
          {
            beforeDatasetsDraw(chart, args, options) {
              const { ctx, data } = chart;
              ctx.save();
              const xCoord = chart.getDatasetMeta(0).data[0].x,
                yCoord = chart.getDatasetMeta(0).data[0].y;
              ctx.font = "400 75px TanseekModernProArabic";
              ctx.fillStyle = "#0A0A0A";
              ctx.textAlign = "center";
              ctx.textBaseLine = "middle";
              ctx.fillText(self.all_opportunities_lost, xCoord, yCoord);
              ctx.font = "400 18px TanseekModernProArabic";
              ctx.fillStyle = "#798793";
              ctx.fillText("TOTAL", xCoord, yCoord + 35);
            },
          },
        ],
      });
    },

    //All Aahd Opportunities
    all_aahd_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["type", "=", "opportunity"],
        ["for_aahd", "=", true],
      ];
      if (product) {
        domain_filter.push(["product_ids", "in", [parseInt(product)]]);
      }
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (account_manager) {
        domain_filter.push([
          "partner_id.account_manager",
          "=",
          parseInt(account_manager),
        ]);
      }

      this.do_action({
        name: _t("Aahd Opportunities"),
        type: "ir.actions.act_window",
        res_model: "crm.lead",
        view_mode: "kanban,tree,form,calendar",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
          [false, "calendar"],
        ],
        domain: domain_filter,
        target: "current",
        context: {
          default_type: "opportunity",
          form_view_ref: "thiqah_crm.thiqah_aahd_crm_lead_view_form",
          default_for_aahd: true,
        },
      });
    },
    // open total sla
    open_total_sla: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var partner = $("#choose_partner").val();

      var domain_filter = [];
      if (partner) {
        domain_filter.push(["partner_ids", "in", [parseInt(partner)]]);
      }

      this.do_action({
        name: _t("SLA Policies"),
        type: "ir.actions.act_window",
        res_model: "helpdesk.sla",
        view_mode: "tree,kanban,form",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
        ],
        domain: domain_filter,
        target: "current",
        context: {},
      });
    },
    // open helpedesk ticket sla
    open_tickets_sla: function (e) {
      var self = this;
      console.log("e", e);
      console.log("e.target", e.currentTarget);
      //var sla_id = e.currentTarget.getAttribute('id');
      ///  console.log('sla_id',sla_id);
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var partner = $("#choose_partner").val();

      var domain_filter = [];
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      //if (sla_id){domain_filter.push(['sla_ids','in',[parseInt(sla_id)]])}

      this.do_action({
        name: _t("SLA Tickets"),
        type: "ir.actions.act_window",
        res_model: "helpdesk.ticket",
        view_mode: "kanban,tree,form",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
        ],
        domain: domain_filter,
        target: "current",
        context: {},
      });
    },
    // open total tickets
    open_total_tickets: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var partner = $("#choose_partner").val();

      var domain_filter = [];
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }

      this.do_action({
        name: _t("SLA Tickets"),
        type: "ir.actions.act_window",
        res_model: "helpdesk.ticket",
        view_mode: "kanban,tree,form",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
        ],
        domain: domain_filter,
        target: "current",
        context: {},
      });
    },
    // open helpedesk ticket
    open_tickets_stages: function (e) {
      var self = this;
      console.log("e", e);
      console.log("e.target", e.currentTarget);
      var stage_id = e.currentTarget.getAttribute("id");
      console.log("stage_id", stage_id);
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var partner = $("#choose_partner").val();

      var domain_filter = [];
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (stage_id) {
        domain_filter.push(["stage_id", "=", parseInt(stage_id)]);
      }

      this.do_action({
        name: _t("Tickets"),
        type: "ir.actions.act_window",
        res_model: "helpdesk.ticket",
        view_mode: "kanban,tree,form",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
        ],
        domain: domain_filter,
        target: "current",
        context: {},
      });
    },
    //All BD Opportunities
    all_bd_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["type", "=", "opportunity"],
        ["for_bd", "=", true],
      ];
      if (product) {
        domain_filter.push(["product_ids", "in", [parseInt(product)]]);
      }
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (account_manager) {
        domain_filter.push([
          "partner_id.account_manager",
          "=",
          parseInt(account_manager),
        ]);
      }

      this.do_action({
        name: _t("BD Opportunities"),
        type: "ir.actions.act_window",
        res_model: "crm.lead",
        view_mode: "kanban,tree,form,calendar",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
          [false, "calendar"],
        ],
        domain: domain_filter,
        target: "current",
        context: {
          default_type: "opportunity",
          form_view_ref: "thiqah_crm.thiqah_bd_crm_lead_view_form",
          default_for_bd: true,
        },
      });
    },
    //WON BD Opportunities
    won_bd_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["type", "=", "opportunity"],
        ["for_bd", "=", true],
        ["stage_id.is_won", "=", true],
      ];
      if (product) {
        domain_filter.push(["product_ids", "in", [parseInt(product)]]);
      }
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (account_manager) {
        domain_filter.push([
          "partner_id.account_manager",
          "=",
          parseInt(account_manager),
        ]);
      }

      this.do_action({
        name: _t("WON BD Opportunities"),
        type: "ir.actions.act_window",
        res_model: "crm.lead",
        view_mode: "kanban,tree,form,calendar",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
          [false, "calendar"],
        ],
        domain: domain_filter,
        target: "current",
        context: {
          default_type: "opportunity",
          form_view_ref: "thiqah_crm.thiqah_bd_crm_lead_view_form",
          default_for_bd: true,
        },
      });
    },
    //WON BAahd Opportunities
    won_aahd_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["type", "=", "opportunity"],
        ["for_aahd", "=", true],
        ["stage_id.is_won", "=", true],
      ];
      if (product) {
        domain_filter.push(["product_ids", "in", [parseInt(product)]]);
      }
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (account_manager) {
        domain_filter.push([
          "partner_id.account_manager",
          "=",
          parseInt(account_manager),
        ]);
      }

      this.do_action({
        name: _t("WON Aahd Opportunities"),
        type: "ir.actions.act_window",
        res_model: "crm.lead",
        view_mode: "kanban,tree,form,calendar",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
          [false, "calendar"],
        ],
        domain: domain_filter,
        target: "current",
        context: {
          default_type: "opportunity",
          form_view_ref: "thiqah_crm.thiqah_aahd_crm_lead_view_form",
          default_for_aahd: true,
        },
      });
    },
    //LOST BD Opportunities
    lost_bd_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["type", "=", "opportunity"],
        ["for_bd", "=", true],
        ["probability", "=", 0],
        "|",
        ["active", "=", true],
        ["active", "=", false],
      ];
      if (product) {
        domain_filter.push(["product_ids", "in", [parseInt(product)]]);
      }
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (account_manager) {
        domain_filter.push([
          "partner_id.account_manager",
          "=",
          parseInt(account_manager),
        ]);
      }

      this.do_action({
        name: _t("LOST BD Opportunities"),
        type: "ir.actions.act_window",
        res_model: "crm.lead",
        view_mode: "kanban,tree,form,calendar",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
          [false, "calendar"],
        ],
        domain: domain_filter,
        target: "current",
        context: {
          default_type: "opportunity",
          form_view_ref: "thiqah_crm.thiqah_bd_crm_lead_view_form",
          default_for_bd: true,
        },
      });
    },
    //LOST Aahd Opportunities
    lost_aahd_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["type", "=", "opportunity"],
        ["for_aahd", "=", true],
        ["probability", "=", 0],
        "|",
        ["active", "=", true],
        ["active", "=", false],
      ];
      if (product) {
        domain_filter.push(["product_ids", "in", [parseInt(product)]]);
      }
      if (partner) {
        domain_filter.push(["partner_id", "=", parseInt(partner)]);
      }
      if (account_manager) {
        domain_filter.push([
          "partner_id.account_manager",
          "=",
          parseInt(account_manager),
        ]);
      }

      this.do_action({
        name: _t("LOST Aahd Opportunities"),
        type: "ir.actions.act_window",
        res_model: "crm.lead",
        view_mode: "kanban,tree,form,calendar",
        views: [
          [false, "kanban"],
          [false, "list"],
          [false, "form"],
          [false, "calendar"],
        ],
        domain: domain_filter,
        target: "current",
        context: {
          default_type: "opportunity",
          form_view_ref: "thiqah_crm.thiqah_aahd_crm_lead_view_form",
          default_for_aahd: true,
        },
      });
    },

    change_template_by_filter: function (partner, product, account_manager) {
      var self = this;
      this._rpc({
        model: "crm.lead",
        method: "get_opp_dashboard_data",
        args: [partner, product, account_manager],
      }).then(function (result) {
        $("#all_opportunities")[0].innerHTML = result["all_opportunities"];
        $("#all_opportunities_bd")[0].innerHTML =
          result["all_opportunities_bd"];
        $("#all_opportunities_aahd")[0].innerHTML =
          result["all_opportunities_aahd"];
        $("#total_opp_revenue")[0].innerHTML = result["total_opp_revenue"];
        $("#total_opp_expected_revenue")[0].innerHTML =
          result["total_opp_expected_revenue"];

        $("#all_opportunities_lost")[0].innerHTML =
          result["all_opportunities_lost"];
        $("#all_opportunities_lost_aahd")[0].innerHTML =
          result["all_opportunities_lost_aahd"];
        $("#all_opportunities_lost_bd")[0].innerHTML =
          result["all_opportunities_lost_bd"];
        $("#total_lost_revenue")[0].innerHTML = result["total_lost_revenue"];

        $("#all_opportunities_won")[0].innerHTML =
          result["all_opportunities_won"];
        $("#all_opportunities_won_aahd")[0].innerHTML =
          result["all_opportunities_won_aahd"];
        $("#all_opportunities_won_bd")[0].innerHTML =
          result["all_opportunities_won_bd"];
        $("#total_won_revenue")[0].innerHTML = result["total_won_revenue"];
      });
    },

    change_tickets_template_by_filter: function (partner) {
      var self = this;
      this._rpc({
        model: "helpdesk.stage",
        method: "get_tickets_dashboard_data",
        args: [partner],
      }).then(function (result) {
        $("#all_tickets")[0].innerHTML = result["all_tickets"];
        var stages_tickets = result["stages_tickets"];
        stages_tickets.forEach((stage) => {
          var strstage = "#tickets_nbr_stage_" + stage[0];
          $(strstage)[0].innerHTML = stage[2];
        });
      });
    },
  });

  core.action_registry.add(
    "ThiqahCRMDashboardAllData",
    ThiqahCRMDashboardAllData
  );

  return ThiqahCRMDashboardAllData;
});
