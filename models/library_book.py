from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class LibraryBook(models.Model):

    _name = "library.book"
    _description = "Library Book"


    # Fields
    name = fields.Char(
        string="Title", required=True, index=True, help="Tile of the book"
    )
    isbn = fields.Char(
        string="ISBN",
        index=True,
        copy=False,
        help="International Standard Book Number (must be unique)",
    )
    author_id = fields.Many2one(
        comodel_name="library.author",
        string="Author",
        index=True,
        ondelete="set null",
        help="Author of the book",
    )
    publication_date = fields.Date(
        string="Publication Date", help="Date when the book was published"
    )
    status = fields.Selection(
        selection=[("available", "Available"), ("rented", "Rented")],
        string="Status",
        default="available",
        required=True,
        help="Current availability status of the book",
    )
    
    available = fields.Boolean(
        string='Is Available',
        compute='_compute_available',
        store=True,
        help='Computed field indicating if the book is available for rental'
    )
    
    rental_ids = fields.One2many(
        comodel_name='library.rental',
        inverse_name='book_id',
        string='Rental History',
        help='History of all rentals for this book'
    )
    rental_count = fields.Integer(
        string='Rental Count',
        compute='_compute_rental_count',
        help='Total number of times this book has been rented'
    )
    
    # Constraints
    _isbn_unique = models.Constraint(
        "UNIQUE(isbn)", "The ISBN field must be unique! This ISBN already exists."
    )

    
    # Methods
    @api.depends('status')
    def _compute_available(self):
        for book in self:
            book.available = bool(book.status == 'available')
    
    @api.depends('rental_ids')
    def _compute_rental_count(self):
        for book in self:
            book.rental_count = len(book.rental_ids)
            
    
    # Actions
    def action_check_availability(self):
        self.ensure_one()
        if self.available:
            message = f"'{self.name}' is available for rental."
            notification_type = 'success'
        else:
            current_rental = self.env['library.rental'].search([
                ('book_id', '=', self.id),
                ('state', 'in', ['ongoing', 'overdue'])
            ], limit=1)
            
            if current_rental:
                message = f"'{self.name}' is currently rented by {current_rental.member_id.name}. Due date: {current_rental.due_date}"
            else:
                message = f"'{self.name}' is not available."
            notification_type = 'warning'
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Book Availability',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }
        