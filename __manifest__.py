{
    "name": "Library Management",
    "version": "19.0.1.0.0",
    "author": "Mohamed Samir",
    "description": "Library Management System for Odoo 19",
    "license": 'LGPL-3',
    "depends": ["base"],
    "data": [
        'security/base_menu_security.xml',
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'data/library_cron.xml',
        'views/library_author_views.xml',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_rental_views.xml',
        'views/base_menu.xml',
        'views/library_menus.xml',
    ],
    "assets": {
    },
    "application": True,
    "installable": True,
}
