/** @odoo-module **/

import { RPCErrorDialog } from '@web/core/errors/error_dialogs';

import core from 'web.core';
import Dialog from 'web.Dialog';
import utils from 'web.utils';
import session  from 'web.session';
import { patch } from 'web.utils';
var _t = core._t;
import { odooExceptionTitleMap } from "@web/core/errors/error_dialogs";
patch(RPCErrorDialog.prototype, 'web/static/src/core/errors/error_dialogs.js', {
	
    inferTitle() {
        // If the server provides an exception name that we have in a registry.
        if (this.props.exceptionName && odooExceptionTitleMap.has(this.props.exceptionName)) {
            this.title = odooExceptionTitleMap.get(this.props.exceptionName).toString();
            return;
        }
        // Fall back to a name based on the error type.
        if (!this.props.type) return;
        switch (this.props.type) {
            case "server":
                this.title = this.env._t("CXP Server Error");
                break;
            case "script":
                this.title = this.env._t("CXP Client Error");
                break;
            case "network":
                this.title = this.env._t("CXP Network Error");
                break;
        }
    }


});
