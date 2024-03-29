from odoo import models,fields,api,_
from datetime import date,datetime,timedelta
import random, time, pytz

from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    operator_id = fields.Many2one(
        comodel_name='res.users',
        domain=[('operator', '=', True)],
        string='Operator',
        # default=lambda self: self.env.uid
        default=False,
        copy=False,
    )

    working_so_ids = fields.One2many('working.so','so_id',string='Working SO')

    source_seq_id = fields.Many2one(
        'source.sequence',
        string='Source',
        store=True,
        copy=False,
    )
    working_schedule_count = fields.Integer(string='Schedule Count', compute='_compute_schedule_count')

    state_ws = fields.Selection([
        ('pending', 'Pending'),
        ('paused', 'Paused'),
        ('progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='pending',string='Working Status')

    duration = fields.Float(
        'Real Duration', compute='_compute_duration',
        readonly=True, store=True)
    duration_unit = fields.Float(
        'Duration Per Unit', compute='_compute_duration',
        readonly=True, store=True)

    working_so_line_ids = fields.One2many(
        comodel_name='working.so.line',
        inverse_name='so_id',
        string='Working SO')
    is_user_working = fields.Boolean(
        string='Is Current User Working',
        compute='_compute_is_user_working',
    )

    previous_orders = fields.Boolean(
        string='Previous Orders',default=True
    )
    cancel_date = fields.Date(
        string='Cancel Date'
    )

    @api.multi
    def refresh_view(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'target':'main',
        }

    @api.depends('working_so_line_ids')
    def _compute_is_user_working(self):
        """ Checks whether the current user is working """
        for order in self:
            working_so_line_ids = order.working_so_line_ids.filtered(
                lambda line:
                (line.operator_id.id == self.env.user.id) and
                (not line.end_time or line.line_id.line_state_ws in ['partial'])
            )
            print("working_so_line_ids ",working_so_line_ids)
            if working_so_line_ids:
                order.is_user_working = True
            else:
                order.is_user_working = False

    @api.onchange('working_status')
    def onchange_working_status(self):
        if not self.working_status:
            self.write({'working_status':'pending'})

    @api.multi
    @api.depends('working_so_ids')
    def _compute_schedule_count(self):
        for order in self:
            order.working_schedule_count = len(order.working_so_ids)

    # @api.multi
    # def action_view_work_schedule(self):
    #     action = self.env.ref('ping_modifier_sales.action_working_so_view').read()[0]
    #     working_schedule = self.mapped('working_so_ids')
    #     if len(working_schedule) > 1:
    #         action['domain'] = [('id', 'in', working_schedule.ids)]
    #     elif working_schedule:
    #         action['views'] = [(self.env.ref('ping_modifier_sales.view_workin_so').id, 'form')]
    #         action['res_id'] = working_schedule.id
    #     else:
    #         raise Warning(_("No Related Working Schedule Found!!!"))
    #     return action


    # def find_operator(self):
    #     operator_users = self.env['res.users'].search([('active', '=', True), ('operator', '=', True)])
    #     if operator_users:
    #         operator_user = []
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
    #     else:
    #         return False

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
                        active_operators.append(ws.user_id)
        return active_operators


    @api.one
    @api.depends('state_ws', 'working_so_line_ids.duration', 'order_line.line_state_ws')
    def _compute_duration(self):
        self.duration = sum(self.working_so_line_ids.mapped('duration'))
        # Old Code
        # self.duration = sum(self.env.user.working_schedule_ids.mapped('duration'))
        self.duration_unit = 0  # rounding 2 because it is a time

    @api.multi
    def action_assign_operator(self):
        for line in self.order_line:
            if line.line_state_ws and line.line_state_ws == 'progress':
                raise ValidationError(_('You cannot able to Re-assign operator while product still in progress'))
        view = (self.env.ref('ping_modifier_sales.select_operator_form_view')).id
        return {
            'name': 'Assign Operator',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'assign.operator',
            'view_id': view,
            'target': 'new',
            'context':{'default_operator_bool':True},
            'type': 'ir.actions.act_window',
        }



    @api.multi
    def action_cancel(self):
        res = super(SaleOrder,self).action_cancel()
        self.cancel_date = date.today()
        today = date.today()
        before_three_months = (date.today() - timedelta(3*365/12)).isoformat()
        cancelled_so = self.search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'cancel'),
            ('cancel_date', '>', before_three_months),
            ('cancel_date', '<=', today)
        ])
        self.partner_id.update({'cancel_counts': len(cancelled_so)})

        self.partner_id.cancel_counts +=1
        if self.partner_id.cancel_counts >= 5:
            self.partner_id.update({'trust':'bad','cancel_counts':0})
        # if self.partner_id.cancel_counts == -3:
        #     self.partner_id.update({'trust':'good','cancel_counts':0})
        if self.state=='sale':
            self.operator_id.compute_count_confirmed_orders_today()
        return res

    @api.multi
    def action_confirm(self):
        if self.partner_id.trust and self.partner_id.trust == 'bad':
            raise ValidationError(_('Customer is bad debtor, Please contact the Administrator to activate'))
        # if self.partner_id.cancel_counts > 0:
        #     self.partner_id.update({'cancel_counts': -1})
        # elif self.partner_id.cancel_counts <= 0:
        #     count_sale = self.partner_id.cancel_counts - 1
        #     self.partner_id.update({'cancel_counts': count_sale})
        # else:
        #     pass
        # operator = self.find_operator()
        # operator, scheduled_line = self.find_operator()
        # if operator:
        #     self.operator_id = operator[0]
        # else:
        #     raise ValidationError(_('No more active operator '))
        # if scheduled_line:
        #     scheduled_line.update({'used_operator': True})
        three_hours_period = (datetime.now().replace(microsecond=0)) - timedelta(hours=3)
        orders = (self.env['sale.order'].search(
            [('state', '=', 'sale'), ('id', '!=', self.id), ('partner_id', '=', self.partner_id.id),
            ('confirmation_date', '>=', str(three_hours_period))]))
            
        if orders and self.previous_orders:
            if orders:
                orders=sorted(orders, key=lambda x: (x.confirmation_date))
                view = (self.env.ref('ping_modifier_sales.previous_orders_form_view')).id
                return {
                    'name': 'Orders',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'previous.sale.orders',
                    'view_id': view,
                    'target': 'new',
                    'context':{'default_sale_order_id':orders[-1].id},
                    'type': 'ir.actions.act_window',
                }
        else:
            res = super(SaleOrder, self).action_confirm()
            self.action_active_users()
            return res


    # @api.multi
    # def working_so_modifications(self):
    #     if self.state_ws == 'pending':
    #         self.state_ws = 'progress'
    #     self.env['working.so.line'].create({
    #         'so_id': self.id,
    #         'operator_id':self.operator_id.id,
    #         'start_time': datetime.today(),
    #     })

    @api.multi
    def pause_section(self):
        if self.state_ws == 'progress':
            self.state_ws = 'paused'
            self.is_user_working = False
        for line in self.order_line:
            line.write({'line_state_ws': 'partial'})
            working_so_lines = self.env['working.so.line'].search([('line_id', '=', line.id)]).sorted(key=lambda r: r.start_time)
            if working_so_lines and not working_so_lines[-1].end_time:
                working_so_lines[-1].update({'end_time': datetime.today()})

        # working_so_lines = self.env['working.so.line'].search([])
        # working_so_lines.sorted(key=lambda r: r.start_time)
        # if working_so_lines:
        #     for line in working_so_lines:
        #         line.update({'end_time': datetime.today()})
                # working_so_lines[-1].update({'end_time': datetime.today()})

    @api.multi
    def complete_section(self):
        # working_so_lines = self.env['working.so.line'].search([])
        # working_so_lines.sorted(key=lambda r: r.start_time)
        # if working_so_lines and not working_so_lines[-1].end_time:
        #     working_so_lines[-1].update({'end_time': datetime.today()})
        for line in self.order_line:
            if line.line_state_ws != 'done':
                raise ValidationError(_('Sale Order still in progress, please make sure all the process are completed'))
        self.state_ws = 'completed'
        self.operator_id.compute_count_confirmed_orders_today()

    @api.multi
    def start_section(self):
        if self.state_ws in ['paused', 'pending']:
            self.state_ws = 'progress'
        # self.env['working.so.line'].create({
        #     'so_id': self.id,
        #     'start_time': datetime.today(),
        #     'operator_id': self.operator_id.id,
        # })

    @api.multi
    def action_active_users(self):
        active_operators = self.find_operator()
        self.so_balanced_assignment(active_operators)
        for user in self.env['res.users'].search([('active','=',True),('operator','=',True)]):
            user.compute_count_confirmed_orders_today()

    @api.multi
    def so_balanced_assignment(self, active_operators):
        count_dir = {}
        if active_operators:
            for op in active_operators:
                count_dir[op] = op.count_confirmed_orders_today
            
            sorted_count = sorted(count_dir.iterkeys(), key=lambda k: count_dir[k], reverse=False)
            user_to_assign = sorted_count[0]
            self.operator_id = user_to_assign.id

    @api.multi
    def create(self, vals):
        # import pdb;pdb.set_trace()
        if vals.get('source_seq_id'):
            source_seq_id = vals.get('source_seq_id')
            source = self.env['source.sequence'].search([('id', '=', source_seq_id)], limit=1).sequence_id.id
            # source_name = self.env['source.sequence'].search([('id', '=', source)], limit=1).name
            ir_seq = self.env['ir.sequence'].search([('id', '=', source)], limit=1)
            if ir_seq:
                vals['name'] = ir_seq.next_by_id() or _('New')
                vals['sequence'] = vals['name']
        res = super(SaleOrder, self).create(vals)
        return res



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    related_state_ws = fields.Selection([
        ('pending', 'Pending'),
        ('paused', 'Paused'),
        ('progress', 'Progress'),
        ('completed', 'Completed')
    ],
    default='pending',
    string='Order Working Status',
    related='order_id.state_ws',
    )

    current_qty = fields.Float(string='Current Qty')
    line_state_ws = fields.Selection([
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('partial', 'Partially Done'),
        ('done', 'Done')
    ], default='pending', string='Status')


    @api.multi
    def _prepare_invoice_line(self, qty):
        if not self.current_qty==0.0:
            qty = self.current_qty
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        return res

    def action_start_working(self):
        if not self.order_id.state_ws == 'progress':
            self.order_id.state_ws = 'progress'
        if self.line_state_ws in ['pending', 'partial']:
            self.line_state_ws = 'progress'
        self.env['working.so.line'].create({
            'so_id': self.order_id.id,
            'line_id': self.id,
            'start_time': datetime.today(),
            'operator_id': self.order_id.operator_id.id,
        })
    
    def action_done_working(self):
        view = (self.env.ref('ping_modifier_sales.current_qty_view')).id
        return {
            'name': 'Fill Current QTY',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'current.qty',
            'view_id': view,
            'target': 'new',
            'context':{'default_orderline_id':self.id},
            'type': 'ir.actions.act_window',
        }
        
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'current_qty')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if not line.current_qty == 0.0:
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.current_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            else:
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        active_id = self.env.context.get('active_id', False)
        order = self.env['sale.order'].browse(active_id)
        for line in order.order_line:
            if line.state != 'done':
                raise ValidationError(_('You cannot able to create an invoice if the status is still in progress'))
        return super(SaleAdvancePaymentInv, self).create_invoices()