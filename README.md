# Library Management Addon for Odoo 19 (Production Ready)

A production-ready library management module for Odoo 19 that manages books, authors, members, and rentals, with automatic overdue detection and email notifications.

## Overview
Manage book catalog, track members, handle rentals, and monitor overdue items automatically.

## Requirements
- Odoo 19.0 (Community or Enterprise)  
- Python 3.10+  
- PostgreSQL 12+  
- Dependencies: base, mail  

## Installation
Copy the `library_management` folder to your Odoo addons directory and install via the Apps menu.

## Configuration

### User Groups
- **Library User**: Read/Write, no delete  
- **Library Manager**: Full access including delete  

### Email & Scheduled Action
Configure outgoing mail servers for reminders. Overdue rentals are checked daily by a scheduled action.

## Module Structure

### Models
**library.author** – Author info and books  
**library.book** – Title, ISBN, author, status, availability  
**library.member** – Name, email, active status, rentals  
**library.rental** – Book, member, checkout/due/return dates, state, days overdue  

### Business Logic
- Rentals can only be created if the book is available  
- Returning a book updates rental state and availability  
- Overdue rentals are flagged and trigger email reminders  
- Validation ensures correct dates and valid emails  

## Menu Structure
Library  
├── Catalog (Books, Authors, Rentals, Members)  

## Troubleshooting
- Ensure the module is in the addons path  
- Verify outgoing mail server configuration  
- Confirm scheduled actions and cron worker are active  
- Check user group assignments for access  

## License
GNU Lesser General Public License v3.0 (LGPL-3)

## Version
19.0.1.0.0



