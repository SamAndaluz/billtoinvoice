# -*- coding: utf-8 -*-
{
    'name': "ITL From Bill to Invoice",

    'summary': """
        This module allow to create a invoice from a bill.""",

    'description': """
        This module allow to create a invoice from a bill.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'data/comision_product.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
