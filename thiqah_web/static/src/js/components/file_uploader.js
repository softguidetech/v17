/** @odoo-module **/

import { FileUploader } from '@mail/components/file_uploader/file_uploader';
console.log('FileUploader');
import core from 'web.core';
import utils from 'web.utils';
import session  from 'web.session';


console.log('max_file_upload_size',session.max_file_upload_size);


import { patch } from 'web.utils';
var _t = core._t;
const components = { FileUploader };

patch(components.FileUploader.prototype, 'mail/static/src/components/file_uploader/file_uploader.js', {


	async uploadFiles(files) {
		var self = this;
		for (const file of files) {
			this.max_upload_size = session.max_file_upload_size || 128 * 1024 * 1024;
			
			var suported_typ= session.binary_supported_types.split(',');
			var binary_supported_types_list = [];
			suported_typ.forEach(function (type) {
				binary_supported_types_list.push(type);
			});
			
			this.binary_supported_types = binary_supported_types_list || '*';
				
		//    if (file.size > this.max_upload_size) {
		// 	   var msg = _t("The selected file exceed the maximum file size of %s.");
		// 	   this.env.services['notification'].notify({
		// 		type: 'danger',
		// 		title: _t("File upload"),
		// 		message: _.str.sprintf(msg, utils.human_size(this.max_upload_size)),
		// 	});
			   
		// 	   return false;
		//    }
		   if(this.binary_supported_types.indexOf(file.type) !== -1 || this.binary_supported_types == '*'){
	            console.log(' type exists')
	        } else{
	        	var msg = _t("The selected type file is not supported only theese types %s are supported.");
				this.env.services['notification'].notify({
						type: 'danger',
						title: _t("File upload Type"),
						message: _.str.sprintf(msg, this.binary_supported_types),
					});
				
				return false;
			}
		   
		   
		}
	
		return this._super(...arguments);
	}



});

