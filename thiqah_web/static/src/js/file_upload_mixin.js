/** @odoo-module **/


import ProgressBarMixin from '@web/legacy/js/views/file_upload_mixin';

const session = require('web.session');
const { _t, qweb } = require('web.core');
import utils from 'web.utils';



ProgressBarMixin._uploadFiles = async function(files, params={})  {
			 if (!files || !files.length) { return; }
 
			for (const file of files) 
				{
				this.max_upload_size = session.max_file_upload_size || 128 * 1024 * 1024;
				
				var suported_typ= session.binary_supported_types.split(',');
				var binary_supported_types_list = [];
				suported_typ.forEach(function (type) {
					binary_supported_types_list.push(type);
				});
				
				this.binary_supported_types = binary_supported_types_list || '*';

				// if (file.size > this.max_upload_size) {
				// 	var msg = _t("The selected file exceed the maximum file size of %s.");
				// 		this.displayNotification({
				// 			type: 'danger',
				// 			title: _t("File upload"),
				// 			message: _.str.sprintf(msg, utils.human_size(this.max_upload_size)),
				// 		});
				// 		return false;
				// }

				if(this.binary_supported_types.indexOf(file.type) !== -1 || this.binary_supported_types == '*'){
						console.log(' type exists')
					} 
				else
					{
					var msg = _t("The selected type file is not supported only theese types %s are supported.");
					this.displayNotification({
						type: 'danger',
						title: _t("File upload Type"),
						message: _.str.sprintf(msg, this.binary_supported_types),
					});
					return false;
					}
				
		   
			}
            
			//code odoo
            await new Promise(resolve => {
				const xhr = this._createXhr();
				xhr.open('POST', this._getFileUploadRoute());
				const fileUploadData = this._makeFileUpload(Object.assign({ files, xhr }, params));
				const { fileUploadId, formData } = fileUploadData;
				this._fileUploads[fileUploadId] = fileUploadData;
				xhr.upload.addEventListener("progress", ev => {
					this._updateFileUploadProgress(fileUploadId, ev);
				});
				const progressPromise = this._onBeforeUpload();
				xhr.onload = async () => {
					await progressPromise;
					resolve();
					this._onUploadLoad({ fileUploadId, xhr });
				};
				xhr.onerror = async () => {
					await progressPromise;
					resolve();
					this._onUploadError({ fileUploadId, xhr });
				};
				xhr.send(formData);
			});

    
};


