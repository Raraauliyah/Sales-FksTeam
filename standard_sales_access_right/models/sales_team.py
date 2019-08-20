# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.addons.base.res.res_users import get_selection_groups

class ResUsers(models.Model):
	_inherit = 'res.users'

	
	@api.multi
	def write(self, vals):
		group_obj = self.env['res.groups']
		groups_by_application = group_obj.get_groups_by_application()
		def find_implied(group):
			# Recusively find all implied groups
			res = []
			for implied in group.implied_ids:
				res.append(implied)
				for item in implied:
					res += find_implied(item)
			return res

		def update_implied(implied):
			res = {}
			for item in implied:
				for category, ttype, groups in groups_by_application:  # pylint: disable=W0612
					if ttype == 'boolean' and \
					   item.id in [g.id for g in groups]:
						res.update({'in_group_%s' % item.id: False})
			return res

		to_upd = {}
		for key, value in vals.items():  # pylint: disable=W0612
			if key.startswith('in_group_'):
				groups = self.get_selection_groups_1(key)
				for group in group_obj.browse(groups):
					implied = find_implied(group)
					to_upd.update(update_implied(implied))
		vals.update(to_upd)
		return super(ResUsers, self).write(vals)
	
	def get_selection_groups_1(self,key):
		local = map(int, key[9:].split('_'))
		return local

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	is_direct_state= fields.Selection([
		('default', 'default'),
		('sale', 'sale'),
		('direct', 'direct')], string="Tracking", default='default')
	is_direct_sale = fields.Boolean(string='Is Direct Sale', default=False)
	is_sale_order = fields.Boolean(string='Is Sale Order', default=False)

	@api.multi
	def write(self, vals):
		res = super(SaleOrder, self).write(vals)
		for record in self:
			if record.user_has_groups('standard_sales_access_right.group_sales_team_mngr') == False \
					and record.user_has_groups('sales_team.group_sale_manager') == False:
				if record.user_has_groups('standard_sales_access_right.group_sales_team_docs') \
						or record.user_has_groups('sales_team.group_sale_salesman_all_leads') \
						or record.user_has_groups('sales_team.group_sale_salesman'):
					if record.user_id.id != record.env.user.id:
						raise ValidationError(_(
								"The requested operation cannot be completed due to security restrictions. Please contact your system administrator. "))
		return res

	# @api.multi
	# @api.depends('team_id', 'team_id.member_ids')
	# def compute_is_direct_sale(self):
	# 	print"compute_is_direct_sale "
	# 	for record in self:
	# 		if record.user_id.id != self.env.user.id and record.team_id.member_ids:
	# 			for team in record.team_id.member_ids:
	# 				if team.id == self.env.user.id:
	# 					record.is_direct_state = 'direct'
	# 					record.is_direct_sale = True
	#
	# @api.multi
	# def compute_is_order_sale(self):
	# 	for record in self:
	# 		if self.user_has_groups('standard_sales_access_right.group_sales_team_docs'):
	# 			if record.user_id.id == self.env.user.id:
	# 				record.is_direct_state = 'sale'
	# 				record.is_sale_order = True

	@api.model
	def search(self, args, offset=0, limit=None, order=None, context=None, count=False):
		if not args:
			args = []
		sale_team_id = self.env.user.sale_team_id
		user = self.env.user
		# if self.env.user.id != 1:
		if self.user_has_groups('standard_sales_access_right.group_sales_team_mngr'):
			print"sales team group ",self.user_has_groups('standard_sales_access_right.group_sales_team_mngr')
			# args = []
			args += [('user_id', 'in', sale_team_id.member_ids.ids), ('team_id', '=', sale_team_id.id)]
			# if self.is_direct_sale:
			# 	args += [('user_id','in',sale_team_id.member_ids.ids),('team_id','=',sale_team_id.id)]
			# if self.is_sale_order:
			# 	args += [('user_id', 'in', self.env.user.id), ('team_id', '=', sale_team_id.id)]
		elif self.user_has_groups('standard_sales_access_right.group_sales_team_docs'):
			# args = []
			args += [('user_id','in',sale_team_id.member_ids.ids),('team_id','=',sale_team_id.id)]
		return super(SaleOrder,self).search(args, offset, limit, order, count=count)






class CrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.multi
	def write(self, vals):
		res = super(CrmLead, self).write(vals)
		for record in self:
			# if Sales: All Docs  or Sales: Team Docs is enable need to hide to show warning
			if record.user_has_groups('standard_sales_access_right.group_sales_team_mngr') == False \
					and record.user_has_groups('sales_team.group_sale_manager') == False:
				if record.user_has_groups('standard_sales_access_right.group_sales_team_docs') \
						or record.user_has_groups('sales_team.group_sale_salesman_all_leads') \
						or record.user_has_groups('sales_team.group_sale_salesman'):
					if record.user_id.id != record.env.user.id:
						raise ValidationError(_(
							"The requested operation cannot be completed due to security restrictions. Please contact your system administrator. "
						))
		return res

	@api.model
	def search(self, args, offset=0, limit=None, order=None, context=None, count=False):
		if not args:
			args = []
		sale_team_id = self.env.user.sale_team_id
		user = self.env.user
		# if self.env.user.id != 1:
		if self.user_has_groups('standard_sales_access_right.group_sales_team_mngr'):
			# args = []
			args += [('user_id','in',sale_team_id.member_ids.ids),('team_id','=',sale_team_id.id)]
		elif self.user_has_groups('standard_sales_access_right.group_sales_team_docs'):
			# args = []
			args += [('user_id','in',sale_team_id.member_ids.ids),('team_id','=',sale_team_id.id)]
		return super(CrmLead,self).search(args, offset, limit, order, count=count)