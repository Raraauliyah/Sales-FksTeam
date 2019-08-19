# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cancel_counts = fields.Integer()

    @api.onchange('trust')
    def on_change_trust(self):
        if self.trust and self.trust in ['normal', 'good']:
            self.write({'cancel_counts':0})