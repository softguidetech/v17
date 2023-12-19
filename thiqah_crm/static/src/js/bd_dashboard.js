odoo.define('thiqah.bd.dashboard', function(require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var ajax = require('web.ajax'); 

    var _t = core._t;
    var QWeb = core.qweb;

    var ThiqahDashboardBd = AbstractAction.extend({
        jsLibs: [
            '/web/static/lib/Chart/Chart.js',
        ],
        hasControlPanel: true,
        template: 'thiqah_bd_dashboard',
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['thiqah_bd_dashboard'];
        },
        start: function() {
            var self = this;
            this.set("title", 'BD Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.render_dashbaord_data();
            });
        },
    
        // willStart: function() {
        //     var self = this;
        //     return $.when(ajax.loadLibs(this), this._super()).then(function() {
        //         return self.dashboard_fetch_data();
                
        //     });
        // },

        render_dashboards: function () {
          var self = this;
          // Append the widget to the proper place in the DOM.
          _.each(this.dashboards_templates, function (template) {
              self.$('.bd_dashboard_dom').append(QWeb.render(template, { widget: self }));
          });
        },

        // https://www.30secondsofcode.org/articles/s/js-remove-trailing-zeros
        toFixedWithoutZeros: function(num,precision){
            return num.toFixed(precision).replace(/\.0+$/, '');
        },

        render_dashbaord_data: function(){
            var leadSourceID = this.$("#leadSource");
            var DBopportunitiesValueID = this.$("#DBopportunitiesValue");
            

                    
            // One call to get all dashboard data
            ajax.jsonRpc('/bd/sales/dashboard','call',{}).then(function(result){
                // Card data
                const total_opportunities = parseInt(result.total_opportunities)
                $('#_bd_total_opportunities').text(total_opportunities);
                $('#_bd_winnig_opportunities').text(result['bd_winnig_opportunities']);
                $('#_bd_lost_opportunities').text(result['bd_lost_opportunities']);
                $('#_bd_revenue_opportunities').text(result['bd_revenue']);

                // Common Attributes
                var barColors = [
                    "#a1c4d5",
                    "#cbd7a7",
                    "#daeddb",
                    "#d8c8d8",
                ];
                const datalabels = {
                    color: 'white',
                    // anchor:'end',
                    // align:'end',
                    // offset:5,
                    backgroundColor:'#6f42c1',
                    borderColor:'white',
                    borderWidth:1,
                    borderRadius:5,
                    font:{
                        weight:'bold'
                    },
                    // padding:5,
                    formatter: function(value, context) {
                        var number_ = (context.chart.data.datasets[0].data[context.dataIndex]/total_opportunities)*100
                        return number_.toFixed(1).replace(/\.0+$/, '').toString()+'%';
                    }
                  }
                var callbacks = { 
                    label: function(tooltipItem, data) {
                        const number = parseInt(tooltipItem.value).toString()
                        console.log(number)
                        const len = number.length
                        const place = len % 3 || 3
                        let abb, r
                        switch(true) {
                        case len > 9:
                            abb = 'B'
                            break
                        case len > 6:
                            abb = 'M'
                            break
                        case len > 3:
                            abb = 'K'
                            break
                        default:
                            return number
                        }
                        return `${number.slice(0, place)}.${number.slice(place, place + 1)}${abb}`
                    
                    },
                }
                var ticks = {
                    min: 0,
                    callback: function(value){
                        const number = value.toString()
                        console.log(number)
                        const len = number.length
                        const place = len % 3 || 3
                        let abb, r
                        switch(true) {
                        case len > 9:
                            abb = 'B'
                            break
                        case len > 6:
                            abb = 'M'
                            break
                        case len > 3:
                            abb = 'K'
                            break
                        default:
                            return number
                        }
                        return `${number.slice(0, place)}.${number.slice(place, place + 1)}${abb}`
                        // return value+ "%"
                    }
                    
                };
                
                var projectsAwardedBD = result.projects_awarded_BD
                var divsToAppend = "";
                let opportunity_value = 0;

                $.each( projectsAwardedBD, function( index ,item ) {
                    const number = item[1].toString();
                    console.log(number)
                    // const number = 1234.2893;
                    const len = number.length
                    const place = len % 3 || 3
                    let abb, r
                    switch(true) {
                    case len > 9:
                        abb = 'B'
                        break
                    case len > 6:
                        abb = 'M'
                        break
                    case len > 3:
                        abb = 'K'
                        break
                    default:
                        opportunity_value =  number
                    }

                    opportunity_value = `${number.slice(0, place)}.${number.slice(place, place + 1)}${abb}`
                    
                    divsToAppend += `
                   
                        <div class="col-12">
    
                            <div class="badge badge-purple" >
                                
                                ${item[0]}
    
                            </div>
    
                            <div style="color:white;" class="badge badge-warning" >
                                
                                ${opportunity_value}
                                
    
                            </div>
                    
                        </div>
                    
    
                    `; 
                });  

                $('#table_awarded_bd').append(divsToAppend);
                

                // Chart(s)
                var leadSourceData = result.lead_source_data
                var OpportunitiesValues = result.BdOpportunitiesValues



                 // Lead Source
                 new Chart(leadSourceID, {
                    type: 'bar',
                    data:{
                    labels: leadSourceData[0],
                        datasets: [{
                            label: 'Count of Opportunities',
                            data: leadSourceData[1],
                            backgroundColor: barColors,
                            borderColor: barColors,
                            borderWidth: 1,
                            datalabels: datalabels
                        }]
                },
                
                    options: {
                        tooltips: {
                                    callbacks: {
                                        afterTitle: function(tooltipItem, chart){
                                            return '----------------';
                                        },
                                        afterBody: function(tooltipItem, chart){
                                            return '----------------';
                                        },
                                        footer: function(tooltipItem, chart){
                                            return 'Total Amount: '+leadSourceData[2][tooltipItem[0].index];
                                        }
            
                                    }
                                },
                        legend: {
                            display: false,
                            position: 'top',
                        },
                        scales: {
                             xAxes: [{
                                gridLines: {
                                   display: false
                                }
                             }],
                             yAxes: [{
                                ticks: {
                                    min: 0,
                                    stepSize: 5
                                    //    max: 100,
                                    // callback: function(value){return value+ "%"}
                                    },  
                                        scaleLabel: {
                                        display: false,
                                        labelString: "Lead Source"
                                    },
                                // display: false,
                                gridLines: {
                                   display: true
                                }
                             }]
                        }
                     },
                     
                    plugins: [ChartDataLabels]
                });


                // Opportunity Value Chart
                new Chart(DBopportunitiesValueID, {
                    type: 'bar',
                    data:{
                    labels: OpportunitiesValues[0],
                        datasets: [{
                            label: 'Opportunity Value',
                            data: OpportunitiesValues[1],
                            backgroundColor: barColors,
                            borderColor: barColors,
                            borderWidth: 1,
                            datalabels: {
                                color: 'white',
                                // anchor:'end',
                                // align:'end',
                                // offset:5,
                                backgroundColor:'#6f42c1',
                                borderColor:'white',
                                borderWidth:1,
                                borderRadius:5,
                                font:{
                                    weight:'bold'
                                },
                                padding:5,
                                formatter: function(value, context) {
                                    var number = context.chart.data.datasets[0].data[context.dataIndex]
                                    console.log(number)
                                    const number_ = parseInt(number).toString()
                                    const len = number_.length
                                    const place = len % 3 || 3
                                    let abb, r
                                    switch(true) {
                                    case len > 9:
                                        abb = 'B'
                                        break
                                    case len > 6:
                                        abb = 'M'
                                        break
                                    case len > 3:
                                        abb = 'K'
                                        break
                                    default:
                                        return number_
                                    }
                                    return `${number_.slice(0, place)}.${number_.slice(place, place + 1)}${abb}`
                                }
                            }
                        }]
                },
                
                options: {
                    legend: {
                        display: false,
                        position: 'top',
                        },
                    tooltips: { 
                        callbacks: callbacks,
                        }, 
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false
                            }
                        }],
                        
                        yAxes: [{
                            display: false,
                            ticks : ticks,  
                            gridLines: {
                                display: false
                            }
                        }]
                    }
                },
                plugins: [ChartDataLabels]
                });
            
            });

       

        
       
       

      }


    });

    // Registering the widget in the action registry.
    core.action_registry.add('ThiqahDashboardBd',ThiqahDashboardBd);

    return ThiqahDashboardBd;

    
});