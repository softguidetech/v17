odoo.define("thiqah_portal.chatter", function (require) {
  "use strict";

  var portalChatter = require("portal.chatter");
  var portalcomposer = require("portal.composer");
  var time = require("web.time");
  const {Markup} = require('web.utils');
  var session = require("web.session");

  var PortalChatter = portalChatter.PortalChatter;
  var PortalComposer = portalcomposer.PortalComposer;

  var htmlLang = $("html").attr("lang");
  /**
   * PortalComposer
   *
   * Extends Frontend Chatter to handle rating
   */
  PortalComposer.include({
    xmlDependencies: (PortalChatter.prototype.xmlDependencies || []).concat([
      "/thiqah_portal/static/src/xml/chatter.xml",
    ]),
    /**
     * @override
     */
    init: function () {
      this.user = "";
      this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    start: function () {
      var self = this;
      return this._super.apply(this, arguments).then(function () {
        self
          ._rpc({
            model: "res.users",
            method: "search_read",
            kwargs: {
              domain: [["id", "=", session.user_id]],
              fields: ["name"],
            },
          })
          .then(function (res) {
            $($(self.$attachmentButton).find("span")).text(
              htmlLang.includes("ar") ? "أرفق ملف" : "Attach file"
            );
            $(self.$sendButton).text(htmlLang.includes("ar") ? "أرسل" : "Send");
            $(self.$inputTextarea).attr(
              "placeholder",
              htmlLang.includes("ar")
                ? "اكتب رسالتك هنا..."
                : "Type your message here..."
            );

            self.user = res[0].name;
            self.$el.find(".username").text(self.user);
          });
      });
    },
    /**
     * @override
     */
    _onSubmitButtonClick: function (ev) {
      ev.preventDefault();
      if (!this.$inputTextarea.val().trim() && !this.attachments.length) {
        this.$inputTextarea.addClass("border-danger");
        const error = htmlLang.includes("ar")
          ? "بعض الحقول مطلوبة. يرجى التأكد من كتابة رسالة أو إرفاق ملف."
          : "Some fields are required. Please make sure to write a message or attach a document";
        this.$(".o_portal_chatter_composer_error")
          .text(error)
          .removeClass("d-none");
        return Promise.reject();
      } else {
        return this._chatterPostMessage(
          ev.currentTarget.getAttribute("data-action")
        );
      }
    },
  });

  /**
   * PortalChatter
   *
   * Extends Frontend Chatter to handle rating
   */
  PortalChatter.include({
    xmlDependencies: (PortalChatter.prototype.xmlDependencies || []).concat([
      "/thiqah_portal/static/src/xml/chatter.xml",
    ]),
    init: function () {
      this._super.apply(this, arguments);
      this.currentLang = htmlLang.split("-")[0];
    },
    /**
     * @override
     */
    preprocessMessages(messages) {
      this._super.apply(this, arguments);
      _.each(messages, function (m) {
        m["published_date_str"] = _.str.sprintf(
          moment(time.str_to_datetime(m.date)).format("D MMM YYYY")
        );
        m["published_time_str"] = _.str.sprintf(
          moment(time.str_to_datetime(m.date)).format("h:mm A")
        );
      });
      return messages;
    },
  });
});
