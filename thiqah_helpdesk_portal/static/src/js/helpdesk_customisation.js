odoo.define('helpdesk.ticket_submit', function(require) {
    "use strict";
    var rpc = require('web.rpc')
    var session = require('web.session')

    $('#helpdesk_ticket_form').ready(function() {

        // $("#ticket_type_id option").each(function()
        // {
        //     // Add $(this).val() to your list
            
        //     let element = document.getElementById("change_request");
        //     element.setAttribute("hidden", "hidden");
            
        //     if (element){
        //         session.user_has_group('thiqah_crm.group_thiqah_sp_manager').then(function(has_group){
        //             if (has_group){
        //                 element.removeAttribute("hidden");
        //             }
                    
        //         });
        //         return false;
        //     }
        
        // });
       

        $('#ticket_type_id').change(function() {
            var div_exist_customer = $('#div_exist_customer');
            div_exist_customer.removeClass('d-none');
            
             // getting custom attribute ('for-sp', help="Type for SP Manager") from selected option.
            var option = $('option:selected', this).attr('for-sp');

            if (option !== undefined) { 
            
                // Visibility of the 'section existing customer' depending from the choice of the change request.
                if (option.toLowerCase() === 'true'){

                    div_exist_customer.addClass('d-none');
                }
                else{
                    div_exist_customer.removeClass('d-none');
                }

        }
    
            /* Get Ticket type ID */
            var ticket_type_id = $(this).val();
            /* Call Python function that return team and description according to ticket type */
            rpc.query({
                model: 'helpdesk.ticket.type',
                method: 'get_team_id',
                args: [ticket_type_id],
            }).then(function(result) {
                /* Update 'team_id' value and 'description' value if exist */
                if (result !== undefined) {

                    $('[name="user_id"]').val(result.user_id);
                    $('[name="team_id"]').val(result.ticket_team_id_id);
                    $('[name="description"]').val(result.description);
                    if (result.required_attachment =="required")
                    {
                        $("#required_attachment").removeClass('s_website_form_dnone');
                        $('[id="helpdesk5"]').attr({required:'required'});

                    }
                    else{
                        $("#required_attachment").addClass('s_website_form_dnone');
                        $('[id="helpdesk5"]').prop( "required", null );
                    }
                }
            });
        });


        $('#exist_customer').change(function() {
            if ($(this).is(':checked') == true)
            {
                console.log('_________ True');
                $(".is_sector").removeClass('d-none');
                $(".input_customer").removeClass('d-none');
                $(".responsible_name").removeClass('d-none');
                $(".responsible_mobile").removeClass('d-none');
                $(".customer_name").addClass('d-none');
                $(".customer_email").addClass('d-none');
                $(".input_position").addClass('d-none');
                $(".customer_name").removeClass('s_website_form_model_required');
                $(".customer_email").removeClass('s_website_form_model_required');
                $(".input_position").removeClass('s_website_form_model_required');
                $('[id="helpdesk1"]').prop("required", null );
                $('[id="helpdesk2"]').prop("required", null );
            }
            else{
                console.log('_________ False');
                $(".input_customer").addClass('d-none');
                $(".is_sector").addClass('d-none');
                $(".responsible_mobile").addClass('d-none');
                $(".responsible_name").addClass('d-none');
                $(".input_customer").removeClass('s_website_form_model_required');
                $(".responsible_mobile").removeClass('s_website_form_model_required');
                $(".responsible_name").removeClass('s_website_form_model_required');
                $('[id="partner_id"]').prop( "required", null );
                $(".customer_name").removeClass('d-none');
                $(".customer_email").removeClass('d-none');
                $(".input_position").removeClass('d-none');
                $('[id="helpdesk1"]').attr({required:'required'});
                $('[id="helpdesk2"]').attr({required:'required'});
            }
        });

         // add function onchange of sector
        $('#sector_id').change(function() {
            var sector_id = $(this).val();
            if (sector_id !== undefined && sector_id !== null) {
                rpc.query({
                    model: 'category.portfolio',
                    method: 'get_portfolio_info',
                    args: [sector_id],
                }).then(function(result) {
                    if (result !== undefined) {
                        $('[name="responsible_name"]').val(result.sp_manager_name);
                        $('[name="user_id"]').val(result.user_id);
                        if (result.mobile){
                            $('[name="responsible_mobile"]').val(result.mobile);
                        }
                        else{
                        $('[name="responsible_mobile"]').val('');
                        }
                    }
                });
                
                rpc.query({
                    model: 'category.portfolio',
                    method: 'get_contacts',
                    args: [sector_id],
                }).then(function(result) {
                    if (result !== undefined) {
                    var select = document.getElementById("partner_id");
//                        $('[name="partner_id"]').empty();
                        for (var i = 0; i < result.length; i++) {
                            var opt = document.createElement('option');
                            opt.textContent = result[i]['name'];
                            opt.value = result[i]['id'];
                            select.appendChild(opt);
                        }
                    }
                });
            }


        });


//        add function submit
    });
});