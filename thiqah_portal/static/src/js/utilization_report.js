odoo.define("thiqah.utilization.report.dashboard", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var ajax = require("web.ajax");
  var Utils = require("thiqah.Utils");

  var htmlLang = $("html").attr("lang");

  publicWidget.registry.UtilizationReportDahboard = publicWidget.Widget.extend({
    selector: ".utilization_report_dashboard",
    jsLibs: ["/thiqah_base/static/libs/Chart.js"],
    events: {
      "change .ur_filter": "_onChangeFilter",
    },

    /**
     * @override
     */
    start: function () {
      let category = $('select[name="filter_by_category"]').val();
      let user = $('select[name="filter_by_user"]').val();
      let period = $('select[name="filter_by_period"]').val();
      let params = {
        filter_by_category: category,
        filter_by_user: user,
        filter_by_period: period,
      };
      this.getDashboardData(params);
      this.$(".selectpicker").selectpicker();
      return this._super.apply(this, arguments);
    },

    _onChangeFilter: function () {
      let category = $('select[name="filter_by_category"]').val();
      let user = $('select[name="filter_by_user"]').val();
      let period = $('select[name="filter_by_period"]').val();
      window.location = `/utilization/dashboard?filter_by_category=${category}&filter_by_user=${user}&filter_by_period=${period}`;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    getDashboardData: function (params) {
      ajax
        .jsonRpc("/utilization/dashboard/fetch_data", "call", params)
        .then(function (result) {
          //Lead Generation Chart: By Department
          var leadByDepartmentLabel = result.lead_by_department_labels;
          var leadByDepartmentValue = result.lead_by_department_values;
          const leadByDepartmentElement =
            document.getElementById("lg_by_department");
          var sumLeadByDepartment = leadByDepartmentValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let leadByDepartmentLabelFormatted = [];
          for (let i = 0; i < leadByDepartmentValue.length; i++) {
            leadByDepartmentLabelFormatted.push(
              leadByDepartmentLabel[i] +
                " " +
                "(" +
                leadByDepartmentValue[i] +
                ")"
            );
          }
          const leadByDepartmentData = {
            labels: leadByDepartmentLabel,
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
                    ["#00BCB6", "#A7D7CE"],
                    ["#51BBE5", "#A7D7CE"],
                    ["#51BBE5", "#3C85C1"],
                    ["#3C85C1", "#CFDAED"],
                    ["#5B508D", "#CEC9DB"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    leadByDepartmentLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: leadByDepartmentValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const leadByDepartmentConfig = {
            type: "doughnut",
            data: leadByDepartmentData,
            options: {
              maintainAspectRatio: false,
              cutout: "70%",
              responsive: true,
              plugins: {
                tooltip: {
                  rtl: htmlLang.includes("ar") ? true : false,
                },
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
                  ctx.fillText(sumLeadByDepartment, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar") ? "مجموع الفرص" : "TOTAL LEADS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (leadByDepartmentElement != null) {
            new Chart(leadByDepartmentElement, leadByDepartmentConfig);
          }

          //Lead Generation Chart: By Users
          var leadByUserLabel = result.lead_by_user_labels;
          var leadByUserValue = result.lead_by_user_values;
          const leadByUserElement = document.getElementById("lg_by_user");
          var sumLeadByUser = leadByUserValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let leadByUserLabelFormatted = [];
          for (let i = 0; i < leadByUserValue.length; i++) {
            leadByUserLabelFormatted.push(
              leadByUserLabel[i] + " " + "(" + leadByUserValue[i] + ")"
            );
          }
          const leadByUserData = {
            labels: leadByUserLabelFormatted,
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
                    ["#3C85C1", "#4478B4"],
                    ["#4478B4", "#7E84C9"],
                    ["#7E84C9", "#5B508D"],
                    ["#5B508D", "#2A224C"],
                    ["#2A224C", "#0A0A0A"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    leadByUserLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: leadByUserValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const leadByUserConfig = {
            type: "doughnut",
            data: leadByUserData,
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
                  ctx.fillText(sumLeadByUser, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar") ? "مجموع الفرص" : "TOTAL LEADS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (leadByUserElement != null) {
            new Chart(leadByUserElement, leadByUserConfig);
          }

          //Service Request Chart: By Department
          var srequestByDepartmentLabel = result.srequest_by_department_labels;
          var srequestByDepartmentValue = result.srequest_by_department_values;
          const srequestByDepartmentElement =
            document.getElementById("sreq_by_department");
          var sumSrequestByDepartment = srequestByDepartmentValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let srequestByDepartmentLabelFormatted = [];
          for (let i = 0; i < srequestByDepartmentValue.length; i++) {
            srequestByDepartmentLabelFormatted.push(
              srequestByDepartmentLabel[i] +
                " " +
                "(" +
                srequestByDepartmentValue[i] +
                ")"
            );
          }

          const srequestByDepartmentData = {
            labels: srequestByDepartmentLabelFormatted,
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
                    ["#CFDAED", "#3C85C1"],
                    ["#51BBE5", "#3C85C1"],
                    ["#51BBE5", "#A7D7CE"],
                    ["#00BCB6", "#A7D7CE"],
                    ["#00BCB6", "#A7D7CE"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    srequestByDepartmentLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: srequestByDepartmentValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const srequestByDepartmentConfig = {
            type: "doughnut",
            data: srequestByDepartmentData,
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
                  ctx.fillText(sumSrequestByDepartment, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (srequestByDepartmentElement != null) {
            new Chart(srequestByDepartmentElement, srequestByDepartmentConfig);
          }

          // Service Request Chart: By Users
          var srequestByUserLabel = result.srequest_by_user_labels;
          var srequestByUserValue = result.srequest_by_user_values;
          const srequestByUserElement = document.getElementById("sreq_by_user");
          var sumSrequestByUser = srequestByUserValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let srequestByUserLabelFormatted = [];
          for (let i = 0; i < srequestByUserValue.length; i++) {
            srequestByUserLabelFormatted.push(
              srequestByUserLabel[i] + " " + "(" + srequestByUserValue[i] + ")"
            );
          }
          const srequestByUserData = {
            labels: srequestByUserLabelFormatted,
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
                    ["#2A224C", "#0A0A0A"],
                    ["#5B508D", "#2A224C"],
                    ["#7E84C9", "#5B508D"],
                    ["#4478B4", "#7E84C9"],
                    ["#3C85C1", "#4478B4"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    srequestByUserLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                borderRadius: 4,
                borderSkipped: "bottom",
                data: srequestByUserValue,
              },
            ],
          };

          const srequestByUserConfig = {
            type: "doughnut",
            data: srequestByUserData,
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
                  ctx.fillText(sumSrequestByUser, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (srequestByUserElement != null) {
            new Chart(srequestByUserElement, srequestByUserConfig);
          }

          //Inquiry Request Chart: By Department
          var irequestByDepartmentLabel = result.irequest_by_department_labels;
          var irequestByDepartmentValue = result.irequest_by_department_values;
          const irequestByDepartmentElement =
            document.getElementById("ireq_by_department");
          var sumirequestByDepartment = irequestByDepartmentValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let irequestByDepartmentLabelFormatted = [];
          for (let i = 0; i < irequestByDepartmentValue.length; i++) {
            irequestByDepartmentLabelFormatted.push(
              irequestByDepartmentLabel[i] +
                " " +
                "(" +
                irequestByDepartmentValue[i] +
                ")"
            );
          }

          const irequestByDepartmentData = {
            labels: irequestByDepartmentLabelFormatted,
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
                    ["#00BCB6", "#A7D7CE"],
                    ["#51BBE5", "#A7D7CE"],
                    ["#51BBE5", "#3C85C1"],
                    ["#3C85C1", "#CFDAED"],
                    ["#5B508D", "#CEC9DB"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    irequestByDepartmentLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                borderRadius: 4,
                borderSkipped: "bottom",
                data: irequestByDepartmentValue,
              },
            ],
          };

          const irequestByDepartmentConfig = {
            type: "doughnut",
            data: irequestByDepartmentData,
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
                  ctx.fillText(sumirequestByDepartment, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع الإستفسارات"
                      : "TOTAL INQUIRIES",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (irequestByDepartmentElement != null) {
            new Chart(irequestByDepartmentElement, irequestByDepartmentConfig);
          }

          //Inquiry Request Chart: By Users
          var irequestByUserLabel = result.irequest_by_user_labels;
          var irequestByUserValue = result.irequest_by_user_values;
          const irequestByUserElement = document.getElementById("ireq_by_user");
          var sumIrequestByUser = irequestByUserValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let irequestByUserLabelFormatted = [];
          for (let i = 0; i < irequestByUserValue.length; i++) {
            irequestByUserLabelFormatted.push(
              irequestByUserLabel[i] + " " + "(" + irequestByUserValue[i] + ")"
            );
          }
          const irequestByUserData = {
            labels: irequestByUserLabelFormatted,
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
                    ["#3C85C1", "#4478B4"],
                    ["#4478B4", "#7E84C9"],
                    ["#7E84C9", "#5B508D"],
                    ["#5B508D", "#2A224C"],
                    ["#2A224C", "#0A0A0A"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    irequestByUserLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: irequestByUserValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const irequestByUserConfig = {
            type: "doughnut",
            data: irequestByUserData,
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
                  ctx.fillText(sumIrequestByUser, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع الإستفسارات"
                      : "TOTAL INQUIRIES",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (irequestByUserElement != null) {
            new Chart(irequestByUserElement, irequestByUserConfig);
          }

          //Freelance Request Chart: By Department
          var frequestByDepartmentLabel = result.frequest_by_department_labels;
          var frequestByDepartmentValue = result.frequest_by_department_values;
          const frequestByDepartmentElement =
            document.getElementById("freq_by_department");
          var sumFrequestByDepartment = frequestByDepartmentValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let frequestByDepartmentLabelFormatted = [];
          for (let i = 0; i < frequestByDepartmentValue.length; i++) {
            frequestByDepartmentLabelFormatted.push(
              frequestByDepartmentLabel[i] +
                " " +
                "(" +
                frequestByDepartmentValue[i] +
                ")"
            );
          }

          const frequestByDepartmentData = {
            labels: frequestByDepartmentLabelFormatted,
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
                    ["#CFDAED", "#3C85C1"],
                    ["#51BBE5", "#3C85C1"],
                    ["#51BBE5", "#A7D7CE"],
                    ["#00BCB6", "#A7D7CE"],
                    ["#00BCB6", "#A7D7CE"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    frequestByDepartmentLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: frequestByDepartmentValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const frequestByDepartmentConfig = {
            type: "doughnut",
            data: frequestByDepartmentData,
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
                  ctx.fillText(sumFrequestByDepartment, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (frequestByDepartmentElement != null) {
            new Chart(frequestByDepartmentElement, frequestByDepartmentConfig);
          }

          // Freelance Request Chart: By Users
          var frequestByUserLabel = result.frequest_by_user_labels;
          var frequestByUserValue = result.frequest_by_user_values;
          const frequestByUserElement = document.getElementById("freq_by_user");
          var sumFrequestByUser = frequestByUserValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let frequestByUserLabelFormatted = [];
          for (let i = 0; i < frequestByUserValue.length; i++) {
            frequestByUserLabelFormatted.push(
              frequestByUserLabel[i] + " " + "(" + frequestByUserValue[i] + ")"
            );
          }
          const frequestByUserData = {
            labels: frequestByUserLabelFormatted,
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
                    ["#2A224C", "#0A0A0A"],
                    ["#5B508D", "#2A224C"],
                    ["#7E84C9", "#5B508D"],
                    ["#4478B4", "#7E84C9"],
                    ["#3C85C1", "#4478B4"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    frequestByUserLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: frequestByUserValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const frequestByUserConfig = {
            type: "doughnut",
            data: frequestByUserData,
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
                  ctx.fillText(sumFrequestByUser, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع الطلبات"
                      : "TOTAL REQUESTS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (frequestByUserElement != null) {
            new Chart(frequestByUserElement, frequestByUserConfig);
          }

          //Loggins By Department
          var logginsByDepartmentLabel = result.loggins_by_department_labels;
          var logginsByDepartmentValue = result.loggins_by_department_values;
          const logginsByDepartmentElement = document.getElementById(
            "loggins_by_department"
          );
          var sumLogginsByDepartment = logginsByDepartmentValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let logginsByDepartmentLabelFormatted = [];
          for (let i = 0; i < logginsByDepartmentValue.length; i++) {
            logginsByDepartmentLabelFormatted.push(
              logginsByDepartmentLabel[i] +
                " " +
                "(" +
                logginsByDepartmentValue[i] +
                ")"
            );
          }

          const logginsByDepartmentData = {
            labels: logginsByDepartmentLabelFormatted,
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
                    ["#CFDAED", "#3C85C1"],
                    ["#51BBE5", "#3C85C1"],
                    ["#51BBE5", "#A7D7CE"],
                    ["#00BCB6", "#A7D7CE"],
                    ["#00BCB6", "#A7D7CE"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    logginsByDepartmentLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                data: logginsByDepartmentValue,
                borderRadius: 4,
                borderSkipped: "bottom",
              },
            ],
          };

          const logginsByDepartmentConfig = {
            type: "doughnut",
            data: logginsByDepartmentData,
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
                  ctx.fillText(sumLogginsByDepartment, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع تسجيل الدخول"
                      : "TOTAL LOGGINS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (logginsByDepartmentElement != null) {
            new Chart(logginsByDepartmentElement, logginsByDepartmentConfig);
          }
          // Loggins Requests By User
          var logginsByUserLabel = result.loggins_by_user_labels;
          var logginsByUserValue = result.loggins_by_user_values;
          const logginsByUserElement =
            document.getElementById("loggins_by_user");
          var sumLogginsByUser = logginsByUserValue.reduce(
            (accumulator, currentValue) => {
              return accumulator + currentValue;
            },
            0
          );
          let logginsByUserLabelFormatted = [];
          for (let i = 0; i < logginsByUserValue.length; i++) {
            logginsByUserLabelFormatted.push(
              logginsByUserLabel[i] + " " + "(" + logginsByUserValue[i] + ")"
            );
          }
          const logginsByUserData = {
            labels: logginsByUserLabelFormatted,
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
                    ["#2A224C", "#0A0A0A"],
                    ["#5B508D", "#2A224C"],
                    ["#7E84C9", "#5B508D"],
                    ["#4478B4", "#7E84C9"],
                    ["#3C85C1", "#4478B4"],
                  ];
                  return Utils.generateGradients(
                    colors,
                    logginsByUserLabelFormatted,
                    ctx,
                    chartArea
                  );
                },
                borderRadius: 4,
                borderSkipped: "bottom",
                data: logginsByUserValue,
              },
            ],
          };

          const logginsByUserConfig = {
            type: "doughnut",
            data: logginsByUserData,
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
                  ctx.fillText(sumLogginsByUser, xCoord, yCoord);
                  ctx.font = "400 18px TanseekModernProArabic";
                  ctx.fillStyle = "#798793";
                  ctx.fillText(
                    htmlLang.includes("ar")
                      ? "مجموع تسجيل الدخول"
                      : "TOTAL LOGGINS",
                    xCoord,
                    yCoord + 35
                  );
                },
              },
            ],
          };

          if (logginsByUserElement != null) {
            new Chart(logginsByUserElement, logginsByUserConfig);
          }

          /* Bar Charts */
          var leadByDepartmentBarElement =
            document.getElementById("lead_by_dep_bar");
          if (leadByDepartmentBarElement != null) {
            new Chart(leadByDepartmentBarElement, {
              type: "bar",
              data: leadByDepartmentData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            });
          }
          var leadByUserBarElement = document.getElementById("lead_by_user_bar");
          if (leadByUserBarElement != null) {
            new Chart(leadByUserBarElement, {
              type: "bar",
              data: leadByUserData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            });
          }

          var sreqByDepartmentBarElement = document.getElementById("sreq_by_dep_bar");
          if (sreqByDepartmentBarElement != null) {
            new Chart(sreqByDepartmentBarElement,{
              type: "bar",
              data: srequestByDepartmentData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            })
          }

          var sreqByUserBarElement = document.getElementById("sreq_by_user_bar");
          if (sreqByUserBarElement != null) {
            new Chart(sreqByUserBarElement,{
              type: "bar",
              data: srequestByUserData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            })
          }

          var ireqByDepartmentBarElement = document.getElementById("ireq_by_dep_bar");
          if (ireqByDepartmentBarElement != null) {
            new Chart(ireqByDepartmentBarElement,{
              type: "bar",
              data: irequestByDepartmentData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            })
          }

          var ireqByUserBarElement = document.getElementById("ireq_by_user_bar");
          if (ireqByUserBarElement != null) {
            new Chart(ireqByUserBarElement,{
              type: "bar",
              data: irequestByUserData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            })
          }

          var freqByDepartmentBarElement = document.getElementById("freq_by_dep_bar");
          if (freqByDepartmentBarElement != null) {
            new Chart(freqByDepartmentBarElement,{
              type: "bar",
              data: frequestByDepartmentData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            })
          }

          var freqByUserBarElement = document.getElementById("freq_by_user_bar");
          if (freqByUserBarElement != null) {
            new Chart(freqByUserBarElement,{
              type: "bar",
              data: frequestByUserData,
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
                    position: htmlLang.includes("ar") ? "right" : "left",
                  },
                },
              },
            })
          }
        });
    },
  });
});
