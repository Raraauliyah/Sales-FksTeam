# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    so_virtual_available = fields.Float(string="Virtual Available")

    def _compute_quantities_dict(self):
        # TDE FIXME: why not using directly the function fields ?
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        context = self._context.get('virtual_available')
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            if template.so_virtual_available:
                for p in template.product_variant_ids:
                    qty_available += variants_available[p.id]["qty_available"]
                    virtual_available += template.so_virtual_available
                    incoming_qty += variants_available[p.id]["incoming_qty"]
                    outgoing_qty += variants_available[p.id]["outgoing_qty"]
            else:
                for p in template.product_variant_ids:
                    qty_available += variants_available[p.id]["qty_available"]
                    virtual_available += variants_available[p.id]["virtual_available"]
                    incoming_qty += variants_available[p.id]["incoming_qty"]
                    outgoing_qty += variants_available[p.id]["outgoing_qty"]

            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
            }
        return prod_available

    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.qty_available = res[template.id]['qty_available']
            template.virtual_available = res[template.id]['virtual_available']
            template.incoming_qty = res[template.id]['incoming_qty']
            template.outgoing_qty = res[template.id]['outgoing_qty']


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        for rec in res:
            for line in rec.order_line: 
                product = self.env['product.product'].search([('id', '=', line.product_id.id)])
                product_template = self.env['product.template'].search([('id', '=', line.product_id.product_tmpl_id.id)])
                forecasted_qty = product.qty_available - line.product_uom_qty
                product_template.so_virtual_available = forecasted_qty
        return res

    

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for rec in self:
            for line in rec.order_line:
                product = self.env['product.product'].search([('id', '=', line.product_id.id)])
                product_template = self.env['product.template'].search([('id', '=', line.product_id.product_tmpl_id.id)])
                product_template.so_virtual_available = 0
        return res