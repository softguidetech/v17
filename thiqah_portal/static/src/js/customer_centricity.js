odoo.define("thiqah.CustomerCentricity.dashboard", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");
  var Utils = require("thiqah.Utils");
  publicWidget.registry.CustomerCentricity = publicWidget.Widget.extend({
    selector: "#customer_centricity_class",
    jsLibs: ["/thiqah_base/static/libs/Chart.js"],
    /**
     * @override
     */
    start: function () {
      this.getDashboardData();
      return this._super.apply(this, arguments);
    },

    chartFunc: function (type, ctx, data, options, plugins) {
      var myDoughnutChart = new Chart(ctx, {
        type: type,
        data: data,
        options: options,
        plugins,
      });
    },

    getDashboardData: function () {
      var ctxCsat = document.getElementById("csat-chart").getContext("2d");
      var ctxNps = document.getElementById("nps-chart").getContext("2d");
      var ctxCes = document.getElementById("ces-chart").getContext("2d");
      var ctxOpportunities = document
        .getElementById("opportunities-chart")
        .getContext("2d");
      var ctxAnalysis = document.getElementById("escalation").getContext("2d");
      var ctxEndUsers = document.getElementById("end_users").getContext("2d");
      var ctxBusinessPa = document
        .getElementById("business-pa")
        .getContext("2d");
      var ctxMarketingCrm = document
        .getElementById("marketing-crm")
        .getContext("2d");
      var ctxProductDebt = document
        .getElementById("product-debt")
        .getContext("2d");
      var ctxEmp = document.getElementById("empo").getContext("2d");

      var gradientFillNps = ctxNps.createLinearGradient(1, 150, 0, 0);
      gradientFillNps.addColorStop(0, "#3C85C1");
      gradientFillNps.addColorStop(1, "#5B508D");

      var gradientFillPerformance = ctxCsat.createLinearGradient(1, 150, 0, 0);
      gradientFillPerformance.addColorStop(0, "#5B508D");
      gradientFillPerformance.addColorStop(1, "#0A0A0A");

      var gradientFillCes = ctxCes.createLinearGradient(1, 120, 0, 0);
      gradientFillCes.addColorStop(0, "#A7D7CE");
      gradientFillCes.addColorStop(1, "#E9F4F1");

      var gradientFillAnalysisLight = ctxOpportunities.createLinearGradient(
        1,
        150,
        0,
        0
      );
      gradientFillAnalysisLight.addColorStop(0, "rgba(101, 74, 130, .1)");
      gradientFillAnalysisLight.addColorStop(1, "rgba(101, 74, 130, .2)");

      var gradientFillAnalysisDark = ctxOpportunities.createLinearGradient(
        1,
        150,
        0,
        0
      );
      gradientFillAnalysisDark.addColorStop(0, "rgba(101, 74, 130, .6)");
      gradientFillAnalysisDark.addColorStop(1, "rgba(101, 74, 130, .8)");

      var optionsAction = {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              display: false,
            },
          },
          y: {
            grid: {
              display: false,
            },
            beginAtZero: true,
            ticks: {
              display: false,
            },
          },
        },
        elements: {
          point: false,
        },
      };

      var endUsersOptions = {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
        },
      };

      var analysisOptions = {
        plugins: {
          legend: {
            display: false,
          },
        },
      };
      var opportunitiesOptions = {
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
            display: false,
            ticks: {
              // beginAtZero: true,
              display: false,
            },
          },
        },
      };

      var endUsersData = {
        label: "",
        labels: ["Total Incidents", "SLA Compliance", "Breach"],
        datasets: [
          {
            data: [200, 350, 495, 460, 390, 350, 350],
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

      var businessPaData = {
        label: "",
        labels: ["Within Schedule", "No Progress", "Behind Schedule"],
        datasets: [
          {
            data: [1, 6, 3],
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

      var productDebtData = {
        label: "",
        labels: ["Debt Rate", "Baseline"],
        datasets: [
          {
            data: [2, 4],
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

      var empoData = {
        label: "",
        labels: ["Within Schedule ", "Behind Schedule"],
        datasets: [
          {
            data: [7, 3],
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

      var marketingCrmData = {
        label: "",
        labels: ["Within Schedule", "No Progress", "Behind Schedule"],
        datasets: [
          {
            data: [2, 4, 7],
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

      var csatData = {
        label: "",
        labels: ["1", "2", "3", "4", "5", "6", "7"],
        datasets: [
          {
            borderColor: ["0A0A0A"],
            data: [420, 320, 300, 460, 460, 350, 350],
            backgroundColor: gradientFillPerformance,
            fill: true,
            pointRadius: 0,
          },
        ],
      };

      var npsData = {
        label: "",
        labels: ["1", "4", "3", "4", "5", "6", "7"],
        datasets: [
          {
            borderColor: ["#3C85C1"],
            data: [520, 420, 360, 460, 460, 350, 350],
            backgroundColor: gradientFillNps,
            fill: true,
            pointRadius: 0,
          },
        ],
      };

      var cesData = {
        label: "",
        labels: ["1", "2", "3", "4", "5", "6", "7"],
        datasets: [
          {
            borderColor: ["#A7D7CE"],
            data: [120, 220, 160, 460, 460, 350, 350],
            backgroundColor: gradientFillCes,
            fill: true,
            pointRadius: 0,
          },
        ],
      };

      var analysisData = {
        label: "",
        labels: ["Total", "Resolved", "Ongoing"],
        datasets: [
          {
            data: [1, 3, 2],
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
      var opportunitiesLabels = ["Won", "Lost", "Pipeline"];
      var opportunitiesDatas = [13, 18, 2];
      var opportunitiesData = {
        label: "",
        labels: _.map(opportunitiesLabels, function (item, index) {
          return `${item} (${opportunitiesDatas[index]}%)`;
        }),
        datasets: [
          {
            data: opportunitiesDatas,
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

      this.chartFunc("line", ctxCsat, csatData, optionsAction);
      this.chartFunc("line", ctxNps, npsData, optionsAction);
      this.chartFunc("line", ctxCes, cesData, optionsAction);
      this.chartFunc(
        "doughnut",
        ctxOpportunities,
        opportunitiesData,
        opportunitiesOptions,
        [
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
              ctx.fillText(123, xCoord, yCoord);
              ctx.font = "400 18px TanseekModernProArabic";
              ctx.fillStyle = "#798793";
              ctx.fillText("TOTAL REQUESTS", xCoord, yCoord + 25);
            },
          },
        ]
      );
      this.chartFunc("bar", ctxAnalysis, analysisData, analysisOptions);
      this.chartFunc("bar", ctxEndUsers, endUsersData, endUsersOptions);
      this.chartFunc("bar", ctxBusinessPa, businessPaData, endUsersOptions);
      this.chartFunc("bar", ctxMarketingCrm, marketingCrmData, endUsersOptions);
      this.chartFunc("bar", ctxProductDebt, productDebtData, endUsersOptions);
      this.chartFunc("bar", ctxEmp, empoData, endUsersOptions);
    },
  });
});

odoo.define(
  "thiqah.CustomerCentricityFilterByProject.modal",
  function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.CustomerCentricityFilterByProject =
      publicWidget.Widget.extend({
        selector: "#by_client_modal",
        events: {
          "click .select_client a": "_GetProjects",
          "click .back-top": "_backToclients",
          "keyup .clients_input": "_filterClients",
        },
        start: function (parent) {
          this.$el.find(".projects-list").hide();
          return this._super.apply(this, arguments);
        },

        _GetProjects: function (e) {
          this.$el.find(".clients-list").hide();
          this.$el.find(".projects-list").show();
          $(".back-top").toggleClass("d-flex");
        },
        _backToclients: function () {
          this.$el.find(".clients-list").show();
          this.$el.find(".projects-list").hide();
          $(".back-top").toggleClass("d-flex");
        },
        _filterClients: function (e) {
          var value = $(e.target).val().toLowerCase();
          $(".select_client a span").filter(function () {
            $(this.parentElement).toggle(
              $(this).text().toLowerCase().indexOf(value) > -1
            );
          });
        },
      });
  }
);
