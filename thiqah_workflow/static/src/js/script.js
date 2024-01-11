odoo.define('workflow.reload.FormView',function(require){
    'user strict';

    var FormView = require('web.FormView');



    var RelaodFormView = FormView.extend({

        /**
         * append the renderer and instantiate the line renderers
         *
         * @override
         */
        start: function () {
            console.log("reload hereeee")
            var self = this;
            var args = arguments;
            var sup = this._super;
            return sup.apply(self, args);
        },
       
    });

    return RelaodFormView;





});