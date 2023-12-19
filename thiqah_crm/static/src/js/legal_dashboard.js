odoo.define('thiqah.legal.dashboard.component',function(require){
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var ajax = require('web.ajax');

    var _t = core._t;
    var QWeb = core.qweb;

    // Adding a client action
    var ThiqahLegalDashboard =AbstractAction.extend({
        hasControlPanel: true,
        template : '_legal_dashboard',
        events:{

            'click .legal-card':'onClickCard'

        },

        init: function(parent,context){
            this._super(parent,context);
            this.dashboard_templates = ['thiqah_legal_dashboard'];
        },

        start: function(){
            
            var self=this;
            this.set('title','Legal Dashboard');

            return this._super().then(function(){
                self.render_dashboards();
                self.render_dashbaord_data();

            });
        },

        render_dashboards: function(){
            var self= this;
            // Inject the widget in the DOM.
            _.each(this.dashboard_templates,function(template){
                self.$('.legal_dashboard_dom').append(QWeb.render(template,{ widget: self}))
            });
        },
        
        render_dashbaord_data: function(){
            ajax.jsonRpc('/render/legal/dashboard','call',{}).then(function(result){

                $('#running_count').text(result['running_count']);
                $('#pre_end_count').text(result['pre_end_count']);
                $('#end_count').text(result['end_count']);
                $('#total_contracts').text(result['contracts_count']);
    

                var dataSetPre = result['pre_end'];
                var dataSetEnd = result['end'];
                var dataSetRunnig = result['runnig'];

                let columns=[
                    { title: 'Name' },
                    { title: 'Client' },
                    { title: 'Project Name' },
                    { title: 'Responsible' },
                    { title: 'Start date' },
                    { title: 'End date' },
                ]

                $('#pre_end_contracts').DataTable({
                    data: dataSetPre,
                    columns: columns,
                });

                $('#end_contracts').DataTable({
                    data: dataSetEnd,
                    columns: columns,
                });

                $('#running_contracts').DataTable({
                    data: dataSetRunnig,
                    columns: columns,
                });
            
            });

        },

        // Events Tools
        onClickCard: function(e){
            var kind_card = $(e.target).attr('id');
            console.log("kind_card",kind_card)
            let domain = [];

            // Prepare the domain dynamically
            if (kind_card == 'legal_running_card'){
                domain.push(['state','=','running']);
            }
            else if(kind_card == 'legal_pre_end_card'){
                domain.push(['state','=','pre_end']);
            }
            else if(kind_card == 'legal_end_card'){
                domain.push(['state','=','end']);
            }
            else if(kind_card == '_total_legal_card'){
                domain = [];
            }
          
            this.do_action({
                name: _t("Contracts"),
                type: 'ir.actions.act_window',
                res_model: 'thiqah.contract',
                view_mode: 'tree,form',
                views: [[false, 'list'],[false, 'form']],
                domain: domain,
                target: 'current',
                context:{}
            })
        }

    });

    // Registering the client action:

    core.action_registry.add('ThiqahLegalDashboard',ThiqahLegalDashboard);

    return ThiqahLegalDashboard;




});

