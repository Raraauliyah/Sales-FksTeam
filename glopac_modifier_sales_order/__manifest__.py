{
    'name': 'Glopac Modifier Sales Order',
    'category': 'Hidden',
    'summary': '',
    'version': '1.0',
    'description': """
add following field for SO
========================

        """,
    'author': 'Hashmicro/ Janbaz Aga',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml'
             ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
