odoo.define("thiqah.portal.aahd.dashboard", function (require) {
  "use strict";

  var AbstractAction = require("web.AbstractAction");
  var core = require("web.core");
  var ajax = require("web.ajax");
  var Utils = require("thiqah.Utils");
  var formatCash = Utils.formatCash;
  var formatCurrency = Utils.formatCurrency;
  var _t = core._t;
  var QWeb = core.qweb;

  var year;

  var ThiqahAahdDashboard = AbstractAction.extend({
    jsLibs: [
      "/thiqah_base/static/libs/Chart.js",
      "/thiqah_base/static/libs/chartjs-plugin-datalabels.min.js",
    ],
    hasControlPanel: false,
    template: "aahd_sales_dashboard",
    events: {
      "change #choose_year": function (e) {
        e.stopPropagation();

        year = $("#choose_year option:selected").text();
        $("#choose_year selectd").attr("selected", "selected");
        sessionStorage.setItem("key", year);
        location.reload();
      },
    },
    init: function (parent, context) {
      this._super(parent, context);
      this.dashboards_templates = ["aahd_sales_dashboard_document"];
      this.yearsInterval = [
        new Date().getFullYear() - 1,
        new Date().getFullYear(),
      ];
      if (!sessionStorage.getItem("key"))
        sessionStorage.setItem("key", new Date().getFullYear());
    },
    start: function () {
      var self = this;
      this.set("title", "Aahd Sales Dashboard");
      let data = sessionStorage.getItem("key");

      var def = this._super().then(function () {
        self.render_dashboards();
        self.render_dashbaord_data(parseInt(data));
        sessionStorage.removeItem("key");
        self.$el.find(".selectpicker").selectpicker();
        if (data) {
          self.$("#choose_year").val(data);
          self.$el
            .find(".bootstrap-select .filter-option-inner-inner")
            .text(data);
        } else {
          data = new Date().getFullYear();
          self.$("#choose_year").val(data);
          self.$el
            .find(".bootstrap-select .filter-option-inner-inner")
            .text(data);
        }
      });
      return def;
    },

    render_dashboards: function () {
      var self = this;
      // Append the widget to the proper place in the DOM.
      _.each(this.dashboards_templates, function (template) {
        self
          .$(".sales_aahd_DASHBOARD")
          .append(QWeb.render(template, { widget: self }));
      });
    },

    // https://www.30secondsofcode.org/articles/s/js-remove-trailing-zeros
    toFixedWithoutZeros: function (num, precision) {
      return num.toFixed(precision).replace(/\.0+$/, "");
    },

    render_dashbaord_data: function (year) {
      var distributionProductId = this.$("#distributionProduct");
      var distributionSourceId = this.$("#distributionSource");
      var nonDigitalChartID = this.$("#nonDigitalChart");
      var digitalChartID = this.$("#digitalChart");
      var opportunityValueChartID = this.$("#opportunityValueChart");
      var monthlyRevenueChartID = this.$("#monthlyRevenueChart");
      var monthlyGrowthChartChartID = this.$("#monthlyGrowthChart");
      let parameters = {};
      if (year) {
        parameters = { year: year };
      } else {
        parameters = { year: new Date().getFullYear() - 1 };
      }
      var self = this;
      var symbol = this._rpc({
        route: "/website/get_current_currency",
      }).then((res) => {
        return ({ symbol } = res);
      });
      // One call to get all dashboard data
      ajax
        .jsonRpc("/aahd/sales/dashboard", "call", parameters)
        .then(function (result) {
          // Card data
          $("#total_opportunities").text(result["total_opportunities"]);
          $("#non_digital_opportunities").text(
            result["non_digital_opportunities"]
          );
          $("#digital_opportunities").text(result["digital_opportunities"]);

          $("#value_winning_rate").text(result["value_winning_rate"]);
          $("#quantity_value_rate").text(result["quantity_value_rate"]);
          $("#goal_amount").text(
            `${symbol} ${formatCurrency(result["goal_growth"])}`
          );
          $("#revenues_won_stage").text(
            `${symbol} ${formatCurrency(result["revenues_won_stage"])}`
          );

          $("#goal_percent").text(result["goal_percent"]);
          $("#margin_percent").text(result["margin_percent"]);

          $("#margin_value").text(
            `${symbol} ${formatCurrency(result["margin_value"])}`
          );

          const goal_status = result.goal_status;
          if (goal_status == true) {
            $("#sort_up").removeClass("d-none");
            $("#sort_down").addClass("d-none");
            $(".goal_span")
              .removeClass("danger-badge")
              .addClass("badge-approved");
          } else if (goal_status == false) {
            $("#sort_down").removeClass("d-none");
            $("#sort_up").addClass("d-none");
            $(".goal_span")
              .removeClass("badge-approved")
              .addClass("danger-badge");
          } else if (goal_status == "no_status") {
            $("#sort_down").addClass("d-none");
            $("#sort_up").addClass("d-none");
            $("#bullseye_wathiq").removeClass("d-none");
          }
          var projectsAwarded = result.projectsAwarded;
          var divsToAppend = "";
          var i;
          let opportunity_value = 0;

          $.each(projectsAwarded, function (index, item) {
            const number = item[1].toString();
            opportunity_value = ``;
            divsToAppend += `
             <tr><td class="body2">${
               item[0]
             }</td><td class="body2 text-right">${symbol} ${formatCurrency(
              number
            )}</td></tr>
              `;
          });
          $("#table_awarded tbody").append(divsToAppend);

          // Chart(s) data
          const total_opportunities = parseInt(result.total_opportunities);

          var distributionProduct = result.distributionProduct;
          var distributionSource = result.distributionSource;
          var distributionNonDigital = result.distributionNonDigital;
          var distributionDigital = result.distributionDigital;
          var MonthlyRevenue = result.MonthlyRevenue;
          var OpportunityValueChart = result.OpportunityValueChart;
          var MonthlyGrowth = result.MonthlyGrowth;

          const datalabelsFormatter = {
            formatter: function (value, context) {
              var number_ =
                total_opportunities != 0
                  ? (context.chart.data.datasets[0].data[context.dataIndex] /
                      total_opportunities) *
                    100
                  : 0;
              return number_.toFixed(1).replace(/\.0+$/, "").toString() + "%";
            },
          };
          const datalabelsStyle = {
            color: "#0A0A0A",
            backgroundColor: "#ffffff",
            borderColor: false,
            borderWidth: 0,
            borderRadius: 8,
            anchor: "end",
            font: {
              weight: "700",
            },
            padding: 6,
          };

          // Distribution Product
          new Chart(distributionProductId, {
            type: "bar",
            data: {
              labels: distributionProduct[0],
              datasets: [
                {
                  label: "Count of Opportunities",
                  data: distributionProduct[1],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;

                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = [["#A7D7CE", "#E9F4F1"]];
                    return Utils.generateGradients(
                      listOfColor,
                      distributionProduct[0],
                      ctx,
                      chartArea
                    );
                  },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                  datalabels: { ...datalabelsFormatter, ...datalabelsStyle },
                },
              ],
            },
            options: {
              plugins: {
                legend: {
                  display: false,
                },
                tooltip: {
                  callbacks: {
                    afterTitle: function (tooltipItem, chart) {
                      return "----------------";
                    },
                    afterBody: function (tooltipItem, chart) {
                      return "----------------";
                    },
                    footer: function (tooltipItem, chart) {
                      return `Total Amount: ${symbol} ${formatCurrency(
                        distributionProduct[2][tooltipItem[0].dataIndex]
                      )}`;
                    },
                  },
                },
              },
            },
            plugins: [ChartDataLabels],
          });

          // Distribution Source
          new Chart(distributionSourceId, {
            type: "bar",
            data: {
              labels: distributionSource[0],
              datasets: [
                {
                  label: "Count of Opportunities",
                  data: distributionSource[1],
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
                      ["#51BBE5", "#DAECF9"],
                    ];
                    return Utils.generateGradients(
                      listOfColor,
                      distributionSource[1],
                      ctx,
                      chartArea
                    );
                  },
                  datalabels: { ...datalabelsFormatter, ...datalabelsStyle },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                },
              ],
            },
            options: {
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
            plugins: [ChartDataLabels],
          });
          // Distribution Non Digital
          new Chart(nonDigitalChartID, {
            type: "bar",
            data: {
              labels: distributionNonDigital[0],
              datasets: [
                {
                  label: "Count of Opportunities",
                  data: distributionNonDigital[1],
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
                      ["#3C85C1", "#CFDAED"],
                      ["#51BBE5", "#DAECF9"],
                    ];
                    return Utils.generateGradients(
                      listOfColor,
                      distributionNonDigital[0],
                      ctx,
                      chartArea
                    );
                  },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                  datalabels: {
                    ...datalabelsStyle,
                    ...datalabelsFormatter,
                  },
                },
              ],
            },
            options: {
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
            plugins: [ChartDataLabels],
          });

          // Distribution Digital
          new Chart(digitalChartID, {
            type: "bar",
            data: {
              labels: distributionDigital[0],
              datasets: [
                {
                  label: "Count of Opportunities",
                  data: distributionDigital[1],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;

                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = [
                      ["#A7D7CE", "#E9F4F1"],
                      ["#3C85C1", "#CFDAED"],
                      ["#00BCB6", "#A7D7CE"],
                      ["#5B508D", "#CEC9DB"],
                      ["#5B508D", "#CEC9DB"],
                    ];
                    return Utils.generateGradients(
                      listOfColor,
                      distributionDigital[0],
                      ctx,
                      chartArea
                    );
                  },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                  datalabels: {
                    ...datalabelsStyle,
                    ...datalabelsFormatter,
                  },
                },
              ],
            },
            options: {
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
            plugins: [ChartDataLabels],
          });

          var callbacks = {
            label: function (tooltipItem, data) {
              const number = tooltipItem.raw;

              return `${formatCash(number)}`;
            },
          };
          // Monthly Revenue Chart
          new Chart(monthlyRevenueChartID, {
            type: "bar",
            data: {
              labels: MonthlyRevenue[0],
              datasets: [
                {
                  label: "monthly Revenue",
                  data: MonthlyRevenue[1],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;

                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = [["#3C85C1", "#CFDAED"]];
                    return Utils.generateGradients(
                      listOfColor,
                      MonthlyRevenue[0],
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
              plugins: {
                legend: {
                  display: false,
                },
                tooltip: {
                  callbacks: callbacks,
                },
              },
              scales: {
                y: {
                  ticks: {
                    callback: function (val, index) {
                      return `${formatCash(val)}`;
                    },
                  },
                },
              },
            },
          });
          // Opportunity Value Chart
          new Chart(opportunityValueChartID, {
            type: "bar",
            data: {
              labels: OpportunityValueChart[0],
              datasets: [
                {
                  label: "Opportunities Value",
                  data: OpportunityValueChart[1],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;
                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = [
                      ["#A7D7CE", "#E9F4F1"],
                      ["#3C85C1", "#CFDAED"],
                      ["#00BCB6", "#A7D7CE"],
                      ["#5B508D", "#CEC9DB"],
                    ];
                    return Utils.generateGradients(
                      listOfColor,
                      OpportunityValueChart[0],
                      ctx,
                      chartArea
                    );
                  },
                  borderRadius: 4,
                  borderSkipped: "bottom",
                  datalabels: {
                    ...datalabelsStyle,
                    formatter: function (value, context) {
                      var number =
                        context.chart.data.datasets[0].data[context.dataIndex];
                      const number_ = parseInt(number).toString();
                      const len = number_.length;
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
                          return number_;
                      }
                      return `${number_.slice(0, place)}.${number_.slice(
                        place,
                        place + 1
                      )}${abb}`;
                    },
                  },
                },
              ],
            },

            options: {
              plugins: {
                legend: {
                  display: false,
                },
                tooltip: {
                  // callbacks: callbacks,
                  callbacks: {
                    label: function (tooltipItem, data) {
                      return formatCash(tooltipItem.parsed.y);
                    },
                    afterTitle: function (tooltipItem, chart) {
                      return "----------------";
                    },

                    afterBody: function (tooltipItem, chart) {
                      return (
                        "---------------- \n" +
                        `Count of Opportunities: ${
                          OpportunityValueChart[2][tooltipItem[0].dataIndex]
                        }`
                      );
                    },
                    footer: function (tooltipItem, chart) {
                      let value_rate =
                        OpportunityValueChart[3][tooltipItem[0].dataIndex];
                      let quantity_rate =
                        OpportunityValueChart[4][tooltipItem[0].dataIndex];
                      if (value_rate != 101 || quantity_rate != 101) {
                        return (
                          "Value Rate: " +
                          value_rate +
                          "\nQuantity Rate: " +
                          quantity_rate
                        );
                      }
                    },
                  },
                },
              },
            },
            plugins: [ChartDataLabels],
          });
          // Monthly Growth
          new Chart(monthlyGrowthChartChartID, {
            type: "line",
            data: {
              labels: MonthlyGrowth[0],
              datasets: [
                {
                  label: "Monthly Growth",
                  data: MonthlyGrowth[1],
                  backgroundColor: function (context) {
                    const chart = context.chart;
                    const { ctx, chartArea } = chart;

                    if (!chartArea) {
                      // This case happens on initial chart load
                      return;
                    }
                    var listOfColor = [["#A7D7CE", "#E9F4F1"]];
                    return Utils.generateGradients(
                      listOfColor,
                      MonthlyGrowth[1],
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
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
          });
        });
    },
  });

  // Registering the widget in the action registry.
  core.action_registry.add("ThiqahAahdDashboard", ThiqahAahdDashboard);

  return ThiqahAahdDashboard;
});
