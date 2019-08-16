from datetime import datetime
from odoo import fields,models,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    operator = fields.Boolean('Operator')
    manage_operator = fields.Boolean('Can Manage Operator')

    working_schedule_ids = fields.One2many('working.schedule.line','user_id',string='Working Schedules')
    
    count_confirmed_orders_today = fields.Integer(default=0, readonly=1)

    @api.multi
    def compute_count_confirmed_orders_today(self):
        sobj = self.env['sale.order']
        for rec in self:
            rec.count_confirmed_orders_today = 0
            orders = sobj.search([('operator_id', '=', rec.id), ('state', '=', 'sale'), ('state_ws', '!=', 'completed')])
            for order in orders:
                confirmation_date = order.confirmation_date.split(' ')[0]
                today = datetime.today().strftime('%Y-%m-%d')
                if today == confirmation_date:
                    rec.count_confirmed_orders_today += 1


class WorkingScheduleLine(models.Model):
    _name = 'working.schedule.line'

    day = fields.Selection([
        ('monday','Monday'),
        ('tuesday','Tuesday'),
        ('wednesday','Wednesday'),
        ('thursday','Thursday'),
        ('friday','Friday'),
        ('saturday','Saturday'),
        ('sunday','Sunday')
    ],string='Day')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ])
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    time_scedule_from = fields.Float('Work From')
    time_scedule_to = fields.Float('Work To')
    user_id =fields.Many2one('res.users',string='Users')
    used_operator = fields.Boolean('Used Operator',default=False)


    @api.onchange('start_date','end_date','day','status')
    def on_change_operator_schedule(self):
        self.used_operator=False

