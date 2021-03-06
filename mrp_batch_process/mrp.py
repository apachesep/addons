# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
from openerp import models, fields, api

class mrp_production(models.Model):
    _inherit = 'mrp.production'
    
    @api.one
    def batch_process(self):
        if self.state =='draft':
            self.action_confirm()
        if self.state == 'confirmed':
            self.force_production()
            self.action_ready()
        if self.state == 'ready':
            self.pool.get('mrp.production').action_produce(self.env.cr, self.env.uid, self.id, production_qty=self.product_qty, production_mode='consume_produce', wiz=False, context=self.env.context)
            self.action_production_end()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
