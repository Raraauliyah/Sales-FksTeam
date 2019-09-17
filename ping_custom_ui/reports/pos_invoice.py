# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class PosInvoiceReport(models.AbstractModel):
    _name = 'report.point_of_sale.sale_report_invoice'

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        PosOrder = self.env['sale.order']
        print("1111111111ids_to_printids_to_print",docids)

        return Report.sudo().render('sale.report_saleorder', {'docs': self.env['sale.order'].sudo().browse(docids)})
