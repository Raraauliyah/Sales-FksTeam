from odoo import models,fields,api,_
from datetime import date

class ClaimPointWizard(models.TransientModel):
    _name = 'claim.point.wiz'


    partner_id = fields.Many2one('res.partner',string='Partner')
    claim_point_id = fields.Many2one('sale.claim.points',string='Claim Points')

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        date_today = date.today()
        if self.partner_id:
            # claim_points= []
            claim_points = self.env['sale.claim.points'].search(
                [('point_pos', '<=', self.partner_id.point_customer), ('start_date', '<=', date_today),
                 ('end_date', '>=', date_today)])
            if claim_points:
                return {'domain': {'claim_point_id': [('id', 'in', claim_points.ids)]}}
            else:
                return {'domain': {'claim_point_id': [('id', 'in', [])]}}

    @api.multi
    def apply(self):
        sale_id = self._context.get('active_id')
        sale_order_line_obj = self.env['sale.order.line']
        sale_order = self.env['sale.order'].search([('id','=',sale_id)])
        sale_order_line_obj.create({'product_id':self.claim_point_id.product_id.id,
                                    'name':'['+self.claim_point_id.product_id.default_code+']'+self.claim_point_id.product_id.name,
                                    'product_uom_qty':self.claim_point_id.qty,
                                    'order_id':sale_order.id,
                                    'is_claim_product':True,
                                    'price_unit':self.claim_point_id.unit_price})
        sale_order.update({'claim_point_id': self.claim_point_id.id})
        # sale_order.partner_id.point_customer -= self.claim_point_id.point_pos