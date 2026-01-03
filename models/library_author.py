from odoo import models, fields, api


class LibraryAuthor(models.Model):

    _name = "library.author"
    _description = "Library Author"
    
    
    # Fields
    name = fields.Char(string="Name", required=True, index=True, help="Author Full name")
    biography = fields.Text(
        string="Biography", help="Biographical information about the author"
    )
    book_ids = fields.One2many(
        comodel_name="library.book",
        inverse_name="author_id",
        string="Books",
        help="Books written by this author",
    )
    book_count = fields.Integer(
        string="Number of Books",
        compute="_compute_book_count",
        help="Total number of books by this author in the library",
        default=0,
        store=True
    )
    
    
    # Methods
    @api.depends('book_ids')
    def _compute_book_count(self):
        for author in self:
            author.book_count = len(author.book_ids)
