# Digital Library Web Application

A complete Django-based Digital Library System with beautiful UI, user authentication, book management, and protected PDF reading.

## Features

### User Features
- User registration and login with userId + password
- Browse all approved books
- Search books by title, author, or description
- Filter books by category, author, and type (free/paid)
- View book details with reviews and ratings
- Read free books online (PDF viewer)
- Add/remove favorites
- Add/edit/delete reviews with 1-5 star ratings
- View reading history
- View favorite books list

### Admin Features
- Admin dashboard with statistics
- Add/edit/delete books
- Upload book cover images and PDF files
- Approve/reject books
- Manage reviews (delete inappropriate reviews)
- Track book statistics (views, reads, favorites)

### Security Features
- Protected PDF viewing (no direct URL access)
- Disabled download, print, save, and right-click on PDFs
- Login required for reading books
- Paid books are restricted from reading
- Secure file serving through Django views

## Tech Stack

- **Backend**: Python, Django
- **Templates**: Django Templates (HTML)
- **Styling**: Tailwind CSS (via CDN)
- **Database**: SQLite
- **Storage**: Local storage for PDFs and images

## Installation

1. **Install Dependencies**
   ```bash
   pip install django Pillow
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```
   When prompted:
   - User ID: (enter your admin userId)
   - Email: (optional)
   - Password: (enter a secure password)
   - The user will automatically have admin role

4. **Run Server**
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**
   - Open browser and go to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## Project Structure

```
digital_library/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── users/
│   ├── models.py (Custom User Model)
│   ├── views.py
│   ├── forms.py
│   └── ...
├── books/
│   ├── models.py (Book Model)
│   ├── views.py
│   ├── forms.py
│   └── ...
├── reviews/
│   ├── models.py (Review Model)
│   ├── views.py
│   └── ...
├── favourites/
│   ├── models.py (Favourite Model)
│   ├── views.py
│   └── ...
├── history/
│   ├── models.py (ReadingHistory Model)
│   ├── views.py
│   └── ...
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── book_list.html
│   ├── book_detail.html
│   ├── reader.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── favourites_list.html
│   ├── reading_history.html
│   ├── edit_review.html
│   └── admin/
│       ├── dashboard.html
│       ├── book_list.html
│       ├── book_form.html
│       ├── book_confirm_delete.html
│       ├── review_list.html
│       └── review_confirm_delete.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
    ├── covers/
    └── pdfs/
```

## Usage

### As Admin

1. Login with your admin credentials
2. Go to Admin Dashboard
3. Add books with:
   - Title, Author, Description
   - Category (Science, Engineering, Fiction, etc.)
   - Type (Free or Paid)
   - Cover Image
   - PDF File
   - Approval status
4. Approve books to make them visible to users
5. Manage reviews and delete inappropriate ones

### As User

1. Register a new account or login
2. Browse books on the home page or book list
3. Search and filter books
4. Click on a book to view details
5. Read free books online (login required)
6. Add books to favorites
7. Write reviews with ratings
8. View your reading history

## Book Categories

- Science
- Engineering
- Fiction
- Computer Science
- Islamiyat
- History
- Biography
- Literature

## Security Notes

- PDFs are served through protected Django views
- Direct URL access to PDFs is blocked
- Download, print, and save are disabled in the PDF viewer
- Only free books can be read online
- Paid books show a restriction message

## Notes

- All UI is built with Tailwind CSS (via CDN) for modern, responsive design
- The application is fully responsive and works on all devices
- No API endpoints - everything uses Django views and templates
- No React, Next.js, or separate frontend - pure Django

## License

This project is for educational purposes.

