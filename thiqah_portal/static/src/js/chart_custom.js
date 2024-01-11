odoo.define("thiqah.service.requests.dashboard", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var _t = core._t;
  var Utils = require("thiqah.Utils");
  var htmlLang = $("html").attr("lang");
  publicWidget.registry.ServiceRequestsDashbaord = publicWidget.Widget.extend({
    selector: ".requests_dashboard_class",
    jsLibs: ["/thiqah_base/static/libs/Chart.js"],
    evnets: {
      "click #cardlink a": "_onClickCard",
    },

    /**
     * @override
     */
    start: function () {
      var filterById = window.location.search.substring(1).split("=");
      // $('.card-holder').addClass('disblebd');
      // if(filterById == 'project_id'){
      //   $('.card').prop('disblebd',true);
      // }

      this.getDashboardData(filterById);
      return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    _onClickCard: function () {
      console.log("Card Click!!!");
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    getDashboardData: function (filterById) {
      var params = { dashboard: "requests_dashboard" };
      if (filterById[0]) {
        params[filterById[0]] = filterById[1];
      }
      // JSON RPC call
      ajax
        .jsonRpc("/render/dashboard/data", "call", params)
        .then(function (result) {
          // Gathering data
          var byStatus = result.byStatus;
          var byDepartment = result.byDepartment;
          var byServiceCategory = result.byServiceCategory;
          var byClient = result.byClient;
          var byCreateDate = result.byCreateDate;
          var BySlaIndicator = result.BySlaIndicator;

          var barColors = ["#a1c4d5", "#cbd7a7", "#daeddb", "#d8c8d8"];

          //By Creation date
          var min_max = $(byCreateDate).get(-1);
          var byCreateDate_ = byCreateDate.slice();
          var byCreateDateFinal = byCreateDate_.slice(
            0,
            byCreateDate_.indexOf(min_max)
          );
          var byCreateDateData = [];

          //TODO: Replace this to be in controller
          $.each(byCreateDateFinal, function (index, item) {
            var item_0 = item[0];
            var item_1 = item[1];
            item = {};
            item["x"] = item_0;
            item["y"] = item_1;
            byCreateDateData.push(item);
          });

          const ByCreationDate = document.getElementById("by_creation_date");

          let ByCreationlabels;
          if (htmlLang.includes("ar")) {
            ByCreationlabels = [
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
            ];
          } else {
            ByCreationlabels = [
              "January",
              "February",
              "March",
              "April",
              "May",
              "June",
              "July",
              "August",
              "September",
              "October",
              "November",
              "December",
            ];
          }
          const createDate = _.map(byCreateDateData, function (item) {
            return item.x;
          });

          const ByCreationData___ = {
            labels: ByCreationlabels,
            datasets: [
              {
                label: htmlLang.includes("ar")
                  ? "عدد الطلبات"
                  : "Count of requests",
                data: byCreateDateData,
                backgroundColor: "#00BCB4",
                pointStyle: "rectRounded",
                pointRadius: 8,
                pointHoverRadius: 10,
              },
            ],
          };
          const ByCreationDateConfig = {
            type: "scatter",
            data: ByCreationData___,
            options: {
              responsive: true,
              plugins: {
                tooltip: {
                  callbacks: {
                    title: () => {
                      return "";
                    },
                  },
                  rtl: htmlLang.includes("ar") ? true : false,
                  textDirection: htmlLang.includes("ar") ? 'rtl' : 'ltr',
                },
                legend: {
                  display: false,
                },
              },
              scales: {
                x: {
                  type: "category",
                  labels: createDate,
                },
              },
              animation: true,
            },
          };
          if (ByCreationDate != null) {
            new Chart(ByCreationDate, ByCreationDateConfig);
          }

          // By Status
          const byStatusElement = document.getElementById("by_status");
          var xValuesByStatus = byStatus[0].slice(0, 3),
            yValuesByStatus = byStatus[1].slice(0, 3),
            totalByStatus = _.reduce(
              yValuesByStatus,
              function (memo, num) {
                return memo + num;
              },
              0
            );

          const newyValuesByStatus = _.map(
            yValuesByStatus,
            function (item, index) {
              return xValuesByStatus[index] + " " + "(" + item + ")";
            }
          );
          const byStatusData = {
            labels: newyValuesByStatus,
            datasets: [
              {
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var colors = [
                    ["#3C85C1", "#00BCB6"],
                    ["#00BCB6", "#A7D7CE"],
                    ["#A7D7CE", "#EDF6F5"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    newyValuesByStatus,
                    ctx,
                    chartArea
                  );
                },
                data: yValuesByStatus,
              },
            ],
          };

          const byStatusConfig = {
            type: "doughnut",
            data: byStatusData,
            options: {
              maintainAspectRatio: false,
              cutout: "70%",
              responsive: true,
              plugins: {
                legend: {
                  rtl: htmlLang.includes("ar") ? true : false,
                  position: htmlLang.includes("ar") ? "left" : "right",
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
                  ctx.fillText(totalByStatus, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "إجمالي الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };
          if (byStatusElement != null) {
            new Chart(byStatusElement, byStatusConfig);
          }

          // Requests By Department
          const RequestsByDepartment = document
            .getElementById("requests_by_department")
            .getContext("2d");
          var xValuesRequestsByDepartment = byDepartment[0].slice(0, 2);
          var yValuesRequestsByDepartment = byDepartment[1].slice(0, 2);
          const totalByDepartment = _.reduce(
            yValuesRequestsByDepartment,
            function (memo, num) {
              return memo + num;
            },
            0
          );
          const newxValuesRequestsByDepartment = _.map(
            yValuesRequestsByDepartment,
            function (item, index) {
              return (
                xValuesRequestsByDepartment[index] + " " + "(" + item + ")"
              );
            }
          );
          const RequestsByDepartmentData = {
            labels: newxValuesRequestsByDepartment,
            datasets: [
              {
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var colors = [
                    ["#5B508D", "#51BBE5"],
                    ["#30B6E5", "#30B6E5"],
                  ];

                  return Utils.generateGradients(
                    colors,
                    newyValuesByStatus,
                    ctx,
                    chartArea
                  );
                },
                data: yValuesRequestsByDepartment,
              },
            ],
          };

          const RequestsByDepartmentConfig = {
            type: "doughnut",
            data: RequestsByDepartmentData,
            options: {
              maintainAspectRatio: false,
              cutout: "70%",
              responsive: true,
              plugins: {
                legend: {
                  rtl: htmlLang.includes("ar") ? true : false,
                  position: htmlLang.includes("ar") ? "left" : "right",
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
                  ctx.fillText(totalByDepartment, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "إجمالي الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };
          if (RequestsByDepartment != null) {
            new Chart(RequestsByDepartment, RequestsByDepartmentConfig);
          }

          // By Sla Indicator
          const BySlaIndicatorElement =
            document.getElementById("by_sla_indicator");
          var xValuesBySlaIndicator = BySlaIndicator[0];
          var yValuesBySlaIndicator = BySlaIndicator[1];
          const totalBySlaIndicator = _.reduce(
            yValuesBySlaIndicator,
            function (memo, num) {
              return memo + num;
            },
            0
          );
          const newxValuesBySlaIndicator = _.map(
            yValuesBySlaIndicator,
            function (item, index) {
              return xValuesBySlaIndicator[index] + " " + "(" + item + ")";
            }
          );
          const BySlaIndicatorData = {
            labels: newxValuesBySlaIndicator, //["Late", "On Time", "N/A"],
            datasets: [
              {
                data: yValuesBySlaIndicator,
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var colors = [
                    ["#3C85C1", "#5B508D"],
                    ["#5B508D", "#0A0A0A"],
                    ["#0A0A0A", "#0A0A0A"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    newyValuesByStatus,
                    ctx,
                    chartArea
                  );
                },
              },
            ],
          };

          const BySlaIndicatorConfig = {
            type: "doughnut",
            data: BySlaIndicatorData,
            options: {
              maintainAspectRatio: false,
              cutout: "70%",
              responsive: true,
              plugins: {
                legend: {
                  rtl: htmlLang.includes("ar") ? true : false,
                  position: htmlLang.includes("ar") ? "left" : "right",
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
                  ctx.fillText(totalBySlaIndicator, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "إجمالي الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 25
                  );
                },
              },
            ],
          };
          if (BySlaIndicatorElement != null) {
            new Chart(BySlaIndicatorElement, BySlaIndicatorConfig);
          }

          // By Service category
          const ServiceCategory = document.getElementById(
            "by_service_category"
          );
          const ServiceCategoryLabels = _.map(
            byServiceCategory[0],
            function (label) {
              return label.replaceAll(/ /g, "\n");
            }
          );
          const ServiceCategoryCount = byServiceCategory[1];
          const data = {
            labels: ServiceCategoryLabels,
            datasets: [
              {
                label: htmlLang.includes("ar")
                  ? "عدد الطلبات"
                  : "Count of requests",
                data: ServiceCategoryCount,
                borderRadius: 4,
                borderSkipped: "bottom",
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var backgroundColorList = [];
                  var listOfColor = [["#51BBE5", "#DAECF9"]];
                  return Utils.generateGradients(
                    listOfColor,
                    ServiceCategoryLabels,
                    ctx,
                    chartArea
                  );
                },
                borderWidth: 0,
              },
            ],
          };
          const config = {
            type: "bar",
            data: data,
            options: {
              responsive: true,
              plugins: {
                tooltip: {
                  rtl: htmlLang.includes("ar") ? true : false,
                  textDirection: htmlLang.includes("ar") ? 'rtl' : 'ltr',
                },
                legend: {
                  display: false,
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  position:  htmlLang.includes("ar") ?'right': 'left',
                },
                x: {
                  ticks: {
                    autoSkip: false,
                    maxRotation: 0,
                    minRotation: 0,
                  },
                },
              },
            },
            plugins: [
              {
                beforeInit: function (chart) {
                  chart.data.labels.forEach(function (e, i, a) {
                    if (/\n/.test(e)) {
                      a[i] = e.split(/\n/);
                    }
                    if (e.includes("-")) {
                      e.replace("-", "\n");
                    }
                  });
                },
              },
            ],
          };
          if (ServiceCategory != null) {
            new Chart(ServiceCategory, config);
          }

          // By Client
          const ByClient = document.getElementById("by_client");
          const ByClientLabels = byClient[0];
          const ByClientCount = byClient[1];
          const ByClientdata = {
            labels: ByClientLabels,
            datasets: [
              {
                label: htmlLang.includes("ar")
                  ? "عدد الطلبات"
                  : "Count of requests",
                data: ByClientCount,
                borderRadius: 4,
                borderSkipped: "bottom",
                backgroundColor: function (context) {
                  const chart = context.chart;
                  const { ctx, chartArea } = chart;

                  if (!chartArea) {
                    // This case happens on initial chart load
                    return;
                  }
                  var backgroundColorList = [];
                  var listOfColor = [
                    ["#00BCB6", "#A7D7CE"],
                    ["#A7D7CE", "#E9F4F1"],
                    ["#5B508D", "#CEC9DB"],
                    ["#3C85C1", "#CFDAED"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    ByClientLabels,
                    ctx,
                    chartArea
                  );
                },
                borderWidth: 0,
              },
            ],
          };
          const ByClientconfig = {
            type: "bar",
            data: ByClientdata,
            options: {
              responsive: true,
              plugins: {
                tooltip: {
                  rtl: htmlLang.includes("ar") ? true : false,
                  textDirection: htmlLang.includes("ar") ? 'rtl' : 'ltr',
                },
                legend: {
                  display: false,
                },
              },
            },
          };
          if (ByClient != null) {
            new Chart(ByClient, ByClientconfig);
          }
        });
    },
  });
});

$(document).ready(function () {
  var filterById = window.location.search.substring(1).split("=");
  if (filterById[0] == "project_id") {
    $(".card-body a").attr("href", "#");
    $(".card-body a").attr("class", "");
    $(".card-body").css("cursor", "not-allowed");
  }
});

odoo.define("financial.dashboard", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var Utils = require("thiqah.Utils");
  var session = require("web.session");
  var htmlLang = $("html").attr("lang");

  publicWidget.registry.FinancialDashboard = publicWidget.Widget.extend({
    selector: ".financial_dashboard_class",
    jsLibs: ["/thiqah_base/static/libs/Chart.js"],
    evnets: {
      "click .financial_filter": "_onClickFilter",
    },

    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments);
      var filterById = window.location.search.substring(1).split("=");

      this.getDashboardData(filterById);

      return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    getDashboardData: function (filterById) {
      var params = { dashboard: "financial_dashboard" };
      if (filterById[0]) {
        params[filterById[0]] = filterById[1];
      }

      // if (filterById){
      //   params ['filter'] =
      // }
      // JSON RPC call
      ajax
        .jsonRpc("/render/dashboard/data", "call", params)
        .then(function (result) {
          var cards_data = result.cards_data;
          // attribute card Cards Values
          $(".span_project_value").text(cards_data.project_value_sum);
          $(".available_balance").text(
            cards_data.available_balance ? cards_data.available_balance : 0
          );
          $(".balance_after_commitment").text(
            cards_data.balance_after_commitment
              ? cards_data.balance_after_commitment
              : 0
          );
          $(".actual_revenue").text(cards_data.actual_revenue);

          $(".total_margin_vat").text(cards_data.total_margin_vat);
          $(".total_utilizations_hours").text(
            cards_data.TotalUtilizationsHours
          );

          $(".number_headcount").text(cards_data.number_headcount);
          $(".number_of_pos").text(
            cards_data.number_of_pos ? cards_data.number_of_pos : 0
          );
          $(".vat").text(cards_data.vat ? cards_data.vat : 0);
          $(".actual_margin_amount").text(
            cards_data.actual_margin_amount
              ? cards_data.actual_margin_amount
              : 0
          );
          $(".actual_margin_percent").text(
            parseFloat(cards_data.margin_percent).toFixed(2)
          );
          // $('#actual_margin_percent').text(cards_data.margin_percent);

          $("#total_margin_vat").text(cards_data.total_margin_vat);
          $("#total_utilizations_hours").text(
            cards_data.TotalUtilizationsHours
          );

          // Gathering data
          var ActualCost = result.ActualCost;
          var MPActualCost = result.MPActualCost;
          var ProjectSupplyCost = result.ProjectSupplyCost;
          var MiscellaneousActualCost = result.MiscellaneousActualCost;
          var ProjectUtilitiesActualHours = result.ProjectUtilitiesActualHours;
          var ProjectsInvoices = result.ProjectsInvoices;
          var Contract = result.Contract;
          var Commitments = result.Commitments;
          // var TotalMarginVat = result.TotalMarginVat
          // var TotalMarginVatExpectations = result.TotalMarginVatExpectations

          var ticks = {
            callback: function (value, index, ticks) {
              const number = value.toString();
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
          };
          var barColors = [
            "#a1d683",
            "#009ABF",
            "#5db2c7",
            "#676e9f",
            "#3bd4ae",
          ];

          let parameters = {
            user_id: session.user_id,
          };

          // If the current user  have the groups (base.group_erp_manager,thiqah_crm.group_thiqah_sp_manager) or is a superuser
          // var def = session.user_has_group('base.group_portal').then(function(has_group){
          ajax
            .jsonRpc("/check/is/customer", "call", parameters)
            .then(function (result) {
              if (result) {
                // Project Utilities Actual Hours
                const ProjectUtilitiesActualHoursElement =
                  document.getElementById("project_utilities_actual_hours");
                var ProjectUtilitiesActualHoursLabels =
                  ProjectUtilitiesActualHours[0];
                const ProjectUtilitiesActualHoursData = {
                  labels: ProjectUtilitiesActualHoursLabels,
                  datasets: [
                    {
                      label: "Hours",
                      data: ProjectUtilitiesActualHours[1],
                      backgroundColor: barColors,
                      hoverBackgroundColor: barColors,

                      borderColor: ["#FFFFFF"],
                    },
                  ],
                };
                const ProjectUtilitiesActualHoursConfig = {
                  type: "bar",
                  data: ProjectUtilitiesActualHoursData,
                  options: {
                    responsive: true,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                };
                if (ProjectUtilitiesActualHoursElement != null) {
                  new Chart(
                    ProjectUtilitiesActualHoursElement,
                    ProjectUtilitiesActualHoursConfig
                  );
                }

                // Miscellaneous Actual Cost
                const MiscellaneousActualCostElemnt = document.getElementById(
                  "miscellaneous_actual_cost"
                );
                var MPActualCostLabels = MiscellaneousActualCost[0];
                const MiscellaneousActualCostData = {
                  labels: MPActualCostLabels,
                  datasets: [
                    {
                      label: htmlLang.includes("ar") ?'التكلفة': 'cost',
                      data: MiscellaneousActualCost[1],
                      backgroundColor: barColors,
                      hoverBackgroundColor: barColors,

                      borderColor: ["#FFFFFF"],
                    },
                  ],
                };
                const MiscellaneousActualCostConfig = {
                  type: "bar",
                  data: MiscellaneousActualCostData,
                  options: {
                    responsive: true,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                };
                if (MiscellaneousActualCostElemnt != null) {
                  new Chart(
                    MiscellaneousActualCostElemnt,
                    MiscellaneousActualCostConfig
                  );
                }

                // MP Actual Cost
                const MPActualCostElement =
                  document.getElementById("mp_actual_cost");
                var MPActualCostLabels = MPActualCost[0];
                const MPActualCostData = {
                  labels: MPActualCostLabels,
                  datasets: [
                    {
                      label: htmlLang.includes("ar") ?'التكلفة': 'cost',
                      data: MPActualCost[1],
                    },
                  ],
                };
                const MPActualCostConfig = {
                  type: "bar",
                  data: MPActualCostData,
                  options: {
                    responsive: true,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                };
                if (MPActualCostElement != null) {
                  new Chart(MPActualCostElement, MPActualCostConfig);
                }

                // Project And Supply Actual Cost
                const ProjectSupplyActualCost = document.getElementById(
                  "project_supply_actual_cost"
                );
                var MPActualCostLabels = ProjectSupplyCost[0];
                const formatLabels = function (arr) {
                  return _.map(arr, function (label) {
                    return label.replaceAll(/ /g, "\n");
                  });
                };
                const ProjectSupplyActualCostData = {
                  labels: MPActualCostLabels,
                  datasets: [
                    {
                      label: htmlLang.includes("ar") ?'التكلفة': 'cost',
                      data: ProjectSupplyCost[1],
                      backgroundColor: barColors,
                      hoverBackgroundColor: barColors,

                      borderColor: ["#FFFFFF"],
                    },
                  ],
                };
                const ProjectSupplyActualCostConfig = {
                  type: "bar",
                  data: ProjectSupplyActualCostData,
                  options: {
                    responsive: true,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      yAxes: [
                        {
                          beginAtZero: true,
                          ticks: {
                            callback: function (val, index) {
                              return val + "FFF";
                            },
                          },
                        },
                      ],
                    },
                  },
                };
                if (ProjectSupplyActualCost != null) {
                  new Chart(
                    ProjectSupplyActualCost,
                    ProjectSupplyActualCostConfig
                  );
                }
              } else {
                // Total Actual Cost
                const ActualCostElement =
                  document.getElementById("total_actual_cost");
                var ActualCostLabels = ActualCost[0];
                const ActualCostData = {
                  labels: _.map(ActualCostLabels, function (label) {
                    return label.replaceAll(/ /g, "\n");
                  }),
                  datasets: [
                    {
                      data: ActualCost[1],
                      borderRadius: 4,
                      borderSkipped: "bottom",
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
                          ["#51BBE5", "#DAECF9"],
                          ["#3C85C1", "#CFDAED"],
                        ];
                        return Utils.generateGradients(
                          listOfColor,
                          ActualCostLabels,
                          ctx,
                          chartArea
                        );
                      },
                    },
                  ],
                };
                const ActualCostConfig = {
                  type: "bar",
                  data: ActualCostData,
                  options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: {
                        ticks: {
                          autoSkip: false,
                          maxRotation: 0,
                          minRotation: 0,
                        },
                      },
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                  plugins: [
                    {
                      beforeInit: function (chart) {
                        chart.data.labels.forEach(function (e, i, a) {
                          if (/\n/.test(e)) {
                            a[i] = e.split(/\n/);
                          }
                        });
                      },
                    },
                  ],
                };
                if (ActualCostElement != null) {
                  new Chart(ActualCostElement, ActualCostConfig);
                }

                // Commitments
                const CommitmentsElement =
                  document.getElementById("commitments_chart");
                var CommitmentsLabels = Commitments[0];
                const CommitmentsData = {
                  labels: _.map(CommitmentsLabels, function (label) {
                    return label.replaceAll(/ /g, "\n");
                  }),
                  datasets: [
                    {
                      label: htmlLang.includes("ar") ?'التكلفة': 'cost',
                      data: Commitments[1],
                      borderRadius: 4,
                      borderSkipped: "bottom",
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
                        ];
                        return Utils.generateGradients(
                          listOfColor,
                          CommitmentsLabels,
                          ctx,
                          chartArea
                        );
                      },
                    },
                  ],
                };
                const CommitmentsDataConfig = {
                  type: "bar",
                  data: CommitmentsData,
                  options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: {
                        ticks: {
                          autoSkip: false,
                          maxRotation: 0,
                          minRotation: 0,
                        },
                      },
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                  plugins: [
                    {
                      beforeInit: function (chart) {
                        chart.data.labels.forEach(function (e, i, a) {
                          if (/\n/.test(e)) {
                            a[i] = e.split(/\n/);
                          }
                        });
                      },
                    },
                  ],
                };
                if (CommitmentsElement != null) {
                  new Chart(CommitmentsElement, CommitmentsDataConfig);
                }

                //  Projects Invoices
                const InvoicesElement =
                  document.getElementById("projects_invoices");

                var InvoicesLabels = ProjectsInvoices[0];
                var formattedInvoicesLabels = _.map(
                  InvoicesLabels,
                  function (label) {
                    return label.replaceAll(/ /g, "\n");
                  }
                );
                const InvoicesData = {
                  labels: formattedInvoicesLabels,
                  datasets: [
                    {
                      label: htmlLang.includes("ar") ?'التكلفة': 'cost',
                      data: ProjectsInvoices[1],
                      borderRadius: 4,
                      borderSkipped: "bottom",
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
                          formattedInvoicesLabels,
                          ctx,
                          chartArea
                        );
                      },
                    },
                  ],
                };
                const InvoicesConfig = {
                  type: "bar",
                  data: InvoicesData,
                  options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                      x: {
                        ticks: {
                          autoSkip: false,
                          maxRotation: 0,
                          minRotation: 0,
                        },
                      },
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                  plugins: [
                    {
                      beforeInit: function (chart) {
                        chart.data.labels.forEach(function (e, i, a) {
                          if (/\n/.test(e)) {
                            a[i] = e.split(/\n/);
                          }
                        });
                      },
                    },
                  ],
                };
                if (InvoicesElement != null) {
                  new Chart(InvoicesElement, InvoicesConfig);
                }

                // Contract
                const ContractElement =
                  document.getElementById("contract_chart");
                var ContractLabels = Contract[0];
                const ContractData = {
                  labels: _.map(ContractLabels, function (label) {
                    return label.replaceAll(/ /g, "\n");
                  }),
                  datasets: [
                    {
                      label: htmlLang.includes("ar") ?'التكلفة': 'cost',
                      data: Contract[1],
                      borderRadius: 4,
                      borderSkipped: "bottom",
                      backgroundColor: function (context) {
                        const chart = context.chart;
                        const { ctx, chartArea } = chart;

                        if (!chartArea) {
                          // This case happens on initial chart load
                          return;
                        }
                        var listOfColor = [
                          ["#3C85C1", "#CFDAED"],
                          ["#5B508D", "#CEC9DB"],
                        ];
                        return Utils.generateGradients(
                          listOfColor,
                          ContractLabels,
                          ctx,
                          chartArea
                        );
                      },
                    },
                  ],
                };
                const ContractConfig = {
                  type: "bar",
                  data: ContractData,
                  options: {
                    responsive: true,
                    indexAxis: "x",
                    plugins: { legend: { display: false } },
                    scales: {
                      x: {
                        ticks: {
                          autoSkip: false,
                          maxRotation: 0,
                          minRotation: 0,
                        },
                      },
                      y: {
                        beginAtZero: true,
                        ticks: ticks,
                        position:  htmlLang.includes("ar") ?'right': 'left',
                      },
                    },
                  },
                };
                if (ContractElement != null) {
                  new Chart(ContractElement, ContractConfig);
                }
              }
            });

          // Finacial Chart View
          const dounoutLine = {
            id: "dounoutLine",
            beforeDatasetsDraw(chart, args, options) {
              const {
                ctx,
                data,
                height,
                width,
                chartArea: { top, bottom, left, right },
              } = chart;
              ctx.save();
              const halfWidth = width / 2 + left;
              const halfHeight = height / 2 + top;
              let pos = 0;
              data.datasets[0].data.forEach(function (datapoint, idx) {
                const { x, y } = chart
                  .getDatasetMeta(0)
                  .data[idx].tooltipPosition();
                ctx.lineWidth = 1;
                ctx.strokeStyle = "#798793";
                const xLine = x >= halfWidth ? x + 15 : x - 15;
                const yLine = y >= halfHeight ? x + 15 : x - 15;
                const extraLine = x >= halfWidth ? 15 : -15;
                const textWidth = ctx.measureText(data.labels[idx]).width;
                const textWidthPosition =
                  x >= halfWidth ? textWidth : -textWidth;
                if (!data.datasets[0].data[idx]) return;
                ctx.beginPath();
                if (pos == 1) {
                  ctx.beginPath();
                  ctx.moveTo(0, 0);
                  ctx.lineTo(0, y);
                  ctx.lineTo(xLine - 30, y);
                  ctx.stroke();
                }
                if (pos == 0) {
                  ctx.beginPath();
                  ctx.moveTo(x + 30, y);
                  ctx.lineTo(width, y);
                  ctx.lineTo(width, height);
                  ctx.stroke();
                }
                pos++;
              });
            },
          };

          const actualCommitment = document.getElementById("actual_commitment");
          const actualCommitmentData = {
            labels: ["Balance After Commitment", "Actual Available Balance"],
            datasets: [
              {
                data: [
                  cards_data.balance_after_commitment
                    ? parseInt(cards_data.balance_after_commitment)
                    : 0,
                  cards_data.available_balance
                    ? parseInt(cards_data.available_balance)
                    : 0,
                ],
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
                  var colors = [
                    ["#00BCB6", "#3C85C1"],
                    ["#00BCB6", "#A7D7CE"],
                  ];

                  return Utils.generateGradients(
                    colors,
                    labels,
                    ctx,
                    chartArea
                  );
                },
                hoverBorderWidth: 0,
              },
            ],
          };
          const actualCommitmentConfig = {
            type: "doughnut",
            data: actualCommitmentData,
            options: {
              layout: { padding: 20 },
              cutout: "70%",
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false,
                },
              },
            },
            plugins: [dounoutLine],
          };
          if (actualCommitment != null) {
            new Chart(actualCommitment, actualCommitmentConfig);
          }
          const vatRevenue = document.getElementById("vatRevenue");
          const vatRevenueData = {
            labels: ["Actual Revenu", "Total Utilization With Margin And Vat"],
            datasets: [
              {
                data: [
                  parseInt(cards_data.actual_revenue),
                  parseInt(cards_data.total_margin_vat),
                ],

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
                  var colors = [
                    ["#51BBE5", "#DAECF9"],
                    ["#3C85C1", "#CFDAED"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    labels,
                    ctx,
                    chartArea
                  );
                },
                hoverBorderWidth: 0,
              },
            ],
          };
          const vatRevenueConfig = {
            type: "doughnut",
            data: vatRevenueData,
            options: {
              layout: { padding: 20 },
              cutout: "70%",
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false,
                },
              },
            },

            plugins: [dounoutLine],
          };
          if (vatRevenue != null) {
            new Chart(vatRevenue, vatRevenueConfig);
          }
          const marginVat = document.getElementById("marginVat");
          const marginVatData = {
            labels: ["Margin", "VAT"],
            datasets: [
              {
                data: [
                  cards_data.actual_margin_amount
                    ? parseInt(cards_data.actual_margin_amount)
                    : 0,
                    cards_data.vat ? parseInt(cards_data.vat) : 0,
                ],
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
                  var colors = [
                    ["#5B508D", "#3C85C1"],
                    ["#5B508D", "#0A0A0A"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    labels,
                    ctx,
                    chartArea
                  );
                },
                hoverBorderWidth: 0,
              },
            ],
          };
          const marginVatConfig = {
            type: "doughnut",
            data: marginVatData,
            options: {
              layout: { padding: 20 },
              cutout: "70%",
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false,
                },
              },
            },

            plugins: [dounoutLine],
          };
          if (marginVat != null) {
            new Chart(marginVat, marginVatConfig);
          }
        });
    },
  });
});
