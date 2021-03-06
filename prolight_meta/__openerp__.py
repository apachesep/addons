# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Prolight Meta Package',
    'version': '1.0',
    'category': 'Sales',
    'description': """
    Prolight meta-package
    """,
    'author': 'WEBMANIA',
    'website': 'http://www.webmania.ma',
    'depends': ['account_accountant',
                'purchase',
                'sale_stock',
                'l10n_ma_legal',
                'stock_account',
                'sale_automatic_workflow',
#                'sale_payment_method',
                'sale_margin'
                ],
    'data': [
           'account_views.xml',
           'sale_views.xml',
           'purchase_views.xml',
           'stock_views.xml'
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
