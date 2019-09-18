odoo.define('pos_create_sale_order.model', function (require) {
"use strict";

var BarcodeParser = require('barcodes.BarcodeParser');
var PosDB = require('point_of_sale.DB');
var devices = require('point_of_sale.devices');
var core = require('web.core');
var models = require('point_of_sale.models');
var Model = require('web.DataModel');
var formats = require('web.formats');
var session = require('web.session');
var time = require('web.time');
var utils = require('web.utils');

var QWeb = core.qweb;
var _t = core._t;
var Mutex = utils.Mutex;
var round_di = utils.round_decimals;
var round_pr = utils.round_precision;
var Backbone = window.Backbone;

var exports = {};

var _super_posmodel = models.PosModel.prototype;

//models.PosModel = models.PosModel.extend({
//    _save_to_server: function (orders, options) {
//        if (!orders || !orders.length) {
//            var result = $.Deferred();
//            result.resolve([]);
//            return result;
//        }
//
//        options = options || {};
//
//        var self = this;
//        var timeout = typeof options.timeout === 'number' ? options.timeout : 7500 * orders.length;
//
//        // Keep the order ids that are about to be sent to the
//        // backend. In between create_from_ui and the success callback
//        // new orders may have been added to it.
//        var order_ids_to_sync = _.pluck(orders, 'id');
//
//        // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
//        // then we want to notify the user that we are waiting on something )
//        var saleOrderModel = new Model('sale.order');
//        return saleOrderModel.call('create_from_ui',
//            [_.map(orders, function (order) {
//                order.to_invoice = options.to_invoice || false;
//                return order;
//            })],
//            undefined,
//            {
//                shadow: !options.to_invoice,
//                timeout: timeout
//            }
//        ).then(function (server_ids) {
//            _.each(order_ids_to_sync, function (order_id) {
//                self.db.remove_order(order_id);
//            });
//            self.set('failed',false);
//            return server_ids;
//        }).fail(function (error, event){
//            if(error.code === 200 ){    // Business Logic Error, not a connection problem
//                //if warning do not need to display traceback!!
//                if (error.data.exception_type == 'warning') {
//                    delete error.data.debug;
//                }
//
//                // Hide error if already shown before ...
//                if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
//                    self.gui.show_popup('error-traceback',{
//                        'title': error.data.message,
//                        'body':  error.data.debug
//                    });
//                }
//                self.set('failed',error)
//            }
//            // prevent an error popup creation by the rpc failure
//            // we want the failure to be silent as we send the orders in the background
//            event.preventDefault();
//            console.error('Failed to send orders:', orders);
//        });
//    },
//});

});