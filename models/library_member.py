from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class LibraryMember(models.Model):

    _name = "library.member"
    _description = "Library Member"

    # Fields
    name = fields.Char(
        string="Name", required=True, index=True, help="Full name of the Member."
    )
    email = fields.Char(
        string="Email",
        required=True,
        help="Email address for notifications and reminders",
    )
    active = fields.Boolean(string="Active", default=True)
    rental_ids = fields.One2many(
        comodel_name='library.rental',
        inverse_name='member_id',
        string='Rentals',
        help='All rentals by this member'
    )
    current_rental_ids = fields.One2many(
        comodel_name='library.rental',
        inverse_name='member_id',
        string='Current Rentals',
        help='Active rentals by this member',
        compute='_compute_current_rentals'
    )
    rental_count = fields.Integer(
        string="Total Rentals",
        compute="_compute_rental_count",
        store=True,
        help="Total number of rentals by this member.",
    )
    active_rental_count = fields.Integer(
        string="Active Rentals",
        compute="_compute_rental_count",
        store=True,
        help="Number of currently active rentals",
    )
    overdue_rental_count = fields.Integer(
        string="Overdue Rentals",
        compute="_compute_rental_count",
        store=True,
        help="Number of overdue rentals",
    )


    # Constraints
    @api.constrains('email')
    def _check_email(self):
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for member in self:
            if member.email and not email_pattern.match(member.email):
                raise ValidationError(
                    f"Invalid email format: {member.email}"
                    "Please enter a valid email address."
                )

    
    # Methods
    @api.depends('rental_ids', 'rental_ids.state')
    def _compute_rental_count(self):
        for member in self:
            member.rental_count = len(member.rental_ids)
            member.active_rental_count = len(
                member.rental_ids.filtered(lambda r: r.state == 'ongoing')
            )
            member.overdue_rental_count = len(
                member.rental_ids.filtered(lambda r: r.state == 'overdue')
            )
            
    def _compute_current_rentals(self):
        for member in self:
            member.current_rental_ids = member.rental_ids.filtered(lambda rental: rental.state in ['ongoing', 'overdue'])

