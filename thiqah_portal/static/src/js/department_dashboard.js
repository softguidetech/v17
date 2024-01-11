odoo.define("thiqah.department.task.dashboard", function (require) {
  "use strict";

  var session = require("web.session");
  var htmlLang = $("html").attr("lang");
  function format(d) {
    // `d` is the original data object for the row
    return (
      '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
      "<tr>" +
      "<td>Actions</td>" +
      '<td><a href="/my/requests/' +
      d[9] +
      '?mode=change_status" class="fa fa-eye"></a></td>' +
      "</tr>" +
      "<tr>" +
      "<td>Current Step:</td>" +
      "<td>" +
      d[5] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Request status:</td>" +
      "<td>" +
      d[4] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Last Step:</td>" +
      "<td>" +
      d[6] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Last Step created By:</td>" +
      "<td>" +
      d[7] +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>Last Step creation Date Time:</td>" +
      "<td>" +
      d[8] +
      "</td>" +
      "</tr>" +
      "</table>"
    );
  }

  if (session.user_id) {
    $(document).ready(function () {
      var task_department_data;

      $.ajax({
        async: false,
        type: "GET",
        url: "/tasks/api/mydata",
        success: function (data) {
          task_department_data = data;
        },
        error: function (data) {
          console.log("error");
        },
      });

      var these_data = jQuery.parseJSON(task_department_data);

      // Gathering
      var requiring_data = these_data["requiring_actions"];
      var draft_data = these_data["draft_requests"];
      // Fill count(s)
      $("#requiring_actions_count").text(requiring_data.length);
      $("#draft_requests_count").text(draft_data.length);
      var requiring_table = $("#requiring_actions_table").DataTable({
        responsive: true,
        data: requiring_data,
        language: htmlLang.includes("ar")?{
          "sZeroRecords": "لم يعثر على أية سجلات",
          "sInfoEmpty": "يعرض 0 إلى 0 من أصل 0 سجل",
          "sEmptyTable": "لا توجد بيانات متاحة في الجدول",
          "sInfoPostFix": "",
          "oPaginate": {
              "sFirst": "الأول",
              "sPrevious": "السابق",
              "sNext": "التالي",
              "sLast": "الأخير"
          }}:'',
        columns: [
          { title: htmlLang.includes("ar")?"الكود ذو الصلة":"Related Code" },
          { title: htmlLang.includes("ar")?"نوع الطلب":"Service Catalog" },
          { title: htmlLang.includes("ar")?"الفئة":"Type" },
          {
            className: "dt-control",
            ordering: false,
            data: "",
            defaultContent: "",
          },
        ],
        columnDefs: [
          {
            targets: [3], // column index (start from 0)
            orderable: false, // set orderable false for selected columns
          },
        ],
      });

      // Add event listener for opening and closing details | Delegation
      $("#requiring_actions_table tbody").on(
        "click",
        "td.dt-control",
        function () {
          var tr = $(this).closest("tr");
          var row = requiring_table.row(tr);
          tr.toggleClass("tr-collapse");
          if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass("shown");
          } else {
            // Open this row
            row.child(format(row.data())).show();
            tr.addClass("shown");
          }
        }
      );

      var table = $("#requests_task_department").DataTable({
        responsive: true,
        data: these_data["service_requests_task"],
        ordering: false,
        language: htmlLang.includes("ar")?{
          "sZeroRecords": "لم يعثر على أية سجلات",
          "sInfoEmpty": "يعرض 0 إلى 0 من أصل 0 سجل",
          "sEmptyTable": "لا توجد بيانات متاحة في الجدول",
          "sInfoPostFix": "",
          "oPaginate": {
              "sFirst": "الأول",
              "sPrevious": "السابق",
              "sNext": "التالي",
              "sLast": "الأخير"
          }}:'',
        columns: [
          { title: htmlLang.includes("ar")?"المشروع":"Project" },
          { title: htmlLang.includes("ar")?"الرقم التسلسلي":"Sequence" },
          { title: htmlLang.includes("ar")?"العميل":"Client" },
          { title: htmlLang.includes("ar")?"مقدم الطلب":"Requester" },
          { title: htmlLang.includes("ar")?"إس إل إي":"SLA" },
          { title: htmlLang.includes("ar")?"مستوى الخدمة":"SLA Indicator" },
          { title: htmlLang.includes("ar")?"الإدارة":"Department" },
          { title: htmlLang.includes("ar")?"نوع الطلب":"Service Catalog" },
        ],
      });

      var draft_requests = $("#draft_requests_table").DataTable({
        responsive: true,
        data: draft_data,
        language: htmlLang.includes("ar")?{
          "sZeroRecords": "لم يعثر على أية سجلات",
          "sInfoEmpty": "يعرض 0 إلى 0 من أصل 0 سجل",
          "sEmptyTable": "لا توجد بيانات متاحة في الجدول",
          "sInfoPostFix": "",
          "oPaginate": {
              "sFirst": "الأول",
              "sPrevious": "السابق",
              "sNext": "التالي",
              "sLast": "الأخير"
          }}:'',
        columns: [
          { title: htmlLang.includes("ar")?"المشروع":"Project" },
          { title: htmlLang.includes("ar")?"معرف الطلب":"Request ID" },
          { title: htmlLang.includes("ar")?"مقدم الطلب":"Requester" },
          { title: htmlLang.includes("ar")?"إس ال اي":"SLA" },
          { title: htmlLang.includes("ar")? "مستوى الخدمة":"SLA Indicator" },
          { title: htmlLang.includes("ar")?"الإدارة":"Department" },
          { title: htmlLang.includes("ar")?"نوع الطلب":"Service Catalog" },
          { title: htmlLang.includes("ar")?"الحالة":"Status" },
          { title: htmlLang.includes("ar")?"الإجراءات":"Actions" },
        ],
      });
    });
  }
});
