from odoo import models,fields, api
from datetime import date, datetime, timedelta

class WorkingSO(models.Model):
    _name = 'working.so'

    state=fields.Selection([
        ('pending','Pending'),
        ('paused','Paused'),
        ('progress','Progress'),
        ('completed','Completed')
    ],default='pending')
    so_id = fields.Many2one('sale.order',string='Sale Order')

    duration = fields.Float(
        'Real Duration', compute='_compute_duration',
        readonly=True, store=True)
    duration_unit = fields.Float(
        'Duration Per Unit', compute='_compute_duration',
        readonly=True, store=True)

    operator_id = fields.Many2one('res.users',domain=[('operator', '=', True)],string='Operator')

    @api.one
    @api.depends('so_id')
    def _compute_duration(self):
        # self.duration = sum(self.env.user.working_schedule_ids.mapped('duration'))
        self.duration_unit = 0  # rounding 2 because it is a time

    working_so_line_ids = fields.One2many('working.so.line','so_id',string='Working SO')

    @api.multi
    def start_section(self):
        if self.state =='pending':
            self.state ='progress'
        if self.state == 'paused':
            self.state ='progress'
        self.env['working.so.line'].create({
            'workin_so_id':self.id,
            'start_time':datetime.today(),
        })
    @api.multi
    def pause_section(self):
        if self.state == 'progress':
            self.state = 'paused'
        working_so_lines = self.env['working.so.line'].search([])
        working_so_lines.sorted(key=lambda r: r.start_time)
        if working_so_lines:
            working_so_lines[-1].update({'end_time':datetime.today()})

    @api.multi
    def complete_section(self):
        self.state = 'completed'

class WorkingSOLine(models.Model):
    _name = 'working.so.line'

    so_id = fields.Many2one('sale.order')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    duration = fields.Float('Duration',compute='_compute_duration', store=True)
    operator_id = fields.Many2one('res.users',string='Operator', default=lambda self: self.env.uid)

    @api.depends('start_time','end_time')
    def _compute_duration(self):
        for record in self:
            if record.end_time:
                diff = fields.Datetime.from_string(record.end_time) - fields.Datetime.from_string(record.start_time)
                record.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                record.duration = 0.0
            # Old Code
            # if record.start_time and record.end_time:
            #     start_time = datetime.strptime(record.start_time, "%Y-%m-%d %H:%M:%S")
            #     end_time = datetime.strptime(record.end_time, "%Y-%m-%d %H:%M:%S")
            #     print "(end_time - start_time)",(end_time - start_time), type((end_time - start_time))
            #     record.duration = (end_time - start_time)