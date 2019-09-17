# -*- coding: utf-8 -*-
{
    'name': "Create MO Forecastqty",

    'summary': """
        create MO for forecasted QTY""",

    'description': """
        Long description of module's purpose to create MO for forecasted QTY
    """,

    'author': "Hashmicro / Jeel",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_mo_view.xml',
        'views/views.xml',
        'report/sale_report_inherit_view.xml',
    ],
}