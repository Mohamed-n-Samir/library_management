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