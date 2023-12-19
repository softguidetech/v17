odoo.define("thiqah_portal.auth_signup.signup", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.SignUpFormCustom = publicWidget.Widget.extend({
    selector: ".oe_reset_password_form",
    events: {
      'change input[name="password"]': "_onChangePassword",
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onChangePassword: function (e) {
      let regex =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@.#$!%*?&])[A-Za-z\d@.#$!%*?&]{8,20}$/;
        if(!regex.test($(e.target).val())){
            $(".password-check").removeClass("d-none")
        }else{
            $(".password-check").addClass("d-none")
        }
    },
  });
});
