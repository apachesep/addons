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

from openerp import tools
from openerp import fields, models, api


AVAILABLE_PRIORITIES = [
    ('0', 'Bad'),
    ('1', 'Below Average'),
    ('2', 'Average'),
    ('3', 'Good'),
    ('4', 'Excellent')
]

SUBMISS_ETAT= [
    ('draft', 'Brouillon'),
    ('submitted', 'Soumis'),
    ('pending', 'En cours d\'étude'),
    ('accepted', 'Aprouvé'),
    ('rejected', 'Refusé')
]

REQSOUMISS_ETAT =[
    ('draft', 'Brouillon'),
    ('submitted', 'En cours'),
    ('accepted', 'Aprouvé'),
    ('rejected', 'Refusé'),
    ('cancel', 'Annulé')
]


class ProjectOfferField(models.Model):
    _name = 'project.offer.field'
    _description = u'Thématique'
    
    name = fields.Char('Nom')

class ProjectSubmission(models.Model):
    """hr.applicant"""
    _name = 'project.submission'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u'Soumission'
    
    @api.one
    def _get_manager(self):
        return self.offer.user_id
    
    name = fields.Char('Intitulé du projet', required=True)
    field = fields.Many2one('project.offer.field', 'Domaine d\'activité', required=True)
    document_ids = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    project = fields.Many2one('project.project', string='Projet')
    state = fields.Selection(SUBMISS_ETAT, 'Etat', track_visibility='always', default='draft')
    offer = fields.Many2one('project.offer', string='Offre de projet', required=True)
    candidate = fields.Many2one('project.candidate', string='Soumissionnaire', required=True)
    address = fields.Many2one('res.partner', string='Adresse du projet')
    active = fields.Boolean('Actif', default=True)
    description = fields.Text('Description')
    probability = fields.Float('Probabilité', default=0)
    user_id = fields.Many2one('res.users', 'Responsable', track_visibility='always', default=_get_manager)
    date_submitted = fields.Datetime('Date de soumission', readonly=True)
    date_processed = fields.Datetime('Date de traitement', readonly=True)
    date_action = fields.Datetime('Date de la prochaine action')
    title_action = fields.Char('Prochaine action', size=64)
    color = fields.Integer('Couleur', default=0)
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Appreciation')
    partner_mobile = fields.Char(related='candidate.mobile')
    
    @api.multi
    def _get_attached_docs(self):
        res = {}
        for rec in self:
            res[rec.id] = self.env['ir.attachment'].search([('res_model', '=', 'project.submission'), ('res_id', '=', rec.id)])
        return res
    
    @api.one
    def action_get_attachment_tree_view(self):
        model, action_id = self.env['ir.model.data'].get_object_reference('base', 'action_attachment')
        action = self.env[model].read(action_id)
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.id}
        action['domain'] = str([('res_model', '=', 'project.submission'), ('res_id', '=', self.id)])
        return action
    
    @api.onchange('candidate')
    def set_default_address(self):
        self.address = self.candidate.partner_id
    
    def _count_all(self):
        return 0
    
    @api.one
    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        
        partners= []
        if self.candidate:
            partners.append(self.candidate.partner_id.id)
        if self.user_id :
            partners.append(self.user_id.partner_id.id)
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'default_partner_ids': partners,
            'default_user_id': self.user_id,
            'default_name': self.name,
        }
        return res
    
class ProjectOffer(models.Model):
    """hr.job"""
    _description = u'Offre'
    _name = 'project.offer'

    def _get_partner_id(self):
        return self.env.user.company_id.partner_id.id

    name = fields.Char(string='Nom', required=True)
    document_ids = fields.One2many('ir.attachment', compute='_get_attached_docs', string='Documents sources')
    documents_count =  fields.Integer(compute='_count_all', string='Nombre de documents')
    partner_id =  fields.Many2one('res.partner', 'Institut hôte',default=_get_partner_id)
    submissions = fields.One2many('project.submission', 'offer', string='Soumissions', required=True)
    type = fields.Many2one('project.offer.type', required=True)
    total_time = fields.Integer('Durée de Réalisation en mois', required=True)
    survey_id =  fields.Many2one('survey.survey', 'Formulaire d\'inscription')
    color = fields.Integer('Couleur', default=0)
    state =  fields.Selection([('draft', 'Brouillon'), ('open', 'En cours'),
                              ('done', 'Terminé'), ('closed', 'Fermé')],
                              string='Status', readonly=True, required=True,
                              track_visibility='always', copy=False, default='draft')
    submission_count =  fields.Integer(compute='_count_all', string='Soumissions')
    accepted_count =  fields.Integer(compute='_count_all', string='Soumissions acceptées')
    user_id =  fields.Many2one('res.users', 'Responsable', track_visibility='always')
    vacant_count = fields.Integer(compute='_count_all')
    total_count = fields.Integer(string='Limite de soumissions', required=True)
    
    @api.one
    def _get_attached_docs(self):
        res = self.env['ir.attachment'].search([('res_model', '=', 'project.offer'), ('res_id', '=', self.id)])
        self.document_ids =  res.ids
    """
    @api.returns('ir.actions.act_window')
    @api.multi
    def action_get_attachment_tree_view(self):
        self.ensure_one()
        model, action_id = self.env['ir.model.data'].get_object_reference('base', 'action_attachment')
        action = self.env[model].browse(action_id)
        ctx = action.env.context.copy()
        ctx.update({'default_res_model': self._name, 'default_res_id': self.id})
        #action['context'] = {'default_res_model': self._name, 'default_res_id': self.id}
        #action['domain'] = str([('res_model', '=', 'project.offer'), ('res_id', '=', self.id)])
        return action.with_context(ctx)"""
     
    @api.cr_uid_ids_context
    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        #open attachments of job and related applicantions.
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str([('res_model', '=', 'project.offer'), ('res_id', 'in', ids)])
        return action
    
    @api.one
    @api.depends('submissions', 'total_count')
    def _count_all(self):
        self.submission_count = len(self.submissions)
        self.accepted_count = len(self.submissions.filtered(lambda s: s.state == 'accepted'))
        self.vacant_count = self.total_count - self.accepted_count
        self.documents_count = len(self.document_ids)
    
    @api.one
    def action_set_total_count(self, value):
        self.total_count= value
        
    @api.one
    def action_open(self):
        self.state = 'open'
        
    @api.one
    def action_close(self):
        self.state = 'closed'

    def action_print_survey(self):
        return self.survey_id.action_print_survey()

    def set_open(self):
        self.write({
            'state': 'open',
            'no_of_total_submissions': 0
        })
        return True
    
class ProjectOfferType(models.Model):
    """hr.department"""
    _name = 'project.offer.type'
    _description = u'Type d\'appel à projets'
    
    name = fields.Char('Nom', required=True)
    offers = fields.One2many('project.offer', 'type')
    note = fields.Text('Note')
    
    manager = fields.Many2one('res.users', 'Responsable')

class ProjectCandidate(models.Model):

    """hr.employee"""
    _inherit = ['mail.thread']
    _inherits = {"res.users": 'user_id'}
    _name = 'project.candidate'
    _description = u'Soumissionaire'

    submission_ids = fields.One2many('project.submission', 'candidate', 'Soumissions')
    user_id = fields.Many2one('res.users', 'Utilisateur lié', required=True, ondelete='restrict')
    offer_ids = fields.One2many('project.offer', string='Offres', compute='get_offer_ids')
    color = fields.Integer('Color Index', default=0)
    city = fields.Char(related='partner_id.city', string='Ville')
    login = fields.Char(related='user_id.login', string='Login', readonly=True)
    login_date = fields.Date(related='user_id.login_date', string='Dernière Connection', readonly=True)
    address_home_id = fields.Many2one('res.partner', string='Adresse Candidate')
    mobile_phone = fields.Char(string='Mobile', readonly=False)
    email = fields.Char(string='Email', size=240)
    work_location = fields.Char('Adresse Travail')
    notes = fields.Text('Notes')
        
    
    @api.one
    @api.depends('submission_ids')
    def get_offer_ids(self):
        self.offer_ids = self.submission_ids.mapped('offer')
    
class ProjectRequest(models.Model):  
    _name = 'project.request'
    _description = u'Demande de ressources'
    
    name = fields.Char(string='Objet', size=200)
    type_id = fields.Many2one('project.request.type', 'Type de demande')
    submission_id = fields.Many2one('project.submission', 'Projet')
    request_date = fields.Datetime('Date de demande', readonly=True)
    processing_date = fields.Datetime('Date de traitement', readonly=True)
    state = fields.Selection(REQSOUMISS_ETAT, 'Submission')

class ProjectSubmissionRequestType(models.Model):
    _name = 'project.request.type'
    _description = 'Type de demande'
    
    name = fields.Char()
    
    