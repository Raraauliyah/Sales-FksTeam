from odoo import models,api,fields,_
from odoo.exceptions import ValidationError
from datetime import datetime


class SaleTags(models.Model):
    _name = 'sale.tags'
    _rec_name= 'name'

    sale_id = fields.Many2one('sale.order',string="Sale")
    name = fields.Char(related='sale_id.name',string='Name')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.cbm')
    def _total_cbm(self):
        """
                Compute the total amounts of the CBM.
                """
        for order in self:
            total_cbm = 0.0
            for line in order.order_line:
                total_cbm += line.cbm
            order.update({
                'total_cbm': total_cbm,
            })

    stuffing_date = fields.Date(string="Stuffing Date")
    etd = fields.Date(string="ETD")
    eta = fields.Date(string="ETA")
    port_destination = fields.Char(string="Port Destination")
    customer_po = fields.Char(string="Customer PO No.")
    deadline_date = fields.Char(string="Deadline Date")
    tag_ids = fields.Many2many('sale.tags','sale_id',string="Tags")
    total_cbm = fields.Float('Total CBM',compute="_total_cbm")

    @api.multi
    def action_confirm(self):
        bom_obj = self.env['mrp.bom']
        mp_obj = self.env['mrp.plan']
        mrp_production_obj = self.env['mrp.production']
        for order in self.order_line:
            bom_id = bom_obj.sudo().search([('product_tmpl_id','=',order.product_id.product_tmpl_id.id)],limit=1)

            if not bom_id:
                raise ValidationError(('Bill of Material not exist for %s') % order.product_id.name)

            if bom_id and not bom_id.bom_line_ids:
                raise ValidationError(('Bill of Material not exist for %s') % order.product_id.name)

            if order.qty_div_carton and order.product_uom_qty:
                new_value = order.product_uom_qty % order.qty_div_carton
                if new_value != 0.0:
                    raise ValidationError(('Quantity must multiply from Qty/Carton'))
            mp_id = mp_obj.sudo().create({
                'name': self.name,
                'date': datetime.now(),
                'sale_id': self.id,
            })

            mrp_id = mrp_production_obj.create({
                'product_id': order.product_id.id,
                'mrp_plan_id': mp_id.id,
                'product_qty': order.product_uom_qty,
                'product_uom_id': order.product_uom.id,
            })
        return super(SaleOrder, self).action_confirm()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pcs = fields.Float(string='Price/1000 Pcs')
    qty_div_carton = fields.Float(related="product_id.qty_div_carton",string="Qty/Carton")
    sleeve_qty_carton = fields.Float(related="product_id.sleeve_qty_carton",string="Sleeve/Carton")
    sleeve_type = fields.Selection(selection=[('paper_sleeve', 'Paper Sleeve'), ('plastic_sleeve', 'Plastic Sleeve')],related="product_id.sleeve_type",
                                   string="Sleeve Type")
    case_qty = fields.Float(string='Case Qty')
    nett = fields.Float(string='Nett')
    gross = fields.Float(string='Gross')
    cbm = fields.Float(string='CBM')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

        case_qty = 0.0
        if self.qty_div_carton:
            if self.product_uom_qty:
                case_qty =  (self.product_uom_qty/self.qty_div_carton)
            else:
                case_qty = (vals.get('product_uom_qty')/self.qty_div_carton)

            vals['case_qty'] = case_qty
        cbm = 0.0
        cbm = ((self.product_id.case_dim_length * self.product_id.case_dim_width * self.product_id.case_dim_height) * case_qty)

        if vals.get('product_uom_qty') or self.product_uom_qty:
            nett = 0.0
            gross = 0.0
            if self.product_uom_qty:
                pcs =  ((self.product_uom_qty/1000)* vals['price_unit'])
                if self.product_id.product_weight:
                    nett = self.product_id.product_weight * self.product_uom_qty
                # if self.product_id.case_weight:
                gross = (self.product_id.case_weight * case_qty)+(self.product_id.product_weight * self.product_uom_qty)
            else:
                pcs = ((vals.get('product_uom_qty') / 1000) * vals['price_unit'])
                if self.product_id.product_weight:
                    nett = self.product_id.product_weight * vals.get('product_uom_qty')
                # if self.product_id.case_weight:
                gross = (self.product_id.case_weight * case_qty)+(self.product_id.product_weight * vals.get('product_uom_qty'))
            vals['pcs'] = pcs
            vals['nett'] = nett
            vals['gross'] = gross
            vals['cbm'] = cbm


        self.update(vals)

        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            self.pcs = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)
            #custom code
            if self.product_uom_qty:
                pcs =  ((self.product_uom_qty/1000)* self.price_unit)
                self.pcs = pcs
                nett = 0.0
                if self.product_id.product_weight:
                    nett = self.product_id.product_weight * self.product_uom_qty
                self.nett = nett
                # if self.product_id.case_weight:
                gross = (self.product_id.case_weight * self.case_qty)+(self.product_id.product_weight * self.product_uom_qty)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)

            # custom code
            if line.product_uom_qty:
                pcs = ((line.product_uom_qty / 1000) * line.price_unit)
                line['pcs'] = pcs
            case_qty = 0.0
            if line.qty_div_carton:
                if line.product_uom_qty:
                    case_qty = (line.product_uom_qty / line.qty_div_carton)
                    line['case_qty'] = case_qty

            line['cbm'] = ((line.product_id.case_dim_length * line.product_id.case_dim_width * line.product_id.case_dim_height) * case_qty)

            # if line.product_id.case_weight:
            gross = (line.product_id.case_weight * line.case_qty) + (line.product_id.product_weight * line.product_uom_qty)
            line['gross'] = gross
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })






