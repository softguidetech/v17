odoo.define('thiqah_crm.crm_edit', function (require) {
	var FormView = require('web.FormView');
	var FormController = require('web.FormController');
	var session = require('web.session');
	var pass_ = false;
    FormController.include({
    	 update: async function (params, options) {
    		 this._super.apply(this, arguments);    	     
    	    },
	
    	updateButtons: function () {
    		this._super.apply(this, arguments);
			 
			
			// console.log("this.env",this.initialState.data.id);
    		 
    		if (this.modelName === 'crm.lead') {
				if (!this.$buttons) {
					return ;
				}
				var editbtn=this.$buttons.find('.o_form_button_edit');
				var currentpath=window.location.href;
				 
				if(currentpath.indexOf("#id=") !== -1){
					var record=currentpath.split('#id=')[1];
					var recordId=record.split('&')[0];
					}
				else if(currentpath.indexOf("&id=") !== -1){
					var record=currentpath.split('&id=')[1];
					var recordId=record.split('&')[0];
						
				}
				else if(currentpath.indexOf("?id=") !== -1){
					var record=currentpath.split('?id=')[1];
					var recordId=record.split('&')[0];
						
				}
				else
				{
					var recordId=this.model.loadParams.res_id;
				}

		      	this._rpc({
					model: 'crm.lead',
					method: 'check_is_brochure_evaluation_stage',
					args: [parseInt(recordId)],
				})
				.then(function (result) {
	
					if (result == true)
					{	
						if (!editbtn || !editbtn[0]) {
							return ;
						}
						editbtn[0].style.display='none';
						editbtn.addClass('hidden');

					}
					else{
						if (!editbtn || !editbtn[0]) {
							return ;
							}
							editbtn[0].style.display='block';
							editbtn.removeClass('hidden');
					}		
				});
				
				
						
		          	 
		 
    	 }
    		 //return this._super.apply(this, arguments);
    	 }
    	
});
});