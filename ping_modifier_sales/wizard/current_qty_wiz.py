from odoo import api, fields, models
from datetime import datetime

class CurrentQTY(models.TransientModel):
    _name = 'current.qty'

    current_qty = fields.Float(string='Current QTY')

    @api.multi
    def apply(self):
        sol = self.env['sale.order.line']
        active_id = self.env.context.get('active_id', False)
        line =  sol.search([('id', '=', active_id)]) or []
        working_so_lines = self.env['working.so.line'].search([('line_id', '=', active_id)])

        working_so_lines.sorted(key=lambda r: r.start_time)
        if working_so_lines and not working_so_lines[-1].end_time:
            working_so_lines[-1].update({'end_time': datetime.today()})

        if line:

            if line.product_uom_qty > (float(line.current_qty) + float(self.current_qty)):
                state = 'partial'
            else:
                state = 'done'
                open_lines = sol.search([('order_id', '=', line.order_id.id), ('line_state_ws', '!=', 'done')])
                if open_lines and len(open_lines) == 1:
                    line.order_id.state_ws = 'completed'

            return line.write({
                'current_qty': float(line.current_qty) + float(self.current_qty),
                'line_state_ws': state,
            })
        else:
            return False