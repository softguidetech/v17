/** @odoo-module **/

import { ComposerSuggestedRecipient } from '@mail/components/composer_suggested_recipient/composer_suggested_recipient';
import { patch } from 'web.utils';
const component = { ComposerSuggestedRecipient };

patch(component.ComposerSuggestedRecipient.prototype, 'mail/static/src/components/composer_suggested_recipient/composer_suggested_recipient.js', {


	_update() {
			if (this._checkboxRef.el && this.suggestedRecipientInfo) {
				this._checkboxRef.el.checked =  ! this.suggestedRecipientInfo.isSelected;
			}
		}



});