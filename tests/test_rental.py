from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta


class TestLibraryRental(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.author = cls.env['library.author'].create({
            'name': 'Test Author',
            'biography': 'A test author for unit tests.',
        })
        
        cls.book_1 = cls.env['library.book'].create({
            'name': 'Test Book 1',
            'isbn': '978-1234567890',
            'author_id': cls.author.id,
            'publication_date': date(2020, 1, 1),
            'status': 'available',
        })
        
        cls.book_2 = cls.env['library.book'].create({
            'name': 'Test Book 2',
            'isbn': '978-0987654321',
            'author_id': cls.author.id,
            'publication_date': date(2021, 6, 15),
            'status': 'available',
        })
        
        cls.member = cls.env['library.member'].create({
            'name': 'Test Member',
            'email': 'test.member@example.com',
            'active': True,
        })
        
        
    def test_01_book_initial_availability(self):

        self.assertEqual(self.book_1.status, 'available')
        self.assertTrue(self.book_1.available)
        
        
    def test_02_rental_creation_updates_book_status(self):

        # test that the creation of a rental sets book status to rented

        rental = self.env['library.rental'].create({
            'book_id': self.book_1.id,
            'member_id': self.member.id,
            'checkout_date': date.today(),
            'due_date': date.today() + timedelta(days=14),
        })
        
        self.assertEqual(rental.state, 'ongoing')
        
        self.assertEqual(self.book_1.status, 'rented')
        self.assertFalse(self.book_1.available)
        
    def test_03_return_book_restores_availability(self):

        # Test that returning a book restores its availability.

        rental = self.env['library.rental'].create({
            'book_id': self.book_2.id,
            'member_id': self.member.id,
            'checkout_date': date.today(),
            'due_date': date.today() + timedelta(days=14),
        })
        
        self.assertEqual(self.book_2.status, 'rented')
        
        rental.action_return_book()

        self.assertEqual(rental.state, 'returned')
        self.assertIsNotNone(rental.return_date)
        
        self.assertEqual(self.book_2.status, 'available')
        self.assertTrue(self.book_2.available)
        
    def test_04_cannot_rent_already_rented_book(self):
        
        # Test that a rented book cannot be rented again.
        
        self.env['library.rental'].create({
            'book_id': self.book_1.id,
            'member_id': self.member.id,
            'checkout_date': date.today(),
            'due_date': date.today() + timedelta(days=14),
        })
        
        member_2 = self.env['library.member'].create({
            'name': 'Second Member',
            'email': 'second.member@example.com',
        })
        
        with self.assertRaises(UserError):
            self.env['library.rental'].create({
                'book_id': self.book_1.id,
                'member_id': member_2.id,
                'checkout_date': date.today(),
                'due_date': date.today() + timedelta(days=14),
            })
            
            
    def test_05_cron_marks_overdue_rentals(self):
        
        # Test that the cron job correctly marks overdue rentals.
        
        rental = self.env['library.rental'].create({
            'book_id': self.book_2.id,
            'member_id': self.member.id,
            'checkout_date': date.today() - timedelta(days=21),
            'due_date': date.today() - timedelta(days=7),
        })

        self.assertEqual(rental.state, 'ongoing')

        self.env['library.rental']._cron_check_overdue_rentals()

        rental.invalidate_recordset()

        self.assertEqual(rental.state, 'overdue')
        self.assertGreater(rental.days_overdue, 0)
        
        
    def test_06_email_validation(self):

        # Test that invalid email addresses are rejected.

        invalid_emails = [
            'not-a-valid-email',
            'notavalidemail',
            'notavalidemail@yourmail',
            'notavalidemail.com'
        ]

        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                self.env['library.member'].create({
                    'name': 'Invalid Email Member',
                    'email': email,
                })
                
    def test_07_due_date_must_be_after_checkout(self):
        
        # Test that due date cannot be before checkout date.
        
        with self.assertRaises(ValidationError):
            self.env['library.rental'].create({
                'book_id': self.book_2.id,
                'member_id': self.member.id,
                'checkout_date': date.today(),
                'due_date': date.today() - timedelta(days=7),
            })

    def test_08_cannot_delete_active_rental(self):
        
        # Test that active rentals cannot be deleted.
        
        rental = self.env['library.rental'].create({
            'book_id': self.book_2.id,
            'member_id': self.member.id,
            'checkout_date': date.today(),
            'due_date': date.today() + timedelta(days=14),
        })
        
        with self.assertRaises(UserError):
            rental.unlink()

    def test_09_can_delete_returned_rental(self):
        
        # Test that returned rentals can be deleted.
        
        rental = self.env['library.rental'].create({
            'book_id': self.book_2.id,
            'member_id': self.member.id,
            'checkout_date': date.today(),
            'due_date': date.today() + timedelta(days=14),
        })
        
        rental.action_return_book()

        rental.unlink()
        self.assertFalse(rental.exists())