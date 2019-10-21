# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class WizardCreateMO(models.Model):
	_name = 'wizard.create.mo'

	qty_onhand = fields.Float(string="QTY On Hand")
	outgoing_qty = fields.Float(string="Outgoing Qty")
	forecasted_qty = fields.Float(string="Forecasted Qty")
	has_bom = fields.Boolean(string="Has Bom")
	qty_to_mo = fields.Integer(string="Qty to Manufacture")
	total_qty = fields.Float(string="Qty", compute='_compute_forecast')

	@api.model
	def default_get(self, fields):
		rec = super(WizardCreateMO, self).default_get(fields)
		if self._context.get('active_id'):
			active_product = self.env['product.template'].browse(self._context.get('active_id'))
			if active_product.bom_count > 0:
				rec.update({'has_bom': True})
			rec.update({'forecasted_qty': active_product.virtual_available, 
						'outgoing_qty' : active_product.outgoing_qty,
						'qty_onhand':active_product.qty_available,
						})
			return rec

	@api.depends('qty_to_mo')
	def _compute_forecast(self):
		for rec in self:
			rec.total_qty =  rec.forecasted_qty + rec.qty_to_mo
			

	@api.multi
	def confirm_button(self):
		if self._context.get('active_id'):
			mo_id = self.env['product.template'].browse(self._context.get('active_id'))
			if self.has_bom:
				mo_obj = self.env['mrp.production']
				for bom in mo_id.bom_ids:
					for bom_line in bom.bom_line_ids:
						if bom_line.product_id.bom_ids:
							for bbm in bom_line.product_id.bom_ids:
								# if len(bbm) >= 1:
								# for bom_bom in bom_line.product_id.bom_ids:
								bom_mo = mo_obj.create({'product_id': bom_line.product_id.id,
														'product_qty': bom_line.product_qty * self.qty_to_mo,
														'bom_id': bbm.id,
														'product_uom_id': bom_line.product_uom_id.id}) 
					mo = mo_obj.create({'product_id': mo_id.product_variant_id.id, 
										'product_qty': self.qty_to_mo,
										'bom_id': bom.id, 
										'date_planned_start':fields.datetime.now(),
										'product_uom_id': mo_id.uom_id.id})
				for rec in mo_id:
					rec.update({
						'so_virtual_available' : self.total_qty
						})	
			else:
				raise ValidationError(_("Product doesn't have BoM!"))

			if self.forecasted_qty > 0:
				raise ValidationError(_("You can not create Manufacturing Order reason Forecast Qty is positive!"))