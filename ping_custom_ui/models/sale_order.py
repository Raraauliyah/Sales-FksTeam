from odoo import fields,api,models,_
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create_from_ui(self,lines):

        if not lines:
            return False

        values = {}
        partner_obj = self.env['res.partner']

        orderline = []
        for line in lines:
            if line.get('name'):
                partner_id = partner_obj.search([('name', '=', line.get('name'))], limit=1)
                if not partner_id:
                    partner_id = partner_obj.create({'name': line.get('name')})
                if partner_id:
                    values.update({
                        'partner_id': partner_id.id,
                    })
            else:
                orderline.append((0, 0, {
                'product_id': line.get('product_id'),
                              'price_unit': line.get('price_unit'),
                                            'product_uom_qty': line.get('qty'),
                }))


        values.update({
            'order_line': orderline,
            'date_order':datetime.now(),
        })
        if values:
            sale_order_id = self.create(values)
        print("sale order>>>>>>>>>.",sale_order_id)
        return sale_order_id.id