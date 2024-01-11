/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(WebClient.prototype, "thiqah_dynamic_web_theme.WebClient", {
    setup() {
        this._super.apply(this, arguments);
        const system_name = session.user_companies.allowed_companies[1]['company_title'] || 'Thiqah';
        this.title.setParts({ zopenerp: system_name });
       
    }
});



