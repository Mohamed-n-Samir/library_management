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
    
    
    # Methods
    @api.depends('status')
    def _compute_available(self):
        for book in self:
            book.available = book.status == 'available'
    
