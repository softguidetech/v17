odoo.define('thiqah_web.AbstractFieldBinary', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var fields = require('web.basic_fields');
var _t = core._t;


fields.AbstractFieldBinary.include({
	
	 on_file_change: function (e) {
	        console.log('on_file_changeon_file_changeon_file_change');
	        var self = this;
	        var file_node = e.target;
	        var file = file_node.files[0];
	        var suported_typ= session.binary_supported_types.split(',');
	        var binary_supported_types_list = [];
			suported_typ.forEach(function (type) {
				binary_supported_types_list.push(type);
			});
			
			
			this.binary_supported_types = binary_supported_types_list || '*';
			//this.accepted_file_extensions = binary_supported_types_list || '*';
		
	        
	        if(this.binary_supported_types.indexOf(file.type) !== -1 || this.binary_supported_types == '*'){
	           
	            console.log(' type exists')
	        } else{
	        
	        	
				var msg = _t("The selected type file is not supported only theese types %s are supported.");
				this.displayNotification({
			type: 'danger',
			title: _t("File upload Type"),
			message: _.str.sprintf(msg, this.binary_supported_types),
		});
				
				return false;
			}
	        
	        this._super.apply(this, arguments);
	    },
		
	     
	  
	
	
	
	
});


});
