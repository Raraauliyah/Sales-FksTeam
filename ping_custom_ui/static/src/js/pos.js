odoo.define('pos_create_sale_order.pos', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var Model = require('web.DataModel');
var _t = core._t;


var QWeb = core.qweb;

var ActionpadWidget = screens.ActionpadWidget.include({
    renderElement: function() {
        var self = this;
        var invoiced = new $.Deferred();
        var done = new $.Deferred(); // holds the mutex
        this._super();
        this.$('#create_sale_order').click(function(){
            var order = self.pos.get_order();
            var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                return line.has_valid_product_lot();
            });
            var lines = order.get_orderlines();
            var orderLines = [];
            var length = order.orderlines.length;

            var client = self.pos.get_client();


            orderLines.push(client);
            for (var i=0;i<length;i++){
                    orderLines.push(lines[i].export_as_JSON());
            }

            if (client == null){
                alert("Please select customer");
            }
            else if(length === 0){
                alert("No product selected !");
            }
            else{
//                self.gui.show_screen('payment');
                var saleOrderModel = new Model('sale.order');
                return saleOrderModel.call('create_from_ui',
                    [_.map(orderLines, function (order) {
                        return order;
                    })]
                ).then(function (order_id) {

                    if (order_id == false){
                        alert("sale order is not created");
                    }
                    else{
                        if(!has_valid_product_lot){
                            self.gui.show_popup('confirm',{
                                'title': _t('Empty Serial/Lot Number'),
                                'body':  _t('One or more product(s) required serial/lot number.'),
                                confirm: function(){
                                    self.gui.show_screen('payment');
                                },
                            });
                        }else{
//                        if (order.is_to_invoice()) {
                            self.chrome.do_action('ping_custom_ui.sale_report_invoice',{additional_context:{
                                active_ids:[order_id],
                            }}).done(function () {
                                invoiced.resolve();
                                done.resolve();
                            });
//                        }
                        self.pos.get_order().finalize();
                        }
                    }
                });
            }
        });
//        this.$('.set-customer').click(function(){
//            self.gui.show_screen('clientlist');
//        });
    }
});

//var PaymentScreenWidget = screens.PaymentScreenWidget.include({
//    renderElement: function() {
//        var self = this;
//        this._super();
//
//        this.$('.next_order').click(function(){
//            self.validate_orders();
//        });
//    },
//
//    validate_orders: function(force_validation){
//        var self = this;
//        var invoiced = new $.Deferred();
//        var done = new $.Deferred(); // holds the mutex
//
//        var order = self.pos.get_order();
//        var has_valid_product_lot = _.every(order.orderlines.models, function(line){
//            return line.has_valid_product_lot();
//        });
//        var lines = order.get_orderlines();
//        var orderLines = [];
//        var length = order.orderlines.length;
//        var client = this.pos.get_client();
//        if (client == null){
//            alert("Please select customer");
//            return
//        }
//        orderLines.push(client);
//        for (var i=0;i<length;i++){
//                orderLines.push(lines[i].export_as_JSON());
//        }
//
//
//        var saleOrderModel = new Model('sale.order');
//        return saleOrderModel.call('create_from_ui',
//            [_.map(orderLines, function (order) {
//                return order;
//            })]
//        ).then(function (order_id) {
//
//            if (order_id == false){
//                alert("sale order is not created");
//            }
//            else{
//                if(!has_valid_product_lot){
//                    self.gui.show_popup('confirm',{
//                        'title': _t('Empty Serial/Lot Number'),
//                        'body':  _t('One or more product(s) required serial/lot number.'),
//                        confirm: function(){
//                            self.gui.show_screen('payment');
//                        },
//                    });
//                }else{
//                if (order.is_to_invoice()) {
//                    self.chrome.do_action('ping_custom_ui.sale_report_invoice',{additional_context:{
//                        active_ids:[order_id],
//                    }}).done(function () {
//                        invoiced.resolve();
//                        done.resolve();
//                    });
//                }
//                self.pos.get_order().finalize();
//                }
//            }
//        });
//    },
//
//});

var ClientListScreenWidget = screens.ClientListScreenWidget.include({
    save_client_details: function(partner) {
        var self = this;

        var fields = {};
        this.$('.client-details-contents .detail').each(function(idx,el){
            fields[el.name] = el.value || false;
        });

        if (!fields.name) {
            this.gui.show_popup('error',_t('A Customer Name Is Required'));
            return;
        }

        if (!fields.phone) {
            this.gui.show_popup('error',_t('A Customer Phone Is Required'));
            return;
        }

        if (this.uploaded_picture) {
            fields.image = this.uploaded_picture;
        }

        fields.id           = partner.id || false;
        fields.country_id   = fields.country_id || false;

        var contents = this.$(".client-details-contents");
        contents.off("click", ".button.save");

        new Model('res.partner').call('create_from_ui',[fields]).then(function(partner_id){
            self.saved_client_details(partner_id);
        },function(err,event){
            event.preventDefault();
            var error_body = _t('Your Internet connection is probably down.');
            if (err.data) {
                var except = err.data;
                error_body = except.arguments && except.arguments[0] || except.message || error_body;
            }
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Save Changes'),
                'body': error_body,
            });
            contents.on('click','.button.save',function(){ self.save_client_details(partner); });
        });
    },

});


return {
    ActionpadWidget: ActionpadWidget,
//    PaymentScreenWidget: PaymentScreenWidget,
    ClientListScreenWidget: ClientListScreenWidget,
};

});
