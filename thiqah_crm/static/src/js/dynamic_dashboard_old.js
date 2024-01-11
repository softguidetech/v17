odoo.define('thiqah_crm.crmDashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var ThiqahCRMDashboard = AbstractAction.extend({
    template: 'thiqah_crm_dashboard',
    events: {
            // Open views Odoo
           'click .wathiq_opportunities': 'wathiq_opportunities',
           'click .wathiq_enterprise_opportunities': 'wathiq_enterprise_opportunities',
           'click .wathiq_basic_opportunities': 'wathiq_basic_opportunities',
           'click .wathiq_batch_opportunities':'wathiq_batch_opportunities',
           'click .print_dashboard':'fct_print_dashboard',

          //filters
          'change #choose_partner': function(e) {
            e.stopPropagation();
            var $target = $(e.target);
            var partner= $target.val();
            var account_manager = $('#choose_account_manager').val();
            var product = $('#choose_product').val();
            this.change_template_by_filter(partner,product,account_manager);

          },
          'change #choose_product': function(e) {
            e.stopPropagation();
            var $target = $(e.target);
            var product = $target.val();
            var account_manager = $('#choose_account_manager').val();
            var partner = $('#choose_partner').val();
            this.change_template_by_filter(partner,product,account_manager);

          },
          'change #choose_account_manager': function(e) {
            e.stopPropagation();
            var $target = $(e.target);
            var account_manager = $target.val();
            var product = $('#choose_product').val();
            var partner = $('#choose_partner').val();
            this.change_template_by_filter(partner,product,account_manager);

          },
      
    },
    init: function (parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['thiqah_crm_dashboard_document'];
        this.get_top_ten_clients1=[];
        this.get_top_ten_clients2=[];
        this.list_account_managers=[];
        this.list_partners=[];
        this.list_products=[];
        this.get_total_top_ten_clients_revenue=0;
        this.total_revenue=0;
    },
    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.render_wathiq_basic_enterprise_bar_chart_graph();
            self.render_wathiq_enterprise_by_stages_bar_chart_graph();
            self.render_requests_by_stages_bar_chart_graph();
            self.render_opports_month_graph();
            self.render_annual_chart_graph();
            
        });
    },

  
    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.dashboard_fetch_data();
            
        });
    },
    render_dashboards: function () {
      var self = this;
      _.each(this.dashboards_templates, function (template) {
          self.$('.CRM_dashboard').append(QWeb.render(template, { widget: self }));
      });
  },

  // Print Dashboard Data
  fct_print_dashboard: function () {
    var self = this;
  //  this.do_action('thiqah_crm.thiqah_dashboard_reports');
    var data = this._rpc({
      model: 'crm.lead',
      method: 'action_dashboard_report_print',
      args: [[]],
  }).then(function (res) {

      console.log("Success",res);
      return res.res_ids;
        
  });
  console.log("Successres.data",data);
  return this.do_action('thiqah_crm.thiqah_dashboard_reports',{
    additional_context: { active_ids: data}
    });
  //return $.when(data);
  },
  //Wathiq Opportunities
      wathiq_opportunities: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        // get filter values to domain
        var product = $('#choose_product').val();
        var partner = $('#choose_partner').val();
        var account_manager = $('#choose_account_manager').val();
        var domain_filter=[['is_wathiq', '=', true],['type','=','opportunity'],['stage_id.is_won','=',true],];
        if (product){domain_filter.push(['product_ids','in',[parseInt(product)]])}
        if (partner){domain_filter.push(['partner_id','=',parseInt(partner)])}
        if (account_manager){domain_filter.push(['partner_id.account_manager','=',parseInt(account_manager)])}
        
        this.do_action({
            name: _t("Wathiq Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form,calendar',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form'],[false, 'calendar'],],
            domain: domain_filter,
            target: 'current',
            context:{'default_type': 'opportunity',  'form_view_ref':'thiqah_crm.thiqah_aahd_crm_lead_view_form', 'default_for_aahd':true,}
        })
    },
     //Wathiq Enterprise Opportunities
     wathiq_enterprise_opportunities: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        
          // get filter values to domain
          var product = $('#choose_product').val();
          var partner = $('#choose_partner').val();
          var account_manager = $('#choose_account_manager').val();
          var domain_filter=[['is_wathiq', '=', true],['service_type', '=', 'enterprise'],['type','=','opportunity'],['stage_id.is_won','=',true],];
          if (product){domain_filter.push(['product_ids','in',[parseInt(product)]])}
          if (partner){domain_filter.push(['partner_id','=',parseInt(partner)])}
          if (account_manager){domain_filter.push(['partner_id.account_manager','=',parseInt(account_manager)])}
          
        this.do_action({
            name: _t("Wathiq Enterprise Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form,calendar',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form'],[false, 'calendar'],],
            domain: domain_filter,
            target: 'current',
            context:{'default_type': 'opportunity',  'form_view_ref':'thiqah_crm.thiqah_aahd_crm_lead_view_form', 'default_for_aahd':true,}
        })
    },
       //Wathiq Basic Opportunities
       wathiq_basic_opportunities: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        
          // get filter values to domain
          var product = $('#choose_product').val();
          var partner = $('#choose_partner').val();
          var account_manager = $('#choose_account_manager').val();
          var domain_filter=[['is_wathiq', '=', true],['service_type', '=', 'basic'],['type','=','opportunity'],['stage_id.is_won','=',true],];
          if (product){domain_filter.push(['product_ids','in',[parseInt(product)]])}
          if (partner){domain_filter.push(['partner_id','=',parseInt(partner)])}
          if (account_manager){domain_filter.push(['partner_id.account_manager','=',parseInt(account_manager)])}
          
        this.do_action({
            name: _t("Wathiq Basic Opportunities"),
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form,calendar',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form'],[false, 'calendar'],],
            domain: domain_filter,
            target: 'current',
            context:{'default_type': 'opportunity',  'form_view_ref':'thiqah_crm.thiqah_aahd_crm_lead_view_form', 'default_for_aahd':true,}
        })
    },
          //Wathiq Batch Opportunities
          wathiq_batch_opportunities: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            
              // get filter values to domain
              var product = $('#choose_product').val();
              var partner = $('#choose_partner').val();
              var account_manager = $('#choose_account_manager').val();
              var domain_filter=[['is_wathiq', '=', true],['service_type', '=', 'batch'],['type','=','opportunity'],['stage_id.is_won','=',true],];
              if (product){domain_filter.push(['product_ids','in',[parseInt(product)]])}
              if (partner){domain_filter.push(['partner_id','=',parseInt(partner)])}
              if (account_manager){domain_filter.push(['partner_id.account_manager','=',parseInt(account_manager)])}
              
            this.do_action({
                name: _t("Wathiq Batch Opportunities"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form,calendar',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form'],[false, 'calendar'],],
                domain: domain_filter,
                target: 'current',
                context:{'default_type': 'opportunity',  'form_view_ref':'thiqah_crm.thiqah_aahd_crm_lead_view_form', 'default_for_aahd':true,}
            })
        },
    // Get Dashboard Data
    dashboard_fetch_data: function () {
            var self = this;
            var data = this._rpc({
                model: 'crm.lead',
                method: 'get_dashboard_data',
                args: []
            }).then(function (result) {
                self.total_opports_wathiq = result['total_opports_wathiq'];
                self.total_opports_basic = result['total_opports_basic'];
                self.total_opports_enterprise = result['total_opports_enterprise'];
                self.total_opports_batch=result['total_opports_batch'];
                self.total_opports = result['total_opports'];
                self.total_revenue = result['total_revenue'];
                self.get_top_ten_clients1  = result['get_top_ten_clients_1'];
                self.get_top_ten_clients2 = result['get_top_ten_clients_2'];
                self.get_total_top_ten_clients_revenue=result['get_total_top_ten_clients_revenue'];
                self.total_revenue=result['total_revenue'];
                self.list_partners = result['list_partners'];
                self.list_account_managers=result['list_account_managers'];
                self.list_products=result['list_products'];
                self.growth_goal=result['growth_goal'];
                self.percent_growth = result['percent_growth'];
            });
            return $.when(data);
        },
        
        render_wathiq_basic_enterprise_bar_chart_graph:function (partner,product,account_manager) {
        
        var self = this;
        $('.canvas_wathiq_basic_enterprise_bar_chart').html("").append('<canvas id="wathiq_basic_enterprise_bar_chart" class="wathiq_basic_enterprise_bar_chart" width="340px" height="280px" ><canvas>');
         
            var ctx = this.$("#wathiq_basic_enterprise_bar_chart");
          
            rpc.query({
              model: "crm.lead",
                method: "get_wathiq_basic_enterprise_bar_chart",
                args:[partner,product,account_manager]
            }).then(function (arrays) {
                        var data = {
                            labels : arrays[0],
                            datasets:   [{
                                label: "",
                                data: arrays[1],
                                backgroundColor: [
                                      "#595959",
                                      "#36b4e5",
                                      "#00bdb4"
                                ],
                                borderColor: [
                                    "#595959",
                                    "#36b4e5",
                                    "#00bdb4"
                                ],
                               
                                borderWidth: 1,
                                datalabels: {
                                    color: "#fff",
                                    anchor: 'center',
                                    align: 'center',
                                    formatter: (val, context) => val != 0 ? (((val/arrays[2])*100).toFixed(0)+'%') :'', },
                            
                            },],
                        };
                  

                        var chart = new Chart(ctx, {
                            type: "bar",
                            data: data,
                          plugins: [ChartDataLabels],
                        //    
                            options: {
                            	responsive: true,
                              animations: false,
                                title: {

                                    display:false,
                                    text:''
                                },
                                plugins: {
                                	 datalabels: {
                                         color: '#fff',
                                         display: true, 
                                         font: {
                                           size: '20',
                                           weight: 'bold',
                                           anchor: 'center',
                                           align: 'center',
                                       },
                                    
                                       },
                                },
                                tooltips: {
                                    enabled: false,
                                },
                                maintainAspectRatio: false,
                                
                                legend: {
                                    position: 'right',
                                    onClick: function() {
                                      return null;
                                    },
                                    labels: {
                                      generateLabels: function(chart) {
                                        return chart.data.labels.map(function(label, i) {
                                          return {
                                            text: label,
                                            fillStyle: chart.data.datasets[0].backgroundColor[i]
                                          };
                                        });
                                      }
                                    }
                            },
                                
                                scales: {
                                    yAxes: [{
                                        ticks: {
                                          beginAtZero: true,
                                          stepSize:0.5,
                                          precision: 0.5,
                                        }
                                      }]
                                    },
                            }
                        });
                      
                    });
            		
            		
            		
            		
      
        },
        
        render_wathiq_enterprise_by_stages_bar_chart_graph:function (partner,product,account_manager) {
          
                var self = this
                $('.canvas_wathiq_enterprise_stages_bar_chart').html("").append('<canvas id="wathiq_enterprise_stages_bar_chart" class="wathiq_enterprise_stages_bar_chart" width="340px" height="280px" ><canvas>');
                var ctx = self.$("#wathiq_enterprise_stages_bar_chart");
                rpc.query({
                  model: "crm.lead",
                    method: "get_wathiq_enterprise_by_stages_bar_chart",
                    args: [partner,product,account_manager]
                }).then(function (arrays) {
                            var data = {
                                labels : arrays[1],
                                datasets: [{
                                    label: "",
                                    data: arrays[0],
                                    backgroundColor: [
                                          "#00bdb4",
                                          "#36b4e5",
                                          "#727272",
                                          "#464647",
                                          "#7030a0",
                                          "#9dd4c9"
                                    ],
                                    borderColor: [
                                      "#00bdb4",
                                      "#36b4e5",
                                      "#727272",
                                      "#464647",
                                      "#7030a0",
                                      "#9dd4c9"
                                    ],
                                    borderWidth: 1,
                                    datalabels: {
                                        color: '#fff',
                                        display: true, 
                                        font: {
                                          size: '20',
                                          weight: 'bold',
                                          anchor: 'center',
                                          align: 'center',
                                        },
                                       
                                        formatter: (val, context) => val != 0 ? (((val/arrays[2])*100).toFixed(0)+'%') :'' , 
                                        
                                    },
                                },]
                            };

                           

                            //create Chart class object
                            var chart = new Chart(ctx, {
                                type: "bar",
                                data: data,
                               
                                options: {
                                    responsive:true,
                                  
                                        tooltips: {
                                            enabled: false,
                                        },
                                    maintainAspectRatio: false,
                           
                                    scales: {
                                      yAxes: [{
                                          ticks: {
                                            beginAtZero: true,
                                            
                                          }
                                        }]
                                      },
                                      
                                    legend: {
                                        position: 'right',
                                        onClick: function() {
                                          return null;
                                        },
                                        labels: {
                                          generateLabels: function(chart) {
                                            return chart.data.labels.map(function(label, i) {
                                              return {
                                                text: label,
                                                fillStyle: chart.data.datasets[0].backgroundColor[i]
                                              };
                                            });
                                          }
                                        }
                                },
                                },
                                
                            });
                        });
                		
                		
                		
                		
          
            }, 

          
            render_requests_by_stages_bar_chart_graph:function (partner,product,account_manager) {
            
                var self = this
                  
                    $('.canvas_wathiq_requests_bar_chart').html("").append('<canvas id="wathiq_requests_bar_chart" class="wathiq_requests_bar_chart" width="340px" height="280px" ><canvas>');
                    var ctx = self.$("#wathiq_requests_bar_chart");
                    rpc.query({
                      model: "crm.lead",
                        method: "get_wathiq_batch_by_stages_bar_chart",
                        args: [partner,product,account_manager]
                    }).then(function (arrays) {
                                var data = {
                                    labels : arrays[1],
                                    datasets: [{
                                        label: "",
                                        data: arrays[0],
                                        backgroundColor: [
                                          "#00bdb4",
                                          "#36b4e5",
                                          "#727272",
                                          "#464647",
                                          "#7030a0",
                                          "#9dd4c9"
                                    ],
                                    borderColor: [
                                      "#00bdb4",
                                      "#36b4e5",
                                      "#727272",
                                      "#464647",
                                      "#7030a0",
                                      "#9dd4c9"
                                    ],
                                        borderWidth: 1,
                                        datalabels: {
                                            color: '#fff',
                                            display: true, 
                                            font: {
                                              size: '20',
                                              weight: 'bold',
                                              anchor: 'center',
                                              align: 'center',
                                            },
                                            formatter: (val, context) =>  val != 0 ? (((val/arrays[2])*100).toFixed(0)+'%') :'', 
                                           
                                            
                                        },
                                        
                                    },]
                                };
    
                              
    
                                //create Chart class object
                                var chart = new Chart(ctx, {
                                    type: "bar",
                                    data: data,
                                    options: {
                                        responsive:true,
                                        maintainAspectRatio: false,
                                        scales: {
                                          yAxes: [{
                                              ticks: {
                                                beginAtZero: true,
                                                
                                              }
                                            }]
                                          },
                                          tooltips: {
                                              enabled: false,
                                          },
                                        legend: {
                                            position: 'right',
                                            onClick: function() {
                                              return null;
                                            },
                                            labels: {
                                              generateLabels: function(chart) {
                                                return chart.data.labels.map(function(label, i) {
                                                  return {
                                                    text: label,
                                                    fillStyle: chart.data.datasets[0].backgroundColor[i]
                                                  };
                                                });
                                              }
                                            }
                                    },
                                
                                },
                               
                                });
                            });
                            
                            
                            
                            
              
                }, 

        render_opports_month_graph: function(partner,product,account_manager) {
                    
                        var self = this;
                        
                      
                       $('.canvas_opports_month').html("").append('<canvas id="opports_month" class="opports_month" width="340px" height="280px" ><canvas>');
                       var ctx = self.$("#opports_month");
                        rpc.query({
                            model: "crm.lead",
                            method: "get_opportunities_month_chart",
                            args: [partner,product,account_manager]
                        }).then(function (result) {
                            // Define the data
                var months = result[0] // Add data values to array
                var count1 = result[1];
                var count2 = result[2];
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: months,//x axis
                        //leng: [_t('Subscriptions'), _t('Transactions')],
                        datasets: [{
                            label: _t('Subscriptions'), 
                            data: count1, 
                            backgroundColor: '#4d4185',
                            borderColor: '#4d4185',
                            datalabels: {
                                color: "#fff",
                                anchor: 'center',
                                align: 'center',
                                font: {
                                    size: '20',
                                    weight: 'bold',
                                    anchor: 'center',
                                    align: 'center',
                                },
                                formatter: (val, context) => (val != 0 ? val :''), 
                               
                                
                            },
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', 
                            fill: false
                        },
                        {
                            label: _t('Transactions'), // Name 
                            data: count2, // Specify the data values array
                            backgroundColor: '#30b5e4',
                            borderColor: '#30b5e4',
                            datalabels: {
                                color: "#fff",
                                anchor: 'center',
                                align: 'center',
                                font: {
                                    size: '20',
                                    weight: 'bold',
                                    anchor: 'center',
                                    align: 'center',
                                },
                                formatter: (val, context) => (val != 0 ? val :''), 
                               
                                
                            },
                            minBarLength: 0,
                            borderWidth: 1, // Specify bar border width
                            type: 'bar', // Set this data to a line chart
                            fill: false
                        }
                    
                    
                    
                    ]
                    },
                    options: {
                      scales: {
                        yAxes: [{
                            ticks: {
                              beginAtZero: true,
                              
                            }
                          }]
                        },
                        responsive: true, // Instruct chart js to respond nicely.
                        maintainAspectRatio: false, // Add to prevent default behaviour of full-width/height
                        tooltips: {
                            enabled: false,
                        },
                        legend: {
                          position: 'right',
                          onClick: function() {
                            return null;
                          },
                          labels: {
                            generateLabels: function(chart) {
                              return chart.data.datasets.map(function(label, i) {
                                return {
                                  text: chart.data.datasets[i].label,
                                  fillStyle: chart.data.datasets[i].backgroundColor
                                };
                              });
                            }
                          }
                  },
                    }
                });





                        });
                    },
                    
        render_annual_chart_graph:function(partner,product,account_manager){
            var self = this
            
            //$('#canvas_annual_target').html("");
            $('.canvas_annual_target').html("").append('<canvas id="annual_target" class="annual_target" width="340px" height="280px" ><canvas>');
            var ctx = self.$("#annual_target");
            rpc.query({
                model: "crm.lead",
                method: "get_the_annual_target",
                args: [partner,product,account_manager]
            }).then(function (result) {
                      // Define the data
                      var myChart = new Chart(ctx, {
                          type: 'bar',
                          data: {
                              labels: result[0],//x axis
                              datasets:  [{
                                label: "",
                                data: result[1],
                                barPercentage: 0.5,
                                backgroundColor: [
                                      "#003f5c",
                                      "#2f4b7c",
                                      "#f95d6a",
                                      "#665191",
                                      "#d45087",
                                      "#ff7c43",
                                      "#ffa600",
                                      "#a05195",
                                      "#6d5c16"
                                ],
                                borderColor: [
                                      "#003f5c",
                                      "#2f4b7c",
                                      "#f95d6a",
                                      "#665191",
                                      "#d45087",
                                      "#ff7c43",
                                      "#ffa600",
                                      "#a05195",
                                      "#6d5c16"
                                ],
                                borderWidth: 1,
                                datalabels: {
                                    color: "#fff",
                                    anchor: 'center',
                                    align: 'center',
                                    font: {
                                        size: '20',
                                        weight: 'bold',
                                        anchor: 'center',
                                        align: 'center',
                                    },
                                    formatter: (val, context) => val != 0 ? (((val/result[2])*100).toFixed(0)+'%') :'',  
                                    
                                    
                                },
                            },]
                          },
          
                          options: {
                            responsive:true,
                            maintainAspectRatio: false,
                            scales: {
                              yAxes: [{
                                  ticks: {
                                    beginAtZero: true,
                                    
                                  }
                                }]
                              },
                            title: {
                                display: false,
                                text: "",
                              },
                              plugins: {
                             	 datalabels: {
                                      color: '#fff',
                                      display: true, 
                                      font: {
                                        size: '20',
                                        weight: 'bold',
                                        anchor: 'center',
                                        align: 'center',
                                    },
                                 
                                    },
                             },
                             tooltips: {
                                 enabled: false,
                             },
                            legend: {
                                position: 'bottom',
                                onClick: function() {
                                  return null;
                                },
                                labels: {
                                  generateLabels: function(chart) {
                                    return chart.data.labels.map(function(label, i) {
                                      return {
                                        text: label,
                                        fillStyle: chart.data.datasets[0].backgroundColor[i]
                                      };
                                    });
                                  }
                                }
                        },
                        },
                       
                          
                      });
      
      
            });
        },

        change_template_by_filter:function(partner,product,account_manager){
          var self = this;
          this._rpc({
            model: 'crm.lead',
            method: 'get_dashboard_data',
            args: [partner,product,account_manager]
          }).then(function (result) {
          
            $('#total_opports_wathiq')[0].innerHTML = result['total_opports_wathiq'];
            $('#total_opports_basic')[0].innerHTML = result['total_opports_basic'];
            $('#total_opports_enterprise')[0].innerHTML = result['total_opports_enterprise'];
            $('#total_opports_batch')[0].innerHTML = result['total_opports_batch'];
            $('#total_revenue')[0].innerHTML = result['total_revenue'];
          });
        
     
          self.render_wathiq_basic_enterprise_bar_chart_graph(partner,product,account_manager);
          self.render_wathiq_enterprise_by_stages_bar_chart_graph(partner,product,account_manager);
          self.render_requests_by_stages_bar_chart_graph(partner,product,account_manager);
          self.render_opports_month_graph(partner,product,account_manager);
          self.render_annual_chart_graph(partner,product,account_manager);
        },
      




});


core.action_registry.add('ThiqahCRMDashboard', ThiqahCRMDashboard);

return ThiqahCRMDashboard;

});
