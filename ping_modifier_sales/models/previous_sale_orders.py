from odoo import models,fields,api,_
from datetime import date,datetime,timedelta
import random, time, pytz

from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PreviousSaleOrder(models.Model):
    _name = 'previous.sale.orders'

    sale_order_id = fields.Many2one('sale.order',string='Sale Order')

    @api.multi
    def approve_sale_order(self):
        sale_order_id =self.env['sale.order'].search([('id','in',self._context.get('active_ids'))],limit=1)
        if sale_order_id:
            sale_order_id.update({'previous_orders':False})
            sale_order_id.action_confirm()