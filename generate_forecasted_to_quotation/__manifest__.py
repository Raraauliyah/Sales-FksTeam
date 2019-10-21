# -*- coding: utf-8 -*-
{
    'name': "Generate Forecasted to Quotation",

    'summary': """
        Summary of the module's purpose, used as when Quotation will create, at that time Forecasted qty will updated.
        """,

    'description': """
        Long description of module's purpose when Quotation will create, at that time Forecasted qty will updated.
    """,

    'author': "Hashmicro / Jeel",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'mrp', 'forecasted_quantity_breakdown'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}