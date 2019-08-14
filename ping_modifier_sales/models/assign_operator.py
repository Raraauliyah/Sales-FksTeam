from odoo import models,fields,api,_
from datetime import date,datetime,timedelta
import random, time, pytz

from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AssignOperator(models.Model):
    _name = 'assign.operator'

    operator_bool = fields.Boolean('operator Bool',default=False)
    operator_id = fields.Many2one('res.users',domain=[('active', '=', True), ('operator', '=', True)])


    @api.onchange('operator_bool')
    def on_change_operator(self):
        operator_user = self.find_operator()
        if operator_user:
            return {'domain':{'operator_id': [('id', 'in',operator_user )]}}


    @api.multi
    def domain_assign(self):
        operator_user = self.find_operator()
        if operator_user:
            return {'domain':{'operator_id': [('id', 'in',operator_user )]}}

    @api.multi
    def assign_operator(self):
        self.domain_assign()
        sale_order = self._context.get('active_ids')
        for order in sale_order:
            order_rec = self.env['sale.order'].search([('id','=',order)])
            order_rec.update({'operator_id':self.operator_id.id})
            if order_rec.state_ws=='progress':
                working_so_lines = self.env['working.so.line'].search([])
                working_so_lines.sorted(key=lambda r: r.start_time)
                if working_so_lines:
                    working_so=working_so_lines[-1]
                    if not working_so.end_time:
                        working_so.update({'operator_id':self.operator_id.id})


    # def find_operator(self):
    #     operator_users = self.env['res.users'].search([('active', '=', True), ('operator', '=', True)])
    #     if operator_users:
    #         operator_user = []
    #         # schedule_line_rec = False
    #         for user in operator_users:
    #             for schedule_line in user.working_schedule_ids:
    #                 if schedule_line.status == 'active':
    #                     start_time = datetime.strptime(schedule_line.start_date, "%Y-%m-%d %H:%M:%S")
    #                     end_time = datetime.strptime(schedule_line.end_date, "%Y-%m-%d %H:%M:%S")
    #                     if start_time <= datetime.now() <= end_time:
    #                         days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    #                         dayNumber = datetime.now().weekday()
    #                         if days[dayNumber] == str(schedule_line.day):
    #                             operator_user.append(user.id)
    #         return operator_user

    @api.multi
    def find_operator(self):
        for user in self.env['res.users'].search([('active','=',True),('operator','=',True)]):
                user.compute_count_confirmed_orders_today()

        operators = self.env['res.users'].search([('active','=',True),('operator','=',True)])
        active_operators = []
        for operator in operators:
            if operator.working_schedule_ids:
                if operator.tz:
                    op_tz = pytz.timezone(str(operator.tz))
                else:
                    op_tz = pytz.timezone('UTC')
                    
                for ws in operator.working_schedule_ids:
                    start_date = datetime.strptime(ws.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    end_date = datetime.strptime(ws.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    
                    # dirty way of conversion from float to timestamp
                    work_from = datetime.strptime('{0:02.0f}:{1:02.0f}'.format(*divmod(float(ws.time_scedule_from) * 60, 60)), '%H:%M').time()
                    work_to = datetime.strptime('{0:02.0f}:{1:02.0f}'.format(*divmod(float(ws.time_scedule_to) * 60, 60)), '%H:%M').time()
                    
                    now = datetime.now(op_tz).time() 
                    day = ws.day
                    status = ws.status

                    if start_date <= datetime.now() and datetime.now() <= end_date and day == datetime.now(op_tz).strftime('%A').lower()\
                        and work_from <= now and now <= work_to and status=='active':
                        active_operators.append(ws.user_id.id)
        return active_operators
