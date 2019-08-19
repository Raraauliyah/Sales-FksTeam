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


        partner_id = partner_obj.search([('name','=','pos customer')],limit=1)
        if not partner_id:
            partner_id = partner_obj.create({'name':'pos customer'})



        values.update({
            'partner_id':partner_id.id,
            'date_order': datetime.now(),

        })
        orderline = []
        for line in lines:
            orderline.append((0,0,{
                'product_id': line.get('product_id'),
                'price_unit': line.get('price_unit'),
                'product_uom_qty': line.get('qty'),
            }))

        values.update({
            'order_line': orderline,
        })
        if values:
            sale_order_id = self.create(values)
        print("sale order>>>>>>>>>.",sale_order_id)
        return sale_order_id.id