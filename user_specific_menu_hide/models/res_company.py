# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    hidden_menus_ids = fields.One2many(
        comodel_name='hidden.menu',
        inverse_name='company_id',
        string='Hidden Menus for Users'
    )
    


class HiddenMenu(models.Model):
    _name = 'hidden.menu'
    _description = 'Hidden Menu'

    menu_id = fields.Many2one(
        comodel_name='ir.ui.menu',
        string='Menu',
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='hide_menu_for_user_relation',
        column1='menu_line_id',
        column2='user_id',
        string='User',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True
    )


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ids = super(IrUiMenu, self).search(args, offset=0, limit=None, order=order, count=False)
        ids_list = [rec.id for rec in ids]
        user = self.env['res.users'].browse(self._uid)
        self._cr.execute("""SELECT a.menu_id FROM hidden_menu a WHERE
                        a.id IN(SELECT b.menu_line_id FROM  hide_menu_for_user_relation b WHERE b.user_id = %d)
                        AND a.company_id = %d""" % (self._uid, user.company_id.id))

        for menu_id in self._cr.fetchall():
            if menu_id[0] in ids_list:
                ids_list.remove(menu_id[0])
        ids = self.env['ir.ui.menu'].browse(ids_list)
        if offset:
            ids = ids[offset:]
        if limit:
            ids = ids[:limit]
        return len(ids) if count else ids