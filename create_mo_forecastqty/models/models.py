# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    store_virtual_qty = fields.Float(relate='virtual_available', string="Forecasted Quontity",
    	store=True, compute='_compute_quantities',digits=dp.get_precision('Product Unit of Measure'))
    store_incoming_qty = fields.Float(
        'Incoming',store=True, compute='_compute_quantities',
        digits=dp.get_precision('Product Unit of Measure'))
    store_outgoing_qty = fields.Float(
        'Outgoing',store=True, compute='_compute_quantities',
        digits=dp.get_precision('Product Unit of Measure'))

    def _compute_quantities(self):
    	result = super(ProductTemplate, self)._compute_quantities()
        res = self._compute_quantities_dict()
        for template in self:
            template.write({'store_incoming_qty':res[template.id]['incoming_qty'],
            			    'store_virtual_qty':res[template.id]['virtual_available'],
            			    'store_outgoing_qty': res[template.id]['outgoing_qty']})

        return result

    # def _compute_quantities_dict(self):
    #     # TDE FIXME: why not using directly the function fields ?
    #     variants_available = self.mapped('product_variant_ids')._product_available()
    #     prod_available = {}
    #     for template in self:
    #         qty_available = 0
    #         virtual_available = 0
    #         incoming_qty = 0
    #         outgoing_qty = 0
    #         for p in template.product_variant_ids:
    #             qty_available += variants_available[p.id]["qty_available"]
    #             virtual_available += variants_available[p.id]["virtual_available"]
    #             incoming_qty += variants_available[p.id]["incoming_qty"]
    #             outgoing_qty += variants_available[p.id]["outgoing_qty"]
    #         prod_available[template.id] = {
    #             "qty_available": qty_available,
    #             "virtual_available": virtual_available,
    #             "incoming_qty": incoming_qty,
    #             "outgoing_qty": outgoing_qty,
                
    #             "store_virtual_qty": virtual_available,
    #             "store_incoming_qty": incoming_qty,
    #             "store_outgoing_qty": outgoing_qty,
    #         }
    #     return prod_available