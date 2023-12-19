odoo.define("thiqah_crm.crmDashboard", function (require) {
  "use strict";

  var AbstractAction = require("web.AbstractAction");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var rpc = require("web.rpc");
  var session = require("web.session");
  var Utils = require("thiqah.Utils");
  var web_client = require("web.web_client");
  var _t = core._t;
  var QWeb = core.qweb;
  console.log(session.company_id.currency_id);
  var ThiqahCRMDashboard = AbstractAction.extend({
    jsLibs: [
      "/thiqah_base/static/libs/Chart.js",
      "/thiqah_base/static/libs/chartjs-plugin-datalabels.min.js",
    ],
    // hasControlPanel: true,

    template: "thiqah_crm_dashboard",
    events: {
      // Open views Odoo
      "click .wathiq_opportunities": "wathiq_opportunities",
      "click .wathiq_enterprise_opportunities":
        "wathiq_enterprise_opportunities",
      "click .wathiq_basic_opportunities": "wathiq_basic_opportunities",
      "click .wathiq_batch_opportunities": "wathiq_batch_opportunities",
      "click .print_dashboard": "fct_print_dashboard",

      //filters
      "change #choose_partner": function (e) {
        e.stopPropagation();
        var $target = $(e.target);
        var partner = $target.val();
        var account_manager = $("#choose_account_manager").val();
        var product = $("#choose_product").val();
        this.change_template_by_filter(partner, product, account_manager);
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
      this.dashboards_templates = ["thiqah_crm_dashboard_document"];
      this.get_top_ten_clients1 = [];
      this.get_top_ten_clients2 = [];
      this.list_account_managers = [];
      this.list_partners = [];
      this.list_products = [];
      this.get_total_top_ten_clients_revenue = 0;
      this.total_revenue = 0;
    },
    start: function () {
      var self = this;
      this.set("title", "Dashboard");
      return this._super().then(function () {
        self.render_dashboards();
        self.render_wathiq_basic_enterprise_bar_chart_graph();
        self.render_wathiq_enterprise_by_stages_bar_chart_graph();
        self.render_requests_by_stages_bar_chart_graph();
        self.render_opports_month_graph();
        self.render_annual_chart_graph();
        self.$el.find(".selectpicker").selectpicker();
      });
    },

    willStart: function () {
      var self = this;
      return $.when(ajax.loadLibs(this), this._super()).then(function () {
        return self.dashboard_fetch_data();
      });
    },
    render_dashboards: function () {
      var self = this;
      _.each(this.dashboards_templates, function (template) {
        self
          .$(".CRM_dashboard")
          .append(QWeb.render(template, { widget: self }));
      });
    },

    // Print Dashboard Data
    fct_print_dashboard: function () {
      var self = this;
      //  this.do_action('thiqah_crm.thiqah_dashboard_reports');
      var data = this._rpc({
        model: "crm.lead",
        method: "action_dashboard_report_print",
        args: [[]],
      }).then(function (res) {
        console.log("Success", res);
        return res.res_ids;
      });
      console.log("Successres.data", data);
      return this.do_action("thiqah_crm.thiqah_dashboard_reports", {
        additional_context: { active_ids: data },
      });
      //return $.when(data);
    },

    //Wathiq Opportunities
    wathiq_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();
      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["is_wathiq", "=", true],
        ["type", "=", "opportunity"],
      ];
      // var domain_filter=[['is_wathiq', '=', true],['type','=','opportunity'],['stage_id.is_won','=',true],];
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
        name: _t("Wathiq Opportunities"),
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
    //Wathiq Enterprise Opportunities
    wathiq_enterprise_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();

      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["is_wathiq", "=", true],
        ["service_type", "=", "enterprise"],
        ["type", "=", "opportunity"],
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
        name: _t("Wathiq Enterprise Opportunities"),
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
    //Wathiq Basic Opportunities
    wathiq_basic_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();

      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["is_wathiq", "=", true],
        ["service_type", "=", "basic"],
        ["type", "=", "opportunity"],
      ];
      // var domain_filter=[['is_wathiq', '=', true],['service_type', '=', 'basic'],['type','=','opportunity'],['stage_id.is_won','=',true],];
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
        name: _t("Wathiq Basic Opportunities"),
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
    //Wathiq Batch Opportunities
    wathiq_batch_opportunities: function (e) {
      var self = this;
      e.stopPropagation();
      e.preventDefault();

      // get filter values to domain
      var product = $("#choose_product").val();
      var partner = $("#choose_partner").val();
      var account_manager = $("#choose_account_manager").val();
      var domain_filter = [
        ["is_wathiq", "=", true],
        ["service_type", "=", "batch"],
        ["type", "=", "opportunity"],
      ];
      // var domain_filter=[['is_wathiq', '=', true],['service_type', '=', 'batch'],['type','=','opportunity'],['stage_id.is_won','=',true],];
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
        name: _t("Wathiq Batch Opportunities"),
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

    apply_humain_format: function (value) {
      const number = value.toString();
      console.log(number);
      const len = number.length;
      const place = len % 3 || 3;
      let abb, r;
      switch (true) {
        case len > 9:
          abb = "B";
          break;
        case len > 6:
          abb = "M";
          break;
        case len > 3:
          abb = "K";
          break;
        default:
          return number;
      }
      return `${number.slice(0, place)}.${number.slice(
        place,
        place + 1
      )}${abb}`;
    },

    // Get Dashboard Data
    dashboard_fetch_data: function () {
      var self = this;
      var data = this._rpc({
        model: "crm.lead",
        method: "get_dashboard_data",
        args: [],
      }).then(function (result) {
        self.total_opports_wathiq = result["total_opports_wathiq"];
        self.total_opports_basic = result["total_opports_basic"];
        self.total_opports_enterprise = result["total_opports_enterprise"];
        self.total_opports_batch = result["total_opports_batch"];
        self.total_opports = result["total_opports"];
        // self.total_revenue= parseFloat(result['total_revenue']).toFixed('1');
        // self.total_revenue = result['total_revenue'];
        self.get_top_ten_clients1 = result["get_top_ten_clients_1"];
        self.get_top_ten_clients2 = result["get_top_ten_clients_2"];
        self.get_total_top_ten_clients_revenue = self.apply_humain_format(
          parseFloat(result["get_total_top_ten_clients_revenue"])
        );
        // self.get_total_top_ten_clients_revenue=result['get_total_top_ten_clients_revenue'];
        self.total_revenue = self.apply_humain_format(
          parseFloat(result["total_revenue"])
        );
        self.list_partners = result["list_partners"];
        self.list_account_managers = result["list_account_managers"];
        self.list_products = result["list_products"];
        self.growth_goal = self.apply_humain_format(
          parseFloat(result["growth_goal"])
        );
        // self.growth_goal= result['growth_goal'];
        self.percent_growth = result["percent_growth"];

        self.goal_status = result["goal_status"];
        self.currency = result.currency;
      });
      return $.when(data);
    },

    render_wathiq_basic_enterprise_bar_chart_graph: function (
      partner,
      product,
      account_manager
    ) {
      var self = this;
      $(".canvas_wathiq_basic_enterprise_bar_chart")
        .html("")
        .append(
          '<canvas id="wathiq_basic_enterprise_bar_chart" class="wathiq_basic_enterprise_bar_chart" width="340px" height="280px" ><canvas>'
        );
      var ctx = this.$("#wathiq_basic_enterprise_bar_chart");
      rpc
        .query({
          model: "crm.lead",
          method: "get_wathiq_basic_enterprise_bar_chart",
          args: [partner, product, account_manager],
        })
        .then(function (arrays) {
          var data = {
            labels: arrays[0],
            datasets: [
              {
                data: arrays[1],
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var listOfColor = [
                    ["#00BCB6", "#A7D7CE"],
                    ["#A7D7CE", "#E9F4F1"],
                    ["#5B508D", "#CEC9DB"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    arrays[0],
                    ctx,
                    chartArea
                  );
                },
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          var chart = new Chart(ctx, {
            type: "bar",
            data: data,
            options: {
              responsive: true,
              plugins: {
                legend: {
                  display: false,
                },
              },
              maintainAspectRatio: false,
            },
          });
        });
    },

    render_wathiq_enterprise_by_stages_bar_chart_graph: function (
      partner,
      product,
      account_manager
    ) {
      var self = this;
      $(".canvas_wathiq_enterprise_stages_bar_chart")
        .html("")
        .append(
          '<canvas id="wathiq_enterprise_stages_bar_chart" class="wathiq_enterprise_stages_bar_chart" width="340px" height="280px" ><canvas>'
        );
      var ctx = self.$("#wathiq_enterprise_stages_bar_chart");
      rpc
        .query({
          model: "crm.lead",
          method: "get_wathiq_enterprise_by_stages_bar_chart",
          args: [partner, product, account_manager],
        })
        .then(function (arrays) {
          var data = {
            labels: arrays[1],
            datasets: [
              {
                data: arrays[0],
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var listOfColor = [
                    ["#00BCB6", "#A7D7CE"],
                    ["#5B508D", "#CEC9DB"],
                    ["#3C85C1", "#CFDAED"],
                    ["#A7D7CE", "#E9F4F1"],
                    ["#798793", "#E0E4E7"],
                    ["#0A0A0A", "#798793"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    arrays[1],
                    ctx,
                    chartArea
                  );
                },
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          //create Chart class object
          var chart = new Chart(ctx, {
            type: "bar",
            data: data,
            options: {
              responsive: true,
              plugins: {
                legend: {
                  display: false,
                },
              },
              maintainAspectRatio: false,
            },
          });
        });
    },

    render_requests_by_stages_bar_chart_graph: function (
      partner,
      product,
      account_manager
    ) {
      var self = this;
      $(".canvas_wathiq_requests_bar_chart")
        .html("")
        .append(
          '<canvas id="wathiq_requests_bar_chart" class="wathiq_requests_bar_chart" width="340px" height="280px" ><canvas>'
        );
      var ctx = self.$("#wathiq_requests_bar_chart");
      rpc
        .query({
          model: "crm.lead",
          method: "get_wathiq_batch_by_stages_bar_chart",
          args: [partner, product, account_manager],
        })
        .then(function (arrays) {
          var data = {
            labels: arrays[1],
            datasets: [
              {
                label: "",
                data: arrays[0],
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var listOfColor = [
                    ["#00BCB6", "#A7D7CE"],
                    ["#5B508D", "#CEC9DB"],
                    ["#3C85C1", "#CFDAED"],
                    ["#A7D7CE", "#E9F4F1"],
                    ["#798793", "#E0E4E7"],
                    ["#0A0A0A", "#798793"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    arrays[1],
                    ctx,
                    chartArea
                  );
                },
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          //create Chart class object
          var chart = new Chart(ctx, {
            type: "bar",
            data: data,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
          });
        });
    },

    render_opports_month_graph: function (partner, product, account_manager) {
      var self = this;
      $(".canvas_opports_month")
        .html("")
        .append(
          '<canvas id="opports_month" class="opports_month" width="340px" height="280px" ><canvas>'
        );
      var ctx = self.$("#opports_month");
      rpc
        .query({
          model: "crm.lead",
          method: "get_opportunities_month_chart",
          args: [partner, product, account_manager],
        })
        .then(function (result) {
          // TODO :To be changed after having requirments more clear
          // Define the data
          var months = result[0]; // Add data values to array
          var count1 = result[1];
          var count2 = result[2];
          var myChart = new Chart(ctx, {
            type: "bar",
            data: {
              labels: [_t("Subscriptions"), _t("Transactions")],
              //leng: [_t('Subscriptions'), _t('Transactions')],
              datasets: [
                {
                  label: "",
                  data: [22, 42],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const {
                      ctx,
                      chartArea,
                      data: { labels },
                    } = chart;
                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = [
                      ["#00BCB6", "#A7D7CE"],
                      ["#5B508D", "#CEC9DB"],
                    ];
                    return Utils.generateGradients(
                      listOfColor,
                      labels,
                      ctx,
                      chartArea
                    );
                  },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                  type: "bar",
                },
              ],
            },
            options: {
              responsive: true, // Instruct chart js to respond nicely.
              maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
          });
        });
    },

    render_annual_chart_graph: function (partner, product, account_manager) {
      var self = this;
      //$('#canvas_annual_target').html("");
      $(".canvas_annual_target")
        .html("")
        .append(
          '<canvas id="annual_target" class="annual_target" width="340px" height="280px" ><canvas>'
        );
      var ctx = self.$("#annual_target");
      rpc
        .query({
          model: "crm.lead",
          method: "get_the_annual_target",
          args: [partner, product, account_manager],
        })
        .then(function (result) {
          // Define the data
          var myChart = new Chart(ctx, {
            type: "bar",
            data: {
              labels: result[0],
              datasets: [
                {
                  label: "",
                  data: [13435, 324, 5657], //result[1],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;
                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = ["#5B508D", "#CEC9DB"];
                    return Utils.generateGradients(
                      listOfColor,
                      result[0],
                      ctx,
                      chartArea
                    );
                  },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                },
              ],
            },

            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
          });
        });
    },

    change_template_by_filter: function (partner, product, account_manager) {
      var self = this;
      this._rpc({
        model: "crm.lead",
        method: "get_dashboard_data",
        args: [partner, product, account_manager],
      }).then(function (result) {
        $("#total_opports_wathiq")[0].innerHTML =
          result["total_opports_wathiq"];
        $("#total_opports_basic")[0].innerHTML = result["total_opports_basic"];
        $("#total_opports_enterprise")[0].innerHTML =
          result["total_opports_enterprise"];
        $("#total_opports_batch")[0].innerHTML = result["total_opports_batch"];
        $("#total_revenue")[0].innerHTML = parseFloat(
          result["total_revenue"]
        ).toFixed(1);
      });

      self.render_wathiq_basic_enterprise_bar_chart_graph(
        partner,
        product,
        account_manager
      );
      self.render_wathiq_enterprise_by_stages_bar_chart_graph(
        partner,
        product,
        account_manager
      );
      self.render_requests_by_stages_bar_chart_graph(
        partner,
        product,
        account_manager
      );
      self.render_opports_month_graph(partner, product, account_manager);
      self.render_annual_chart_graph(partner, product, account_manager);
    },
  });

  core.action_registry.add("ThiqahCRMDashboard", ThiqahCRMDashboard);

  return ThiqahCRMDashboard;
});
