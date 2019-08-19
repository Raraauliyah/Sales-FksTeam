odoo.define('pos_create_sale_order.pos', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var PopupWidget = require('point_of_sale.popups');
var Model = require('web.DataModel');


var QWeb = core.qweb;

	var CreateSaleOrder = screens.ActionButtonWidget.extend({
        template: 'CreateSaleOrder',
         events: {
            "click *[rel='do_action']": "doActionClickHandler",
        },

        init: function(parent, context) {
        this._super(parent);
        this.action_manager = this.findAncestor(function(ancestor){ return ancestor instanceof ActionManager });
        },

        button_click: function(){
        	var self = this;
        	var order = this.pos.get_order();
	        var lines = order.get_orderlines();
	        var orderLines = [];
	        var length = order.orderlines.length;
	        for (var i=0;i<length;i++){
	        		orderLines.push(lines[i].export_as_JSON());
	        }
	        if(orderLines.length === 0){
	        	alert("No product selected !");
	        }
	        else{
	            //create new saleorder
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
                        // order is created then remove orderlines from pos
                        order.remove_orderline(lines);
                        return window.open('/web?debug=1#id='+order_id+'&view_type=form&model=sale.order','_self');
                    }
                });
	        }
        },
    });
    screens.define_action_button({
        'name': 'create_sale_order',
        'widget': CreateSaleOrder,
    });


});
