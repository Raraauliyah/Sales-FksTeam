from odoo import models,fields,api,_
from datetime import date
from odoo.exceptions import ValidationError, UserError


class SourceSequence(models.Model):
    _name = 'source.sequence'
    _rec_name = 'name'

    # name = fields.Char(string='Source Sequence', required=True, copy=False, readonly=True, index=True,
    #                    ondelete='cascade', )

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code(
    #             'source.sequence') or _('New')
    #         vals['sequence'] = vals['name']
    #     return super(SourceSequence,self).create(vals)

    name = fields.Char(
        string='Source Sequence',
        required=True,
        copy=False,
        # readonly=True,
        # index=True,
        # ondelete='cascade',
        # default=lambda self: _('New'),
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique.')
    ]

    @api.multi
    def unlink(self):
        raise UserError(_("This record can not be deleted!"))

    @api.model
    def create(self, vals):
        # if vals.get('name', _('New')) == _('New'):
        #     vals['name'] = self.env['ir.sequence'].next_by_code(
        #         'source.sequence') or _('New')
        #     vals['sequence'] = vals['name']
        res = super(SourceSequence,self).create(vals)
        self.create_sequence_from_source(vals['name'])
        return res

    @api.multi
    def create_sequence_from_source(self, name):
        ir_seq = self.env['ir.sequence']
        vals = {}

        vals['name'] = 'Sale Order: ' + name
        # vals['code'] = 'sale.order'
        vals['prefix'] = name
        vals['padding'] = 3
        return ir_seq.create(vals)

    

class SourceSequencegeneration(models.TransientModel):
    _name = 'source.sequence.gen'

    prefix = fields.Char('Prefix',default='',required=True)
    from_seq = fields.Integer('From Sequence',required=True, digits=(16, 4))
    to_seq = fields.Integer('To Sequence',required=True, digits=(16, 4))

    @api.onchange('from_seq','to_seq')
    def on_change_from_to_seq(self):
        if self.from_seq and self.to_seq:
            if self.to_seq<self.from_seq:
                raise ValidationError(_('To sequence should be greater than from sequence'))

    @api.multi
    def generate_sequence(self):
        if self.from_seq and self.to_seq:
            seq_length = self.to_seq - self.from_seq
            for i in range(0,seq_length+1):
                if i<9:
                    self.env['source.sequence'].create({
                        'name':self.prefix+'000'+str(self.from_seq+i)
                    })
                if i>=9:
                    self.env['source.sequence'].create({
                        'name': self.prefix + '00' + str(self.from_seq + i)
                    })