$(document).ready(function () {
  $(".profile .icon_wrap").click(function () {
    $(this).parent().toggleClass("active");
    $(".notifications").removeClass("active");
  });

  $(".notifications .icon_wrap").click(function () {
    $(this).parent().toggleClass("active");
    $(".profile").removeClass("active");
  });

  $(".show_all .link").click(function () {
    $(".notifications").removeClass("active");
    $(".popup").show();
  });

  $(".close").click(function () {
    $(".popup").hide();
  });
});

$(document).mouseup(function (ev) {
  if ($(ev.target).closest(".icon_wrap").length === 1) {
    if ($(".notification_dd").css("display") != "none") {
      $(".notification_dd").hide();
    } else {
      $(".notification_dd").show();
    }
  } else if ($(ev.target).closest(".notification_dd").length === 0) {
    $(".notification_dd").hide();
  }
});

odoo.define("notifications.system", function (require) {
  "use strict";
  var session = require("web.session");
  console.log(session.user_id);
  var divsToAppend = "";
  let these_data_response_length = 0;
  let notification_counter = 0;

  if (session.user_id) {
    $(document).ready(function () {
      var messages;

      $.ajax({
        async: false,
        type: "GET",
        url: "/notification/inbox/messages",
        success: function (data) {
          messages = data;
        },
        error: function (data) {
          console.log("error");
        },
      });

      var these_data = jQuery.parseJSON(messages);
      these_data_response_length = these_data.counter;
      notification_counter = these_data.notification_counter;

      if (these_data_response_length) {
        $.each(these_data.response, function (index, item) {
          let check_record_exists = item.model_id_exists;
          let check_request_rejected = item.is_request_rejected;

          let is_open = item.is_open;
          let new_notification = is_open == "False" ? "t-custom-bg-amulet" : "";

          // if(is_open == 'False'){
          //   css_notification= "success";
          // }

          let exists_notification =
            check_record_exists == "True" ? "" : "notification_disabled";
          let notification_disabled_title =
            check_record_exists == "True" ? "" : "notification_disabled_title";
          let disabledDiv = check_record_exists == "True" ? "" : "disabledDiv";
          let requestRejected =
            check_request_rejected == "reject" ? "request_rejected" : "";
          if (check_record_exists == "False") {
            item.url_redirect = "#";
          }

          divsToAppend += `
    <li class="align-items-center d-flex m-2 p-3 rounded-lg t-custom-bg-light-gray" id="${item.message_id}">
      <div class="notify_data flex-grow-1 body3">
          <div class="title ${notification_disabled_title} ${requestRejected}">
              <span>  
                ${item.name} 
              </span>
          </div>
          <div class="sub_title">
              <span>
                ${item.message}
              </span>
          </div>
      </div>
      <div class="btn-circle flex-shrink-0 ml-3 ${new_notification} ${exists_notification} ${disabledDiv}" style="width: 30px;
      height: 30px;">
      <a href="${item.url_redirect}" class="open-notif">
      <img class="rounded-circle with-arrow"
      style="width:12px;height:10px"
      src="/thiqah_portal/static/src/img/right-arrow.svg" />
      </a>
         
      </div>
    </li>
  `;
        });
      } else {
        // divsToAppend = "<div class='no_notification'><span  style='color:#009ABF;'>There is no any notification!<br></br>If you search to change status of a service request. please verify the configuration in dynamic workflow.Or,the action already performed by another user</span></div>"
        divsToAppend = `
    <div class='no_notification'>
    <span  style='color:#009ABF;'>
    There is no any notification!
    </span>
    <br></br>
    <p style='color:#676e9f;'>
    If you search to change status of a service request:
    </p>
    <p style='color:#676e9f;'>
    Please verify the configuration in dynamic workflow. Or,the action already performed by another user.
    </p>
    </div>
  `;
      }

      $(".dropdown-notifications").append(divsToAppend);
      // Adapt the counter with each click.

      // Attach a delegated event handler
      $(".dropdown-notifications").on(
        "click",
        ".notify_status",
        function (event) {
          let uniq_id = $(this).closest("li").attr("id");
          // Ajax Call to update the state of the current message.
          if (uniq_id) {
            $.ajax({
              type: "POST",
              url: "/notification/update/state",
              data: { key: uniq_id },
              success: function () {
                //success code here
              },
              error: function () {
                //error code here
              },
            });
          }
        }
      );

      if (notification_counter > 0) {
        $(".o_NotificationMenu_counter")
          .removeClass("d-none")
          .text(notification_counter);
      }
    });
  }
});
