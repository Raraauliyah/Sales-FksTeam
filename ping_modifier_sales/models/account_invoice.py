from odoo import models,fields,api,_
from datetime import date

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    is_claim_product = fields.Boolean('Is Claim Product',default=False)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    claim_point_id = fields.Many2one('sale.claim.points',string='Claim Points')