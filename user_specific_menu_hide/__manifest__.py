{
    'name': 'User Specific Menu Hide',
    'version': '10.0.1.0.0',
    'author': 'Hashmicro | Krushndevsinh Jadeja',
    'category': 'Tools',
    'depends': ['base'],
    'summary': 'User Specific Menu Hide',
    'description': """
        Make any menu invisible for specific user(s).
    """,
    'data': [
        'security/user_specific_menu_hide_security.xml',
        'security/ir.model.access.csv',
        'views/company_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
