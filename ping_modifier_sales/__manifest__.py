{
    "name": "ping_modifier_sales",
    "category": 'Sale',
    'summary': '',
    "description": """ping_modifier_sales

    """,
    "author": "Hashmicro/Shiyas",
    "website": "",
    "depends": [
        'base',
        'sales_team',
        'sale',
        'stock',
        'standard_sales_access_right',
    ],
    "data": [
        'views/so_templates.xml',
        'security/security.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/user_view.xml',
        'views/workin_so_view.xml',
        'views/source_sequnce.xml',
        'views/res_partner_view.xml',
        'wizard/current_qty_wiz_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
