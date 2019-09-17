# -*- coding: utf-8 -*-
{
    'name': 'Ping Custom UI',
    'version': '0.1',
    'category': 'Uncategorized',
    'summary': 'This module allow to create a sale order from pos',
    'description': """
    This module allow to create a sale order from pos
""",
    'author': "hashmicro/ Janbaz Aga",
    'website': "http://www.hashmicro.com",
    'depends': ['base','point_of_sale'],
    "data": [
        'views/pos_create_sale_order.xml',
        'views/point_of_sale_report.xml',
    ],
    'qweb': [
            'static/src/xml/pos.xml'
    ],
}

