from odoo import models,fields,api,_
from datetime import date
from odoo.exceptions import ValidationError, UserError


class SourceSequence(models.Model):
    _name = 'source.sequence'
    _rec_name = 'name'

    name = fields.Char(
        string='Source Sequence',
        required=True,
        copy=False,
    )
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Sequence',
        copy=False,
        required=True,
    )
    


    _sql_constraints = [
        ('name_uniq', 'unique (name,sequence_id)', 'Name and sequence must be unique.')
    ]

    @api.multi
    def unlink(self):
        raise UserError(_("This record can not be deleted!"))

    # @api.model
    # def create(self, vals):
    #     res = super(SourceSequence,self).create(vals)
    #     self.create_sequence_from_source(vals['name'])
    #     return res

    # @api.multi
    # def create_sequence_from_source(self, name):
    #     ir_seq = self.env['ir.sequence']
    #     vals = {}

    #     vals['name'] = 'Sale Order: ' + name
    #     # vals['code'] = 'sale.order'
    #     vals['prefix'] = name
    #     vals['padding'] = 3
    #     return ir_seq.create(vals)