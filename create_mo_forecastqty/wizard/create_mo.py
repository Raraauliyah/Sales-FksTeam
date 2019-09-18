# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class WizardCreateMO(models.Model):
	_name = 'wizard.create.mo'

	qty_onhand = fields.Float(string="QTY On Hand")
	outgoing_qty = fields.Float(string="Outgoing Qty")
	forecasted_qty = fields.Float(string="Forecasted Qty")
	has_bom = fields.Boolean(string="Has Bom")

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


	# @api.multi
	# def confirm_button(self):
	# 	if self._context.get('active_id'):
	# 		mo_id = self.env['product.template'].browse(self._context.get('active_id'))
	# 		if self.has_bom:
	# 			mo_obj = self.env['mrp.production']
	# 			for bom in mo_id.bom_ids:
	# 				mo = mo_obj.create({'product_id': mo_id.product_variant_id.id, 
	# 					                'product_qty': abs(self.forecasted_qty), 
	# 					                'bom_id': bom.id, 
	# 					                'date_planned_start':fields.datetime.now(),
	# 					                'product_uom_id': mo_id.uom_id.id})
	# 				a = mo_id.write({'virtual_available': abs(self.forecasted_qty)})
	# 		else:
	# 			raise ValidationError(_("Product doesn't have BoM!"))




	@api.multi
	def confirm_button(self):
		if self._context.get('active_id'):
			mo_id = self.env['product.template'].browse(self._context.get('active_id'))
			if self.has_bom:
				mo_obj = self.env['mrp.production']
				for bom in mo_id.bom_ids:
					for bom_line in bom.bom_line_ids:
						if len(bom_line.product_id.bom_ids) >= 1:
							for bom_bom in bom_line.product_id.bom_ids:
								bom_mo = mo_obj.create({'product_id': bom_line.product_id.id,
														'product_qty': bom_line.product_qty * abs(self.forecasted_qty),
														'bom_id': bom_bom.id,
														'product_uom_id': bom_line.product_uom_id.id}) 
					mo = mo_obj.create({'product_id': mo_id.product_variant_id.id, 
						                'product_qty': abs(self.forecasted_qty), 
						                'bom_id': bom.id, 
						                'date_planned_start':fields.datetime.now(),
						                'product_uom_id': mo_id.uom_id.id})

					a = mo_id.write({'virtual_available': abs(self.forecasted_qty)})
			elif self.forecasted_qty > 0:
				raise ValidationError(_("Forecast Qty is positive!"))
			else:
				raise ValidationError(_("Product doesn't have BoM!"))