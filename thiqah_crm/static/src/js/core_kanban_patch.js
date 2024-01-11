odoo.define('Thiqah.crm.kanban.renderer', function (require) {
    "use strict";

    var KanbanRenderer = require('web.KanbanRenderer');

    var rpc = require('web.rpc');


    // var ThiqahCRMKanbanRenderer = KanbanRenderer.extend({
    //     /**
    //      * @override
    //      */
    //     on_detach_callback: function () {
    //         this._super(...arguments);
    //     },
    // });

    // let myKanbanRenderer1 = KanbanRenderer.extend({
    //     start: function () {
    //         var self = this;
    //         console.log("self",self)
    //         return this._super().always(function(){
    //             console.log(self.$('span'), self.$el)
    //         })
    //     }
    // })
    // console.log("myKanbanRenderer1",myKanbanRenderer1)
    // return myKanbanRenderer1;

    let index_ids = {};

    KanbanRenderer.include({
        /**
         * Updates a given column with its new state.
         *
         * @param {string} localID the column id
         * @param {Object} columnState
         * @param {Object} [options]
         * @param {Object} [options.state] if set, this represents the new state
         * @param {boolean} [options.openQuickCreate] if true, directly opens the
         *   QuickCreate widget in the updated column
         *
         * @returns {Promise}
         */
        updateColumn: function (localID, columnState, options) {
            
            var self = this;
            var KanbanColumn = this.config.KanbanColumn;
            var newColumn = new KanbanColumn(this, columnState, this.columnOptions, this.recordOptions);

            var index = _.findIndex(this.widgets, {db_id: localID});

            index_ids[index] = newColumn.id

            // Thiqah Customization
            if (newColumn.relation == 'thiqah.crm.stage'){
                const lastKey = Object.keys(index_ids).pop();
                if (index == 1){
                    console.log("block")
                    return true;
                }    
            }

            // console.log("lastvalue",index_ids[lastKey])
            var column = this.widgets[index];
            

            this.widgets[index] = newColumn;
            if (options && options.state) {
                this._setState(options.state);
            }
            return newColumn.appendTo(document.createDocumentFragment()).then(function () {
                var def;
                if (options && options.openQuickCreate) {
                    def = newColumn.addQuickCreate();
                }
                return Promise.resolve(def).then(function () {
                    newColumn.$el.insertAfter(column.$el);
                    self._toggleNoContentHelper();
                    // When a record has been quick created, the new column directly
                    // renders the quick create widget (to allow quick creating several
                    // records in a row). However, as we render this column in a
                    // fragment, the quick create widget can't be correctly focused. So
                    // we manually call on_attach_callback to focus it once in the DOM.
                    newColumn.on_attach_callback();
                    column.destroy();
                });
            });
        },
    
     
      
    });
    
    });
    