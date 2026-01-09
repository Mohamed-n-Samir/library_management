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