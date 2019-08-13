odoo.define('mrp.mrp_state', function (require) {
"use strict";

var core = require('web.core');
var common = require('web.form_common');
var Model = require('web.Model');
var time = require('web.time');


var SOTimeCounter = common.AbstractField.extend(common.ReinitializeFieldMixin, {
    start: function() {
        this._super();
        var self = this;
        this.field_manager.on("view_content_has_changed", this, function () {
            self.render_value();
        });
    },
    start_time_counter: function(){
        var self = this;
        clearTimeout(this.timer);
        if (this.field_manager.datarecord.is_user_working) {
            this.duration += 1000;
            this.timer = setTimeout(function() {
                self.start_time_counter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }
        this.$el.html($('<span>' + moment.utc(this.duration).format("HH:mm:ss") + '</span>'));
    },
    render_value: function() {
        this._super.apply(this, arguments);
        var self = this;
        this.duration;
        var working_so_domain = [['so_id', '=', this.field_manager.datarecord.id], ['operator_id', '=', self.session.uid]];
        new Model('working.so.line').call('search_read', [working_so_domain, []]).then(function(result) {
            if (self.get("effective_readonly")) {
                self.$el.removeClass('o_form_field_empty');
                var current_date = new Date();
                self.duration = 0;
                _.each(result, function(data) {
                    self.duration += data.end_time ? self.get_date_difference(data.start_time, data.end_time) : self.get_date_difference(time.auto_str_to_date(data.start_time), current_date);
                });
                self.start_time_counter();
            }
        });
    },
    get_date_difference: function(start_time, end_time) {
        var difference = moment(end_time).diff(moment(start_time));
        return moment.duration(difference);
    },
});

core.form_widget_registry.add('sale_order_time_counter', SOTimeCounter);
});
