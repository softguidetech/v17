odoo.define("thiqah.inquiries.dashboard", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var Utils = require("thiqah.Utils");
  var htmlLang = $("html").attr("lang");

  publicWidget.registry.InquiriesDashboard = publicWidget.Widget.extend({
    selector: ".inquiries_dashboard_class",
    jsLibs: ["/thiqah_base/static/libs/Chart.js"],
    /**
     * @override
     */
    start: function () {
      this.getDashboardData();
      return this._super.apply(this, arguments);
    },

    chartFunc: function (type, ctx, data, options, plugins) {
      return new Chart(ctx, {
        type: type,
        data: data,
        options: options,
        plugins,
      });
    },

    getDashboardData: function () {
      var self = this;
      ajax
        .jsonRpc("/render/inquiries/dashboard/data", "call", {})
        .then(function (result) {
          var ctxByStatus = document
            .getElementById("inquiries_by_status")
            .getContext("2d");
          var ctxByDepartment = document
            .getElementById("inquiries_by_department")
            .getContext("2d");
          var ctxBySLA = document
            .getElementById("inquiries_by_sla_indicator")
            .getContext("2d");
          var ctxBYGategory = document.getElementById("inquiries_by_category");
          var ctxByCreationDate = document
            .getElementById("inquiries_by_creation_date")
            .getContext("2d");
          var ctxByClient = document.getElementById("inquiries_by_client");

          var doughnutOptions = {
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
              tooltip: {
                rtl: htmlLang.includes("ar") ? true : false,
                textDirection: htmlLang.includes("ar") ? 'rtl' : 'ltr',
              },
            },
            cutout: "70%",
            maintainAspectRatio: false,
            scales: {
              x: {
                grid: {
                  display: false,
                },
                display: false,
                ticks: {
                  display: false,
                },
              },
              y: {
                grid: {
                  display: false,
                },
                position:  htmlLang.includes("ar") ?'right': 'left',
                display: false,
                ticks: {
                  // beginAtZero: true,
                  display: false,
                },
              },
            },
          };

          var barChartOptions = {
            // maintainAspectRatio: false,
            responsive: true,
            scales: {
              y: {
                position:  htmlLang.includes("ar") ?'right': 'left',
              }
            },
            plugins: {
              tooltip: {
                rtl: htmlLang.includes("ar") ? true : false,
                textDirection: htmlLang.includes("ar") ? 'rtl' : 'ltr',
              },
              legend: {
                display: false,
              },
            },
          };

          const reducer = (accumulator, curr) => accumulator + curr;
          // BY Status Chart
          var byStatus = result.by_status.slice(0, 3);
          console.log(byStatus);
          var byStatusLabels = _.map(byStatus, function (item) {
            return item[0];
          });
          var byStatusDatas = _.map(byStatus, function (item) {
            return item[1];
          });
          var byStatusSum = 0;
          byStatusSum =
            byStatusDatas.length > 0 ? byStatusDatas.reduce(reducer) : 0;

          var byStatusData = {
            label: "",
            labels: _.map(byStatusLabels, function (item, index) {
              return `${item} (${byStatusDatas[index]})`;
            }),
            datasets: [
              {
                data: byStatusDatas,
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
                    ["#3C85C1", "#5B508D"],
                    ["#5B508D", "#0A0A0A"],
                    ["#0A0A0A", "#0A0A0A"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    labels,
                    ctx,
                    chartArea
                  );
                },
              },
            ],
          };
          self.chartFunc(
            "doughnut",
            ctxByStatus,
            byStatusData,
            doughnutOptions,
            [
              {
                beforeDatasetsDraw(chart, args, options) {
                  const { ctx, data } = chart;
                  ctx.save();
                  const xCoord =
                      chart.getDatasetMeta(0).data.length > 0
                        ? chart.getDatasetMeta(0).data[0].x
                        : 100,
                    yCoord =
                      chart.getDatasetMeta(0).data.length > 0
                        ? chart.getDatasetMeta(0).data[0].y
                        : 100;
                  ctx.font = "400 75px TanseekModernProArabic";
                  ctx.fillStyle = "#0A0A0A";
                  ctx.textAlign = "center";
                  ctx.textBaseLine = "middle";
                  ctx.fillText(byStatusSum, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(htmlLang.includes("ar")
                      ? "إجمالي الطلبات"
                      : "TOTAL REQUESTS", xCoord, yCoord + 25);
                },
              },
            ]
          );

          // By Department Chart
          var byDepartment = result.by_department.slice(0, 3);

          var byDepartmentLabels = _.map(byDepartment, function (item) {
            return item[0];
          });
          var byDepartmentDatas = _.map(byDepartment, function (item) {
            return item[1];
          });

          var byDepartmentSum = 0;

          byDepartmentSum =
            byDepartmentDatas.length > 0
              ? byDepartmentDatas.reduce(reducer)
              : 0;
          var byDepartmentData = {
            label: "",
            labels: _.map(byDepartmentLabels, function (item, index) {
              return `${item} (${byDepartmentDatas[index]})`;
            }),
            datasets: [
              {
                data: byDepartmentDatas,
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
                    ["#3C85C1", "#00BCB6"],
                    ["#00BCB6", "#A7D7CE"],
                    ["#A7D7CE", "#EDF6F5"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    labels,
                    ctx,
                    chartArea
                  );
                },
              },
            ],
          };
          self.chartFunc(
            "doughnut",
            ctxByDepartment,
            byDepartmentData,
            doughnutOptions,
            [
              {
                beforeDatasetsDraw(chart, args, options) {
                  const { ctx } = chart;
                  ctx.save();
                  const xCoord =
                      chart.getDatasetMeta(0).data.length > 0
                        ? chart.getDatasetMeta(0).data[0].x
                        : 100,
                    yCoord =
                      chart.getDatasetMeta(0).data.length > 0
                        ? chart.getDatasetMeta(0).data[0].y
                        : 100;
                  ctx.font = "400 75px TanseekModernProArabic";
                  ctx.fillStyle = "#0A0A0A";
                  ctx.textAlign = "center";
                  ctx.textBaseLine = "middle";
                  ctx.fillText(byDepartmentSum, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(htmlLang.includes("ar")
                      ? "إجمالي الطلبات"
                      : "TOTAL REQUESTS", xCoord, yCoord + 25);
                },
              },
            ]
          );

          // By SLA Chart
          var BySLALabels = htmlLang.includes("ar")
          ?["متأخر","في الوقت","نشط"]:["Late", "On Time", "Active"];
          var BySLADatas = result.by_sla;
          var BySLAData = {
            label: "",
            labels: _.map(BySLALabels, function (item, index) {
              return `${item} ${BySLADatas[index]}`;
            }),
            datasets: [
              {
                data: BySLADatas,
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
                    ["#A7D7CE", "#E9F4F1"],
                    ["#5B508D", "#CEC9DB"],
                    ["#3C85C1", "#CFDAED"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    labels,
                    ctx,
                    chartArea
                  );
                },
              },
            ],
          };
          self.chartFunc("doughnut", ctxBySLA, BySLAData, doughnutOptions, [
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
                ctx.fillText(BySLADatas.reduce(reducer), xCoord, yCoord);
                ctx.font = "400 18px TanseekModernProArabic";
                ctx.fillStyle = "#798793";
                ctx.fillText(htmlLang.includes("ar")
                      ? "إجمالي الطلبات"
                      : "TOTAL REQUESTS", xCoord, yCoord + 25);
              },
            },
          ]);
          // By Category
          const byRequestType = result.by_request_type;

          var byRequestTypeLabels = _.map(byRequestType, function (item) {
            return item[0].charAt(0).toUpperCase() + item[0].slice(1);
          });
          var byRequestTypeData = _.map(byRequestType, function (item) {
            return item[1];
          });
          var categoryData = {
            label: "",
            labels: byRequestTypeLabels,
            datasets: [
              {
                data: byRequestTypeData,
                borderRadius: 4,
                borderSkipped: "bottom",
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
                    ["#A7D7CE", "#E9F4F1"],
                    ["#5B508D", "#CEC9DB"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    labels,
                    ctx,
                    chartArea
                  );
                },
                borderWidth: 0,
              },
            ],
          };
          self.chartFunc("bar", ctxBYGategory, categoryData, barChartOptions);

          // By Client
          var byClient = result.by_partner;
          var byClientLabels = _.map(byClient, function (item) {
            return item[0];
          });
          var byclientData = _.map(byClient, function (item) {
            return item[1];
          });
          var clientData = {
            label: "",
            labels: byClientLabels,
            datasets: [
              {
                data: byclientData,
                borderRadius: 4,
                borderSkipped: "bottom",
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
                    ["#A7D7CE", "#E9F4F1"],
                    ["#5B508D", "#CEC9DB"],
                  ];
                  return Utils.generateGradients(
                    listOfColor,
                    labels,
                    ctx,
                    chartArea
                  );
                },
                borderWidth: 0,
              },
            ],
          };
          self.chartFunc("bar", ctxByClient, clientData, barChartOptions);

          // By create date
          var byCreateDateData = result.by_creation_date;
          const createDate = _.map(byCreateDateData, function (item) {
            return item.x;
          });
          var creationDAteData = {
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
          self.chartFunc("scatter", ctxByCreationDate, creationDAteData, {
            responsive: true,
            plugins: {
              legend: {
                display: false,
              },
              tooltip: {
                rtl: htmlLang.includes("ar") ? true : false,
                textDirection: htmlLang.includes("ar") ? 'rtl' : 'ltr',
              },
            },
            scales: {
              x: {
                type: "category",
                position: "bottom",
                labels: createDate,
              },
              y: {
                position:  htmlLang.includes("ar") ?'right': 'left',
              }
            },
            animation: true,
          });
        });
    },
  });
});

odoo.define("thiqah.inquiries.details.requests", function (require) {
  "use strict";
  var session = require("web.session");

  // this is called even we don't need to fetch ==> need to fix this
  if (session.user_id) {
    $(document).ready(function () {
      var inquiries_details;
      $.ajax({
        async: false,
        type: "GET",
        url: "/get/inquiries/details",
        success: function (data) {
          inquiries_details = data;
        },
        error: function (data) {},
      });

      var these_data = jQuery.parseJSON(inquiries_details);
      var htmlLang = $("html").attr("lang");
      // Gathering
      var inquiries_details_data = these_data["inquiries_details_data"];
      $.extend($.fn.dataTable.defaults, {
        autoWidth: true,
        dom: '<"datatable-header"fl><"datatable-scroll"t><"datatable-footer"ip>',
        language: {
          search:
            '<div class="form-control-feedback form-control-feedback-end flex-fill"><div class="form-control-feedback-icon"><i class="fa fa-search opacity-50"></i></div>_INPUT_</div>',
          searchPlaceholder: htmlLang.includes("ar") ? "بحث..." : "Search...",
          lengthMenu: `<span class="body2" style="color: #798793 !important">Enties Shown:</span> _MENU_`,
          paginate: {
            first: "First",
            last: "Last",
            next: "Next",
            previous: "Previous",
          },
        },
      });
      var inquiries_details = $("#inquiries_details_table").DataTable({
        language: htmlLang.includes("ar")
          ? {
              sLengthMenu: "أظهر _MENU_ مدخلات",
              sZeroRecords: "لم يعثر على أية سجلات",
              sInfo: "إظهار _START_ إلى _END_ من أصل _TOTAL_ مدخل",
              sInfoEmpty: "يعرض 0 إلى 0 من أصل 0 سجل",
              sInfoPostFix: "",
              oPaginate: {
                sFirst: "الأول",
                sPrevious: "السابق",
                sNext: "التالي",
                sLast: "الأخير",
              },
            }
          : "",
        responsive: true,
        data: inquiries_details_data,
        columns: [
          { title: htmlLang.includes("ar") ? "الرقم التسلسلي" : "Sequence" },
          { title: htmlLang.includes("ar") ? "الوصف" : "Description" },
          { title: htmlLang.includes("ar") ? "الإدارة" : "Department" },
        ],
      });
    });
  }
});
