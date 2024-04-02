# -*- coding: utf-8 -*-
{
    'name': "Insights",
    'summary': """
        Business Insights """,
    'description': """
        Display Business Sales/Performance
    """,
    'author': "samuel",
    'website': "",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'web.assets_assets': [
            'insights/static/src/lib/chart.umd.min.js',
        ],
        'web.assets_backend': [
            'insights/static/src/js/insight_owl.js',
            'insights/static/src/js/chartTemplate.js',
        ],
        'web.assets_qweb': [
            'insights/static/src/xml/template.xml',
            'insights/static/src/xml/chart.xml',
        ],
    },
}
