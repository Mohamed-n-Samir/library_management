from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta


class LibraryRental(models.Model):

    _name = "library.rental"
    _description = "Library Rental"

    # Fields
    book_id = fields.Many2one(
        comodel_name="library.book",
        string="Book",
        required=True,
        index=True,
        ondelete="restrict",
        help="The book being rented",
    )
    member_id = fields.Many2one(
        comodel_name="library.member",
        string="Member",
        required=True,
        index=True,
        ondelete="restrict",
        help="The member renting the book",
    )
    checkout_date = fields.Date(
        string="Checkout Date",
        default=fields.Date.context_today,
        required=True,
        help="Date when the book was checked out",
    )
    due_date = fields.Date(
        string="Due Date", required=True, help="Date whan the book should be returned"
    )
    return_date = fields.Date(
        string="Return Date", help="Actual date when the book was returned"
    )
    state = fields.Selection(
        selection=[
            ("ongoing", "Ongoing"),
            ("returned", "Returned"),
            ("overdue", "Overdue"),
        ],
        string="Status",
        default="ongoing",
        required=True,
        help="Current status of the rental",
    )
    days_overdue = fields.Integer(
        string="Days Overdue",
        compute="_compute_days_overdue",
        help="Number of days the rental is overdue",
    )
    book_title = fields.Char(
        related="book_id.name",
        string="Book Title",
        store=True,
        help="Title of the rented book",
    )
    member_name = fields.Char(
        related="member_id.name",
        string="Member Name",
        store=True,
        help="Name of the member rented the book",
    )
    member_email = fields.Char(
        related="member_id.email",
        string="Member email",
        help="Email of the member who rented the book",
    )

    # Constraints
    @api.constrains("book_id", "state")
    def _check_availability(self):
        for rental in self:
            if rental.state == "ongoing":
                existing_rental = self.search(
                    [
                        ("book_id", "=", rental.book_id.id),
                        ("state", "in", ["ongoing", "overdue"]),
                        ("id", "!=", rental.id),
                    ],
                    limit=1,
                )
                if existing_rental:
                    raise ValidationError(
                        f"Cannot create rental: '{rental.book_id.name}' is already "
                        f"rented by {existing_rental.member_name}"
                        f"Please wait until the book is returned."
                    )

    @api.constrains("due_date", "checkout_date")
    def _check_due_date(self):
        for rental in self:
            if rental.due_date and rental.checkout_date:
                if rental.due_date < rental.checkout_date:
                    raise ValidationError(
                        "Due date cannot be earlier than checkout date."
                    )

    @api.constrains("return_date", "checkout_date")
    def _check_return_date(self):
        for rental in self:
            if rental.return_date and rental.checkout_date:
                if rental.return_date < rental.checkout_date:
                    raise ValidationError(
                        "Return date cannot be earlier than checkout date."
                    )

    # Methods
    @api.depends("due_date", "return_date", "state")
    def _compute_days_overdue(self):
        today = fields.Date.context_today(self)
        for rental in self:
            if rental.state in ["ongoing", "overdue"] and rental.due_date:
                if rental.due_date < today:
                    rental.days_overdue = (today - rental.due_date).days
                else:
                    rental.days_overdue = 0
            elif rental.state == "returned" and rental.return_date and rental.due_date:
                if rental.return_date > rental.due_date:
                    rental.days_overdue = (rental.return_date - rental.due_date).days
                else:
                    rental.days_overdue = 0
            else:
                rental.days_overdue = 0

    # CRUD Methods
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            book_id = vals.get("book_id")
            if book_id:
                book = self.env["library.book"].browse(book_id)
                if book.status == "rented":
                    raise UserError(
                        f"Can't create rental: '{book.name} is currently rented. "
                        "Please check availability before creating a rental."
                    )
            vals["state"] = "ongoing"

        rentals = super().create(vals_list)

        for rental in rentals:
            rental.book_id.write({"status": "rented"})

        return rentals

    def unlink(self):
        for rental in self:
            if rental.state in ["ongoing", "overdue"]:
                raise UserError(
                    "Can't delete an active rental. Please return the book "
                    f"'{rental.book_id.name}' first."
                )
        return super().unlink()

    # SET DEFAULT Methods
    @api.onchange("checkout_date")
    def _onchage_checkout_date(self):
        if self.checkout_date and not self.due_date:
            self.due_date = self.checkout_date + timedelta(days=14)

    @api.onchange("book_id")
    def _onchange_book_id(self):
        if self.book_id and not self.book_id.available:
            return {
                "warning": {
                    "title": "Book Not Available",
                    "message": f"'{self.book_id.name}' is currently not available for rental.",
                }
            }

    # Action Methods
    def action_return_book(self):
        for rental in self:
            if rental.state == "returned":
                raise UserError(
                    f"this book has already been returned on {rental.return_date}"
                )
            today = fields.Date.context_today(self)
            rental.write({
                'return_date': today, 
                'state': 'returned',
            })
            rental.book_id.write({
                'status': 'available'
            })
            
            return {
                'type': 'ir.actions.client', 
                'tag': 'reload',
            }
            
    def action_mark_overdue(self):
        for rental in self:
            if rental.state != 'ongoing':
                raise UserError( 
                    f'Only ongoing rentals can be marked as overdue.'
                    f'Current state: {rental.state}'
                )
                
            rental.write({
                'state': 'overdue'
            })
            return True
        
    
    # CRON Methods
    def _cron_check_overdue_rentals(self):
        today = fields.Date.context_today(self)
        
        overdue_rentals = self.search([
            ('due_date', '<', today),
            ('return_date', '=', False), 
            ('state', 'in', ['ongoing', 'overdue'])
        ])
        
        for rental in overdue_rentals:
            if rental.state != 'overdue':
                rental.write({
                    'state': 'overdue'
                })
        
        return True
    
            
    
