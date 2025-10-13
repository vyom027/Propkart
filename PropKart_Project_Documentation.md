# 🏠 PROPkART - Real Estate Platform Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technical Stack](#technical-stack)
3. [Database Schema](#database-schema)
4. [User Roles & Permissions](#user-roles--permissions)
5. [Core Features](#core-features)
6. [API Endpoints](#api-endpoints)
7. [File Structure](#file-structure)
8. [Installation & Setup](#installation--setup)
9. [Configuration](#configuration)
10. [Deployment](#deployment)

---

## 🎯 Project Overview

**PropKart** is a comprehensive real estate platform built with Django that connects property buyers and sellers. The platform provides a complete ecosystem for property listing, searching, communication, and management.

### Key Features:
- **Property Management**: List, search, and manage properties
- **User Authentication**: Secure registration and login system
- **Role-based Access**: Separate interfaces for buyers and sellers
- **Communication System**: Messaging, enquiries, and visit scheduling
- **AI Chatbot**: Intelligent property search assistant
- **File Management**: Image uploads and CSV property imports
- **Notification System**: Real-time in-app notifications

---

## 🛠 Technical Stack

### Backend
- **Framework**: Django 5.2.5
- **Database**: SQLite (Development)
- **Authentication**: Django Auth System
- **File Storage**: Django FileSystemStorage
- **Email**: Django Email Backend (SMTP)

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Bootstrap 5.3, Custom CSS
- **JavaScript**: Vanilla JS, AJAX
- **UI Components**: Bootstrap modals, dropdowns, forms

### External Services
- **AI Integration**: OpenAI GPT-3.5 / Google Gemini
- **Email Service**: Gmail SMTP
- **File Processing**: PIL (Python Imaging Library)

---

## 🗄 Database Schema

### Core Models

#### 1. User Model (Custom AbstractUser)
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_buyer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
```

#### 2. Property Model
```python
class Property(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rooms = models.IntegerField(blank=True, null=True)
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    furnished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    viewers = models.JSONField(default=list, blank=True)
```

#### 3. PropertyImage Model
```python
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

#### 4. Communication Models
```python
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Enquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='enquiries')
    buyer_name = models.CharField(max_length=100)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VisitRequest(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visit_requests')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visit_requests')
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    alternative_date = models.DateField(blank=True, null=True)
    alternative_time = models.TimeField(blank=True, null=True)
    visitor_name = models.CharField(max_length=100)
    visitor_phone = models.CharField(max_length=15)
    visitor_email = models.EmailField()
    message = models.TextField(blank=True)
    visitor_count = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    seller_response = models.TextField(blank=True)
    confirmed_date = models.DateField(blank=True, null=True)
    confirmed_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 5. AI Chat Models
```python
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    referenced_properties = models.JSONField(default=list, blank=True)
```

#### 6. Utility Models
```python
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=120)
    message = models.TextField(blank=True)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SellerRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

class PropertyImportKey(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=100)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='import_keys')
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 👥 User Roles & Permissions

### 1. Guest User (Not Logged In)
- Browse properties
- View property details
- Search properties
- Register account
- Submit enquiries (with contact info)
- Request visits (with contact info)

### 2. Buyer (Logged In User)
- All guest features
- Profile management
- Save properties to wishlist
- Direct messaging with sellers
- View own enquiries and visit requests
- AI chatbot assistance
- Notification management

### 3. Seller (Verified Property Owner)
- All buyer features
- Seller dashboard
- Property management (CRUD)
- Bulk property import (CSV)
- Message management
- Enquiry management
- Visit request management
- Property analytics
- Seller verification system

### 4. Administrator
- Django admin panel access
- User management
- Property verification
- System configuration
- Analytics and reporting

---

## 🚀 Core Features

### 1. Property Management
- **Property Listing**: Create, edit, delete properties
- **Image Management**: Multiple image uploads per property
- **Property Search**: Text-based and criteria-based search
- **Property Verification**: Admin approval system
- **Bulk Import**: CSV import with image URL support
- **View Tracking**: Property view analytics

### 2. User Authentication & Management
- **Registration**: Email verification with OTP
- **Login/Logout**: Secure authentication
- **Profile Management**: User information and avatar
- **Seller Verification**: Email-based verification system
- **Role Management**: Buyer/Seller role switching

### 3. Communication System
- **Direct Messaging**: Buyer-Seller communication
- **Property Enquiries**: Formal enquiry system
- **Visit Scheduling**: Property visit requests
- **Notifications**: Real-time in-app notifications
- **Email Integration**: SMTP email notifications

### 4. AI Chatbot Integration
- **Intelligent Search**: AI-powered property search
- **Context Awareness**: Conversation history
- **Property Recommendations**: AI-suggested properties
- **Multi-Model Support**: OpenAI GPT-3.5 / Google Gemini

### 5. Advanced Features
- **Wishlist System**: Save favorite properties
- **File Management**: Image uploads and processing
- **Responsive Design**: Mobile-friendly interface
- **Admin Panel**: Comprehensive admin interface
- **Analytics**: Property and user analytics

---

## 🔌 API Endpoints

### Authentication Endpoints
```
POST /register/                    # User registration
POST /login/                       # User login
POST /logout/                      # User logout
POST /verify-otp/                  # OTP verification
```

### Property Endpoints
```
GET  /properties/                 # List all properties
GET  /property/<id>/              # Property details
POST /property/<id>/increment-view/ # Increment view count
POST /property/<id>/message/       # Send message about property
POST /property/<id>/enquiry/       # Submit enquiry
POST /property/<id>/request-visit/ # Request property visit
```

### Seller Endpoints
```
GET  /seller/dashboard/           # Seller dashboard
POST /seller/property_create/     # Create property
POST /seller/property/<id>/edit/  # Edit property
POST /seller/property/<id>/delete/ # Delete property
POST /seller/properties/bulk-delete # Bulk delete properties
POST /seller/import/              # Import properties from CSV
GET  /seller/messages/            # Seller messages
GET  /seller/properties/          # My properties
GET  /seller/enquiries/           # Property enquiries
GET  /seller/visit-requests/      # Visit requests
```

### Chat API Endpoints
```
POST /api/chat/ask/               # Ask AI assistant
GET  /api/chat/history/           # Get chat history
POST /api/chat/new-session/       # Start new chat session
POST /api/chat/clear/             # Clear chat history
GET  /api/chat/conversation/      # Get conversation messages
POST /api/chat/delete/            # Delete specific messages
POST /api/chat/clear-conversation/ # Clear conversation
```

### Notification Endpoints
```
GET  /api/notifications/          # Get notifications
POST /api/notifications/mark-read # Mark notifications as read
POST /api/notifications/mark-all-read # Mark all as read
```

### Wishlist Endpoints
```
POST /wishlist/toggle/            # Toggle wishlist item
GET  /wishlist/                   # View wishlist
```

---

## 📁 File Structure

```
PropKart/
├── manage.py                     # Django management script
├── db.sqlite3                    # SQLite database
├── Propkart/                     # Main project directory
│   ├── __init__.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── app/                          # Main application
│   ├── __init__.py
│   ├── models.py                 # Database models
│   ├── views.py                  # View functions
│   ├── urls.py                   # App URL patterns
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── decorators.py             # Custom decorators
│   ├── chat_service.py           # AI chat service
│   ├── tests.py                  # Test cases
│   ├── static/                   # Static files
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   ├── chat-widget.css
│   │   │   └── bootstrap/
│   │   ├── js/
│   │   │   └── chat-widget.js
│   │   ├── images/
│   │   └── fonts/
│   ├── templates/                # HTML templates
│   │   ├── app/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── properties.html
│   │   │   ├── property-single.html
│   │   │   ├── profile.html
│   │   │   ├── messages.html
│   │   │   ├── wishlist.html
│   │   │   ├── buyer/
│   │   │   │   └── visit_requests.html
│   │   │   └── seller/
│   │   │       ├── seller-base.html
│   │   │       ├── seller-index.html
│   │   │       ├── my_properties.html
│   │   │       ├── add_property.html
│   │   │       ├── enquiries.html
│   │   │       ├── messages.html
│   │   │       ├── visit_requests.html
│   │   │       └── analytics.html
│   │   └── emails/
│   │       └── seller_verify.html
│   └── management/
│       └── commands/
│           └── test_chat.py
├── media/                        # User uploaded files
│   ├── profile_pics/
│   ├── property_images/
│   └── temp_uploads/
├── static/                       # Static files
├── templates/                     # Global templates
│   └── admin/
└── sample_data/                  # Sample data files
    ├── property_import_sample.csv
    └── test_import.csv
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Git

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd PropKart
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AI API Keys
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-2.0-flash
```

### Settings Configuration
Key settings in `Propkart/settings.py`:

```python
# Custom User Model
AUTH_USER_MODEL = "app.User"

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
```

---

## 🚀 Deployment

### Production Settings
1. **Set DEBUG = False**
2. **Configure ALLOWED_HOSTS**
3. **Use production database (PostgreSQL recommended)**
4. **Set up static file serving**
5. **Configure email settings**
6. **Set up SSL/HTTPS**

### Deployment Checklist
- [ ] Update SECRET_KEY
- [ ] Configure database
- [ ] Set up static files
- [ ] Configure email settings
- [ ] Set up AI API keys
- [ ] Test all functionality
- [ ] Set up monitoring
- [ ] Configure backups

---

## 📊 Current Status

### Completed Features ✅
- User authentication and registration
- Property management system
- Image upload and management
- Search functionality
- Messaging system
- Enquiry system
- Visit scheduling
- AI chatbot integration
- Notification system
- Admin panel
- Seller verification
- CSV import functionality
- Wishlist system

### In Progress 🚧
- Advanced search filters
- Analytics dashboard improvements
- Email notification expansion
- Property comparison feature

### Future Enhancements 🌟
- Payment integration
- Mobile app
- Advanced analytics
- Multi-language support
- Map integration
- Social features

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For support and questions:
- Email: support@propkart.com
- Documentation: [Project Wiki]
- Issues: [GitHub Issues]

---

*Last Updated: January 2025*
*Version: 1.0.0*
