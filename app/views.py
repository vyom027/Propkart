import os
import random
import string
import json
from io import BytesIO
from datetime import timedelta,datetime
from calendar import month_abbr

# Django Core
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q, Sum, Max, Count

# Custom Imports
from .decorators import modal_login_required
from .chat_service import ChatService
from .models import (
    SellerRequest, Property, PropertyImage, PropertyImportKey, Wishlist,
    Message, Notification, Enquiry, VisitRequest, PasswordResetToken, Contact,
    ChatSession, ChatMessage
)

# ReportLab (PDF Generation)
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage,
    PageBreak, Table, TableStyle, HRFlowable
)


def delete_property_images(property_instance):
    """Helper function to delete all images associated with a property"""
    try:
        images = PropertyImage.objects.filter(property=property_instance)
        deleted_count = 0
        for image in images:
            # Delete the file from filesystem
            if image.image and os.path.exists(image.image.path):
                os.remove(image.image.path)
                deleted_count += 1
        return deleted_count
    except Exception as e:
        print(f"Error deleting images for property {property_instance.id}: {str(e)}")
        return 0
from django.views.decorators.http import require_http_methods, require_POST
import json
from django.utils.dateparse import parse_datetime

User = get_user_model() 
def register(request):
    if request.method == 'POST':
        errors = []

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        address = request.POST.get('address')
        profile_picture = request.FILES.get('profile_picture')

        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username is already taken.")
        if not email:
            errors.append("Email is required.")
        elif User.objects.filter(email=email).exists():
            errors.append("Email is already registered.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not mobile:
            errors.append("Mobile number is required.")
        if not city:
            errors.append("City is required.")
        if not state:
            errors.append("State is required.")
        if not country:
            errors.append("Country is required.")

        if errors:
            for error in errors:
                messages.error(request, error)
            request.session['show_signup_modal'] = True
            return redirect('index')

        temp_file_path = None
        if profile_picture:
            fs = FileSystemStorage(location=settings.TEMP_MEDIA_ROOT)
            filename = fs.save(profile_picture.name, profile_picture)
            temp_file_path = os.path.join(settings.TEMP_MEDIA_ROOT, filename)

        otp = str(random.randint(100000, 999999))
        request.session['unverified_user_data'] = {
            'username': username,
            'email': email,
            'password': password,  
            'first_name': first_name,
            'last_name': last_name,
            'mobile': mobile,
            'city': city,
            'state': state,
            'country': country,
            'address': address,
            'temp_file_path': temp_file_path,
        }
        request.session['otp'] = otp

        subject = 'OTP for Registration'
        message = f'Your OTP for registration is {otp}.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        messages.info(request, "An OTP has been sent to your email. Please verify to complete registration.")
        request.session['show_otp_modal'] = True
        return redirect('index')

    return render(request, 'app/index.html')


def verify_otp(request):
    if request.method == 'POST':
        user_data = request.session.get('unverified_user_data')
        otp_digits = [request.POST.get(f'otp_{i}') for i in range(1, 7)]
        entered_otp = "".join(otp_digits)
        session_otp = request.session.get('otp')

        if not user_data or not session_otp:
            messages.error(request, "Session expired. Please try registering again.")
            return redirect('index')

        if entered_otp == session_otp:
            try:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                )
                if hasattr(user, 'mobile'):
                    user.mobile = user_data['mobile']
                if hasattr(user, 'address'):
                    user.address = user_data['address']
                if hasattr(user, 'city'):
                    user.city = user_data['city']
                if hasattr(user, 'state'):
                    user.state = user_data['state']
                if hasattr(user, 'country'):
                    user.country = user_data['country']
                user.save()

                temp_file_path = user_data.get('temp_file_path')
                if temp_file_path and os.path.exists(temp_file_path):
                    with open(temp_file_path, 'rb') as f:
                        user.profile_picture.save(os.path.basename(temp_file_path), File(f))
                    os.remove(temp_file_path)

                request.session.pop('unverified_user_data', None)
                request.session.pop('otp', None)

                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect('index')

            except Exception as e:
                messages.error(request, f"Registration failed: {e}")
                return redirect('index')

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            request.session['show_otp_modal'] = True
            return redirect('index')

    return redirect('index')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index') 
        else:
            return render(request, 'app/index.html', {'error': 'Invalid username or password.'})
    
    # For GET requests, redirect to home page since login is handled by modal
    return redirect('index')

@modal_login_required    
def logOutUser(request):
    if request.method == 'POST':
        from django.contrib.auth import logout
        logout(request)
        return redirect('index')  
    else:
        return redirect('index')  

def index(request):
    # Fetch the last 10 verified properties, excluding seller's own properties
    if request.user.is_authenticated:
        latest_properties = Property.objects.exclude(seller=request.user)\
            .filter(is_verified=True, is_hidden=False)\
            .order_by('-id')[:10].prefetch_related('images')
    else:
        latest_properties = Property.objects.filter(is_verified=True, is_hidden=False)\
            .order_by('-id')[:10].prefetch_related('images')

    show_otp_modal = request.session.pop('show_otp_modal', False)
    show_signup_modal = request.session.pop('show_signup_modal', False)
    # Calculate statistics for the counter section
    total_properties_count = Property.objects.count()
    verified_properties_count = Property.objects.filter(is_verified=True, is_hidden=False).count()
    total_views = Property.objects.aggregate(total_views=Sum('views'))['total_views'] or 0
    total_enquiries = Enquiry.objects.count()
    property_types_counts = Property.objects.filter(is_verified=True, is_hidden=False).values('type').annotate(count=Count('id'))

    context = {
        'latest_properties': latest_properties,
        'total_properties_count': total_properties_count,
        'verified_properties_count': verified_properties_count,
        'total_views': total_views,
        'total_enquiries': total_enquiries,
        'property_types_counts': property_types_counts,
    }

    return render(request, 'app/index.html', {
        'show_otp_modal': show_otp_modal,
        'show_signup_modal': show_signup_modal,
        'context': context,
    })

def about(request):
    return render(request,'app/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('contactUs')
            
        # Create contact message
        contact = Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            status='new'
        )
        
        # Send email notification to admin
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if admin_emails:
            context = {
                'contact': contact,
                'admin_url': request.build_absolute_uri(reverse('admin:app_contact_change', args=[contact.id]))
            }
            html_message = render_to_string('emails/new_contact_notification.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject=f'New Contact Form Submission: {subject}',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    html_message=html_message,
                    fail_silently=True
                )
            except Exception as e:
                print(f'Failed to send admin notification email: {str(e)}')
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contactUs')
        
    return render(request, 'app/contact.html')

@modal_login_required
def profile(request):
    return render(request,'app/profile.html')

@modal_login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.mobile = request.POST.get('mobile', user.mobile)
        user.city = request.POST.get('city', user.city)
        user.state = request.POST.get('state', user.state)
        user.country = request.POST.get('country', user.country)
        address = request.POST.get('address', '')
        
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            fs = FileSystemStorage()
            filename = fs.save(profile_picture.name, profile_picture)
            user.profile_picture.name = filename
        
        if address:
            user.address = address
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'app/profile.html')

def property_list(request):
    if request.user.is_authenticated:
        properties = Property.objects.exclude(seller=request.user)\
            .filter(is_verified=True, is_hidden=False)\
            .order_by('-id').prefetch_related('images')
        # Precompute wishlist saved ids for current page
        prop_ids = list(properties.values_list('id', flat=True))
        saved_ids = set(Wishlist.objects.filter(user=request.user, property_id__in=prop_ids).values_list('property_id', flat=True))
    else:
        properties = Property.objects.filter(is_verified=True, is_hidden=False)\
            .order_by('-id').prefetch_related('images')
        saved_ids = set()
    return render(request, 'app/properties.html', {'properties': properties, 'saved_ids': saved_ids})
 

@modal_login_required
def become_seller_request(request):
    if request.method == "POST":
        # Create a seller request
        seller_request = SellerRequest.objects.create(user=request.user)

        # Build verification link
        verification_link = request.build_absolute_uri(
            reverse("verify_seller", args=[seller_request.token])
        )

        subject = "Verify your seller account"
        html_content = render_to_string(
            "emails/seller_verify.html",
            {"user": request.user, "verification_link": verification_link}
        )
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email="PropKart <no-reply@example.com>",
            to=[request.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        messages.success(request, "Verification email sent! Please check your inbox.")
        return redirect("index")

@modal_login_required
def verify_seller(request, token):
    seller_request = get_object_or_404(SellerRequest, token=token)

    if not seller_request.is_valid():
        messages.error(request, "This verification link has expired.")
        return redirect("index")

    # Mark user as seller (example)
    user = seller_request.user
    user.is_seller = True  # assuming you have this field
    user.save()

    messages.success(request, "Your seller account has been verified!")
    return redirect("index")

@modal_login_required
def seller_dashboard(request):
    # Basic statistics
    prop_count = Property.objects.filter(seller=request.user).count()
    total_enquiries = Enquiry.objects.filter(property__seller=request.user).count()
    new_enquiries = Enquiry.objects.filter(property__seller=request.user, status='new').count()
    total_visits = VisitRequest.objects.filter(property__seller=request.user).count()
    pending_visits = VisitRequest.objects.filter(property__seller=request.user, status='pending').count()
    
    # Recent properties (last 5)
    recent_properties = Property.objects.filter(seller=request.user).order_by('-created_at')[:5].prefetch_related('images')
    
    # Recent messages (last 5)
    recent_messages = Message.objects.filter(receiver=request.user).order_by('-sent_at')[:5].select_related('sender', 'property')
    
    # Recent notifications (last 5)
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Pending approvals (properties awaiting verification)
    pending_approvals = Property.objects.filter(seller=request.user, is_verified=False).count()
    
    # Total views across all properties
    total_views = Property.objects.filter(seller=request.user).aggregate(total_views=Sum('views'))['total_views'] or 0
    
    context = {
        'prop_count': prop_count,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'total_visits': total_visits,
        'pending_visits': pending_visits,
        'pending_approvals': pending_approvals,
        'total_views': total_views,
        'recent_properties': recent_properties,
        'recent_messages': recent_messages,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'app/seller/seller-index.html', context)

@modal_login_required
def property_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        location = request.POST.get('location')
        property_type = request.POST.get('type')
        length = request.POST.get('length') or None
        width = request.POST.get('width') or None
        rooms = request.POST.get('rooms') or None
        bedrooms = request.POST.get('bedrooms') or None
        bathrooms = request.POST.get('bathrooms') or None
        furnished = True if request.POST.get('furnished') == 'on' else False

        # Create the Property instance
        property_instance = Property.objects.create(
            title=title,
            description=description,
            price=price,
            location=location,
            type=property_type,
            length=length,
            width=width,
            rooms=rooms,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            furnished=furnished,
            seller=request.user
        )

        # Handle uploaded images
        images = request.FILES.getlist('images')
        for image in images:
            PropertyImage.objects.create(
                property=property_instance,
                image=image
            )

        messages.success(request, "Property added successfully!")
        return redirect('seller_dashboard')  # or wherever you want to redirect after saving

    return render(request, 'app/seller/add_property.html')

@modal_login_required
def property_update(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id, seller=request.user)

    if request.method == 'POST':
        property_instance.title = request.POST.get('title', property_instance.title)
        property_instance.description = request.POST.get('description', property_instance.description)
        property_instance.price = request.POST.get('price', property_instance.price)
        property_instance.location = request.POST.get('location', property_instance.location)
        property_instance.type = request.POST.get('type', property_instance.type)
        property_instance.length = request.POST.get('length') or property_instance.length
        property_instance.width = request.POST.get('width') or property_instance.width
        property_instance.rooms = request.POST.get('rooms') or property_instance.rooms
        property_instance.bedrooms = request.POST.get('bedrooms') or property_instance.bedrooms
        property_instance.bathrooms = request.POST.get('bathrooms') or property_instance.bathrooms
        property_instance.furnished = True if request.POST.get('furnished') == 'on' else False

        property_instance.save()

        images = request.FILES.getlist('images')
        for image in images:
            PropertyImage.objects.create(
                property=property_instance,
                image=image
            )

        messages.success(request, "Property updated successfully!")
        return redirect('my_properties')
    


# ===================================================================
# STYLING CONSTANTS (Refined for Premium Look)
# ===================================================================
COLOR_PRIMARY = colors.HexColor('#c0a062')       # Brushed Gold
COLOR_PRIMARY_LIGHT = colors.HexColor('#f3efe5') # Light Gold/Beige (For accents)
COLOR_INK = colors.HexColor('#222222')           # Charcoal (Main Text)
COLOR_BG = colors.HexColor('#f9f7f4')             # Warm Off-white (Overall background)
COLOR_GRAY_LIGHT = colors.HexColor('#e9e9e9')
COLOR_GRAY_DARK = colors.HexColor('#444444')
COLOR_WHITE = colors.white

FONT_BOLD = 'Helvetica-Bold'
FONT_NORMAL = 'Helvetica'
FONT_ITALIC = 'Helvetica-Oblique'

# Register fonts (if not already registered)
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    # if FONT_NORMAL not in pdfmetrics.getRegisteredFontNames():
    #     pdfmetrics.registerFont(TTFont(FONT_NORMAL, 'DejaVuSans.ttf'))
    # if FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
    #     pdfmetrics.registerFont(TTFont(FONT_BOLD, 'DejaVuSans-Bold.ttf'))
except Exception as e:
    print(f"Error registering fonts: {e}")

MARGIN = 2.0 * cm # Increased margin for a cleaner look
PAGE_WIDTH, PAGE_HEIGHT = A4
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)
FOOTER_HEIGHT = 50 # Reduced footer height

# ===================================================================
# UTILITY FUNCTIONS
# ===================================================================

def _safe_image(path):
    """Load image safely, return None if fails"""
    try:
        if not path or not os.path.exists(path):
            return None
        return ImageReader(path)
    except Exception:
        return None

def _scale_to_fit(img_w, img_h, max_w, max_h):
    """Scale image to fit within bounds, maintaining aspect ratio"""
    if img_w <= 0 or img_h <= 0:
        return 0, 0
    ratio = min(max_w / float(img_w), max_h / float(img_h))
    return img_w * ratio, img_h * ratio

def _scale_to_fill(img_w, img_h, target_w, target_h):
    """Scale image to fill bounds, maintaining aspect ratio (cropping)"""
    if img_w <= 0 or img_h <= 0:
        return 0, 0
    ratio = max(target_w / float(img_w), target_h / float(img_h))
    return img_w * ratio, img_h * ratio

def _format_price(value):
    """Format price to ₹X,XX,XXX"""
    try:
        # Enforce comma separation and zero decimal points for clean presentation
        return f"₹{float(value):,.0f}" 
    except (ValueError, TypeError):
        return "N/A"

@modal_login_required
def property_delete(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)

    # Optional: if you had seller field you would also check
    # if property_instance.seller == request.user
    if not property_instance:
        messages.error(request, "Property not found or you do not have permission to delete it.")
        return redirect('my_properties')

    if request.method == 'POST':
        # Delete associated images from filesystem
        deleted_images_count = delete_property_images(property_instance)
        
        # Delete the property (this will also delete PropertyImage records due to CASCADE)
        property_instance.delete()
        
        if deleted_images_count > 0:
            messages.success(request, f"Property and {deleted_images_count} associated images deleted successfully!")
        else:
            messages.success(request, "Property deleted successfully!")
        return redirect('my_properties')  # or wherever you list properties

    messages.error(request, "Invalid request.")
    return redirect('my_properties')

@modal_login_required
def export_wishlist_pdf(request):
    user_wishlist = Wishlist.objects.filter(user=request.user).select_related('property', 'property__seller').prefetch_related('property__images')

    # === COLORS & STYLES ===
    COLOR_PRIMARY = colors.HexColor("#5fbf7f")     # PropKart light green
    COLOR_SECONDARY = colors.HexColor("#c0a062")   # Golden accent
    COLOR_TEXT = colors.HexColor("#222222")
    COLOR_GRAY = colors.HexColor("#555555")
    COLOR_BG = colors.whitesmoke

    FONT_BOLD = "Helvetica-Bold"
    FONT_NORMAL = "Helvetica"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Custom paragraph styles
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"],
        fontName=FONT_BOLD, fontSize=26, textColor=COLOR_PRIMARY,
        alignment=TA_CENTER, spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        "SubTitle", parent=styles["Normal"],
        fontName=FONT_NORMAL, fontSize=12, textColor=COLOR_GRAY,
        alignment=TA_CENTER, spaceAfter=30
    )
    header_style = ParagraphStyle(
        "Header", parent=styles["Heading2"],
        fontName=FONT_BOLD, fontSize=16, textColor=COLOR_SECONDARY,
        alignment=TA_LEFT, spaceAfter=10
    )
    normal_style = ParagraphStyle(
        "NormalText", parent=styles["Normal"],
        fontName=FONT_NORMAL, fontSize=10, textColor=COLOR_TEXT,
        leading=14, spaceAfter=6
    )

    # === STORY SETUP ===
    story = []

    # HEADER
    story.append(Paragraph("Your PropKart Wishlist", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%b %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", color=COLOR_SECONDARY, thickness=2))
    story.append(Spacer(1, 0.4*inch))

    # EMPTY STATE
    if not user_wishlist:
        story.append(Paragraph("Your wishlist is currently empty.", normal_style))
        doc.build(story)
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=wishlist.pdf"
        })

    # === PROPERTY CARDS ===
    for item in user_wishlist:
        prop = item.property

        # Property Title
        story.append(Paragraph(prop.title, header_style))

        # Property Images
        property_images = prop.images.all()
        if property_images:
            # Create a list to hold image flowables
            image_flowables = []
            for img_obj in property_images:
                img_reader = _safe_image(img_obj.image.path)
                if img_reader:
                    img_w, img_h = img_reader.getSize()
                    max_w, max_h = 2.5*inch, 2*inch # Max size for images in a 2-column layout
                    scale = min(max_w / img_w, max_h / img_h)
                    image_flowables.append(ReportLabImage(img_obj.image.path, width=img_w * scale, height=img_h * scale))

            # Arrange images in a 2-column table
            if image_flowables:
                # Pad with None to make it a multiple of 2 for table rows
                while len(image_flowables) % 2 != 0:
                    image_flowables.append(Spacer(1,0.1*inch))

                # Create rows for the table
                image_rows = []
                for i in range(0, len(image_flowables), 2):
                    image_rows.append([image_flowables[i], image_flowables[i+1]])

                image_table = Table(image_rows, colWidths=[4*cm, 4*cm]) # Adjust colWidths as needed
                image_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(image_table)
                story.append(Spacer(1, 0.2*inch))

        # Property Info (Table)
        data = [
            ["💰 Price", f"{_format_price(prop.price)}"],
            ["📍 Location", f"{prop.location}, {prop.city}, {prop.state}, {prop.country}"],
            ["🏡 Type", prop.get_type_display()],
            ["🛏 Bedrooms", prop.bedrooms or "N/A"],
            ["🚿 Bathrooms", prop.bathrooms or "N/A"],
            ["📏 Area", f"{prop.length or 'N/A'} x {prop.width or 'N/A'} sqft"],
            ["🪑 Furnished", "Yes" if prop.furnished else "No"],
            ["👤 Seller Name", f"{prop.seller.first_name} {prop.seller.last_name}"],
            ["📧 Seller Email", prop.seller.email],
            ["📞 Seller Mobile", prop.seller.mobile or "N/A"],
        ]

        table = Table(data, colWidths=[3*cm, 11*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("FONTNAME", (0, 0), (-1, -1), FONT_NORMAL),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), COLOR_SECONDARY),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))

        # Description
        story.append(Paragraph("<b>Description:</b>", normal_style))
        story.append(Paragraph(prop.description or "No description provided.", normal_style))
        story.append(Spacer(1, 0.4*inch))
        story.append(HRFlowable(width="100%", color=COLOR_GRAY, thickness=0.8))
        story.append(Spacer(1, 0.4*inch))

    # === BUILD PDF ===
    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=wishlist.pdf"
    })

@modal_login_required
def properties_bulk_delete(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request.")
        return redirect('my_properties')
    ids = request.POST.getlist('property_ids')
    if not ids:
        messages.warning(request, "No properties selected.")
        return redirect('my_properties')
    
    qs = Property.objects.filter(id__in=ids, seller=request.user)
    total_deleted_images = 0
    
    # Delete images for each property before deleting the properties
    for property_instance in qs:
        deleted_images_count = delete_property_images(property_instance)
        total_deleted_images += deleted_images_count
    
    deleted_count = qs.count()
    qs.delete()
    
    if total_deleted_images > 0:
        messages.success(request, f"Deleted {deleted_count} properties and {total_deleted_images} associated images.")
    else:
        messages.success(request, f"Deleted {deleted_count} properties.")
    return redirect('my_properties')

def seller_messages(request):
    if not getattr(request.user, 'is_seller', False):
        return redirect('seller_dashboard')

    # Filters from query
    property_id = request.GET.get('property')
    buyer_id = request.GET.get('buyer')

    base_qs = Message.objects.filter(receiver=request.user)

    # Threads: group by (property, sender) with last message and unread count
    thread_keys = (
        base_qs.values('property_id', 'sender_id')
              .annotate(last_time=Max('sent_at'))
              .order_by('-last_time')
    )

    threads = []
    for key in thread_keys:
        last_msg = (base_qs.filter(property_id=key['property_id'], sender_id=key['sender_id'])
                            .order_by('-sent_at')
                            .select_related('property', 'sender')
                            .first())
        if not last_msg:
            continue
        unread_count = base_qs.filter(property_id=key['property_id'], sender_id=key['sender_id'], is_read=False).count()
        threads.append({
            'last': last_msg,
            'unread_count': unread_count,
        })

    # Selected conversation
    conversation = []
    related_enquiries = []
    if property_id and buyer_id:
        from django.db.models import Q
        conversation_qs = (
            Message.objects
            .filter(property_id=property_id)
            .filter(
                Q(sender_id=buyer_id, receiver=request.user) |
                Q(sender=request.user, receiver_id=buyer_id)
            )
            .order_by('sent_at')
            .select_related('sender', 'property')
        )
        conversation = list(conversation_qs)
        # Mark as read
        conversation_qs.filter(is_read=False).update(is_read=True)
        
        # Get related enquiries for this property and buyer
        try:
            buyer_user = User.objects.get(id=buyer_id)
            related_enquiries = Enquiry.objects.filter(
                property_id=property_id,
                buyer_email=buyer_user.email
            ).order_by('-created_at')
        except User.DoesNotExist:
            pass
        
        # Also check for enquiries by email if no user match
        if not related_enquiries:
            # Get enquiries for this property that might be from the same person
            related_enquiries = Enquiry.objects.filter(
                property_id=property_id
            ).order_by('-created_at')[:3]  # Show recent enquiries for context

    context = {
        'threads': threads,
        'conversation': conversation,
        'related_enquiries': related_enquiries,
        'selected_property_id': int(property_id) if property_id else None,
        'selected_buyer_id': int(buyer_id) if buyer_id else None,
    }
    return render(request, 'app/seller/messages.html', context)

@modal_login_required
def my_properties(request):
    # Get properties of the logged-in user
    properties = Property.objects.filter(seller=request.user).order_by('-id')
    total_views = properties.aggregate(total_views=Sum('views'))['total_views'] or 0

    return render(request, 'app/seller/my_properties.html', {
        'properties': properties,
        'total_views': total_views,
    })

@modal_login_required
def seller_enquiries(request):
    # Get all enquiries for properties owned by current seller
    enquiries = Enquiry.objects.filter(
        property__seller=request.user
    ).select_related('property').order_by('-created_at')
    
    # Get enquiry statistics
    total_enquiries = enquiries.count()
    new_enquiries = enquiries.filter(status='new').count()
    replied_enquiries = enquiries.filter(status='replied').count()
    
    context = {
        'enquiries': enquiries,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'replied_enquiries': replied_enquiries,
    }
    return render(request, 'app/seller/enquiries.html', context)

def seller_analytics(request):
    # Ensure user is a seller
    if not request.user.is_seller:
        return redirect('home')
    
    seller = request.user
    
    # Get current date info
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_week_start = now - timedelta(days=now.weekday())
    
    # === STATS OVERVIEW ===
    
    # 1. Total Properties
    total_properties = Property.objects.filter(seller=seller).count()
    
    # 2. New Properties This Month
    new_properties = Property.objects.filter(
        seller=seller,
        created_at__gte=current_month_start
    ).count()
    
    # 3. Total Views
    total_views = Property.objects.filter(seller=seller).aggregate(
        total=Sum('views')
    )['total'] or 0
    
    # 4. Views Growth (current month vs previous month)
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    current_month_properties = Property.objects.filter(
        seller=seller,
        created_at__gte=current_month_start
    )
    current_month_views = current_month_properties.aggregate(total=Sum('views'))['total'] or 0
    
    previous_month_properties = Property.objects.filter(
        seller=seller,
        created_at__gte=previous_month_start,
        created_at__lt=current_month_start
    )
    previous_month_views = previous_month_properties.aggregate(total=Sum('views'))['total'] or 1
    
    if previous_month_views > 0:
        views_growth = round(((current_month_views - previous_month_views) / previous_month_views) * 100, 1)
    else:
        views_growth = 0
    
    # 5. Visit Requests (total)
    visit_requests = VisitRequest.objects.filter(
        property__seller=seller
    ).count()
    
    # 6. Visit Requests Growth (this week vs last week)
    last_week_start = current_week_start - timedelta(days=7)
    
    current_week_visits = VisitRequest.objects.filter(
        property__seller=seller,
        created_at__gte=current_week_start
    ).count()
    
    last_week_visits = VisitRequest.objects.filter(
        property__seller=seller,
        created_at__gte=last_week_start,
        created_at__lt=current_week_start
    ).count()
    
    if last_week_visits > 0:
        visit_requests_growth = round(((current_week_visits - last_week_visits) / last_week_visits) * 100, 1)
    else:
        visit_requests_growth = 0
    
    # 7. Total Enquiries
    total_enquiries = Enquiry.objects.filter(
        property__seller=seller
    ).count()
    
    # 8. New Enquiries (this month)
    new_enquiries = Enquiry.objects.filter(
        property__seller=seller,
        created_at__gte=current_month_start
    ).count()
    
    # === CHART DATA ===
    
    # Generate last 6 months
    months = []
    month_labels = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        months.append(month_start)
        month_labels.append(month_abbr[month_start.month])
    
    # 9. Enquiries Trend Data (Line Chart)
    enquiry_new = []
    enquiry_replied = []
    enquiry_closed = []
    
    for month_start in months:
        # Calculate next month
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        
        new_count = Enquiry.objects.filter(
            property__seller=seller,
            status='new',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        replied_count = Enquiry.objects.filter(
            property__seller=seller,
            status='replied',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        closed_count = Enquiry.objects.filter(
            property__seller=seller,
            status='closed',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        enquiry_new.append(new_count)
        enquiry_replied.append(replied_count)
        enquiry_closed.append(closed_count)
    
    # 10. Property Distribution by Type (Doughnut Chart)
    property_distribution = Property.objects.filter(seller=seller).values('type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    property_types = []
    property_counts = []
    
    for item in property_distribution:
        # Get readable name from TYPE_CHOICES
        type_display = dict(Property.TYPE_CHOICES).get(item['type'], item['type'].title())
        property_types.append(type_display)
        property_counts.append(item['count'])
    
    # 11. Visit Requests by Status (Bar Chart)
    visit_pending = []
    visit_approved = []
    visit_completed = []
    visit_cancelled = []
    
    for month_start in months:
        # Calculate next month
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        
        pending = VisitRequest.objects.filter(
            property__seller=seller,
            status='pending',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        approved = VisitRequest.objects.filter(
            property__seller=seller,
            status='approved',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        completed = VisitRequest.objects.filter(
            property__seller=seller,
            status='completed',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        cancelled = VisitRequest.objects.filter(
            property__seller=seller,
            status='cancelled',
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        visit_pending.append(pending)
        visit_approved.append(approved)
        visit_completed.append(completed)
        visit_cancelled.append(cancelled)
    
    # Build context
    context = {
        # Stats Overview
        'total_properties': total_properties,
        'new_properties': new_properties,
        'total_views': total_views,
        'views_growth': views_growth,
        'visit_requests': visit_requests,
        'visit_requests_growth': visit_requests_growth,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        
        # Enquiries Trend Chart
        'enquiry_months': json.dumps(month_labels),
        'enquiry_data': {
            'new': enquiry_new,
            'replied': enquiry_replied,
            'closed': enquiry_closed,
        },
        
        # Property Distribution Chart
        'property_types': json.dumps(property_types),
        'property_counts': property_counts,
        
        # Visit Requests Chart
        'visit_months': json.dumps(month_labels),
        'visit_data': {
            'pending': visit_pending,
            'approved': visit_approved,
            'completed': visit_completed,
            'cancelled': visit_cancelled,
        },
    }
    
    return render(request, 'app/seller/analytics.html', context)
def seller_support(request):
    support_info = {
        'email': 'Hl9kX@example.com',
        'phone': '+1 (123) 456-7890',
    }
    return render(request, 'app/seller/support.html', {'support_info': support_info})

@modal_login_required
def wishlist_toggle(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
    try:
        import json
        data = json.loads(request.body.decode('utf-8'))
        property_id = int(data.get('property_id'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid payload'}, status=400)

    prop = get_object_or_404(Property.objects.filter(is_verified=True, is_hidden=False), id=property_id)
    if prop.seller_id == request.user.id:
        return JsonResponse({'success': False, 'error': 'Cannot save your own property'}, status=400)

    obj, created = Wishlist.objects.get_or_create(user=request.user, property=prop)
    if not created:
        obj.delete()
        return JsonResponse({'success': True, 'saved': False})
    return JsonResponse({'success': True, 'saved': True})

@modal_login_required
def wishlist_list(request):
    items = Wishlist.objects.filter(user=request.user).select_related('property', 'property__seller').prefetch_related('property__images').order_by('-added_at')
    return render(request, 'app/wishlist.html', {'items': items})

def seller_profile_edit(request):
    return render(request, 'app/seller/profile-edit.html')

def seller_send_message(request, recipient_id):
    if request.method == 'POST':
        message = request.POST.get('message')
        print(f"Message to {recipient_id}: {message}")
        
    return render(request, 'app/seller/send_message.html', {'recipient_id': recipient_id})

def increment_property_view(request, property_id):
    property_instance = get_object_or_404(Property.objects.filter(is_verified=True, is_hidden=False), id=property_id)

    if request.user.is_authenticated:
        identifier = f"user_{request.user.id}"
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        identifier = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    if identifier not in property_instance.viewers:
        property_instance.viewers.append(identifier)
        property_instance.views += 1
        property_instance.save(update_fields=['views', 'viewers'])

    return JsonResponse({"views": property_instance.views})

@modal_login_required
def seller_import_properties(request):
    if not getattr(request.user, 'is_seller', False):
        messages.error(request, "Only sellers can import properties.")
        return redirect('seller_dashboard')

    if request.method == 'POST' and request.FILES.get('csv_file') and request.FILES.get('images_zip'):
        import csv, io, re, uuid as uuidlib, zipfile, os, tempfile
        from decimal import Decimal, InvalidOperation
        from PIL import Image
        from django.core.files.base import ContentFile

        csv_file = request.FILES['csv_file']
        zip_file = request.FILES['images_zip']
        
        # Validate ZIP file size (max 50MB)
        MAX_ZIP_MB = 500
        MAX_ZIP_BYTES = MAX_ZIP_MB * 1024 * 1024
        if zip_file.size > MAX_ZIP_BYTES:
            messages.error(request, f'ZIP file too large. Maximum size: {MAX_ZIP_MB}MB')
            return redirect('seller_import_properties')
        
        try:
            text = csv_file.read().decode('utf-8')
        except Exception:
            messages.error(request, 'Invalid CSV encoding. Please upload UTF-8 CSV.')
            return redirect('seller_import_properties')

        reader = csv.DictReader(io.StringIO(text))

        processed = created = skipped = failed = 0
        image_processed = image_failed = 0
        errors = []

        ALLOWED_TYPES = { 'apartment','house','land','villa','commercial' }
        ALLOWED_EXT = { '.jpg', '.jpeg', '.png', '.webp' }
        MAX_IMAGE_MB = 10
        MAX_IMAGE_BYTES = MAX_IMAGE_MB * 1024 * 1024
        MAX_IMAGES = 10

        # Extract ZIP file to temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_images = {}
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Check for suspicious files (zip bombs, etc.)
                total_size = sum(info.file_size for info in zip_ref.infolist())
                if total_size > MAX_ZIP_BYTES * 2:  # Allow some compression overhead
                    messages.error(request, f'ZIP file contains too much data. Maximum: {MAX_ZIP_MB * 2}MB')
                    return redirect('seller_import_properties')
                
                # Extract all files to temp directory
                zip_ref.extractall(temp_dir)
                
                # Create a mapping of filename to file path
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in ALLOWED_EXT:
                            zip_images[file] = os.path.join(root, file)
                
                if not zip_images:
                    messages.error(request, 'No valid image files found in ZIP. Supported formats: JPG, JPEG, PNG, WEBP')
                    return redirect('seller_import_properties')
                    
        except zipfile.BadZipFile:
            messages.error(request, 'Invalid ZIP file format.')
            return redirect('seller_import_properties')
        except Exception as e:
            messages.error(request, f'Error processing ZIP file: {str(e)}')
            return redirect('seller_import_properties')

        for idx, row in enumerate(reader, start=2):  # header is line 1
            processed += 1
            row_errors = []

            external_id = (row.get('external_id') or '').strip()
            title = (row.get('title') or '').strip()
            description = (row.get('description') or '').strip()
            price_raw = (row.get('price') or '').strip()
            location = (row.get('location') or '').strip()
            city = (row.get('city') or '').strip()
            state = (row.get('state') or '').strip()
            country = (row.get('country') or '').strip()
            type_raw = (row.get('type') or '').strip().lower()
            furnished_raw = (row.get('furnished') or '').strip().lower()
            images_raw = (row.get('images') or '').strip()

            # Check all required fields
            required_fields = {
                'external_id': external_id,
                'title': title,
                'description': description,
                'price': price_raw,
                'location': location,
                'city': city,
                'state': state,
                'country': country,
                'type': type_raw,
                'length': row.get('length', '').strip(),
                'width': row.get('width', '').strip(),
                'rooms': row.get('rooms', '').strip(),
                'bedrooms': row.get('bedrooms', '').strip(),
                'bathrooms': row.get('bathrooms', '').strip(),
                'furnished': furnished_raw,
                'images': images_raw
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                failed += 1
                errors.append((idx, external_id, f'Missing required fields: {", ".join(missing_fields)}'))
                continue

            if type_raw not in ALLOWED_TYPES:
                failed += 1
                errors.append((idx, external_id, f'Invalid type: {type_raw}'))
                continue

            try:
                price = Decimal(price_raw)
                if price <= 0:
                    raise InvalidOperation
            except Exception:
                failed += 1
                errors.append((idx, external_id, 'Invalid price'))
                continue

            def parse_int(v):
                v = (v or '').strip()
                if not v:
                    raise ValueError('Required field cannot be empty')
                return int(v)

            def parse_decimal(v):
                v = (v or '').strip()
                if not v:
                    raise ValueError('Required field cannot be empty')
                return Decimal(v)

            try:
                length = parse_decimal(row.get('length'))
                width = parse_decimal(row.get('width'))
                rooms = parse_int(row.get('rooms'))
                bedrooms = parse_int(row.get('bedrooms'))
                bathrooms = parse_int(row.get('bathrooms'))
            except Exception as e:
                failed += 1
                errors.append((idx, external_id, f'Invalid numeric field: {str(e)}'))
                continue
            furnished = furnished_raw in {'true','1','yes'}

            # duplicate check
            if PropertyImportKey.objects.filter(seller=request.user, external_id=external_id).exists():
                skipped += 1
                continue

            # create property
            prop = Property.objects.create(
                seller=request.user,
                title=title,
                description=description,
                price=price,
                location=location,
                city=city,
                state=state,
                country=country,
                type=type_raw,
                length=length,
                width=width,
                rooms=rooms,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                furnished=furnished,
            )

            saved_images = 0
            missing_images = []
            if images_raw:
                image_filenames = [f.strip() for f in images_raw.split(',') if f.strip()]
                for filename in image_filenames[:MAX_IMAGES]:
                    if filename not in zip_images:
                        image_failed += 1
                        missing_images.append(filename)
                        continue
                    
                    try:
                        image_path = zip_images[filename]
                        
                        # Check file size
                        file_size = os.path.getsize(image_path)
                        if file_size > MAX_IMAGE_BYTES:
                            image_failed += 1
                            continue
                        
                        # Verify image
                        try:
                            with Image.open(image_path) as img:
                                img.verify()
                        except Exception:
                            image_failed += 1
                            continue
                        
                        # Read file content
                        with open(image_path, 'rb') as f:
                            content = f.read()
                        
                        # Get file extension
                        _, ext = os.path.splitext(filename)
                        if ext.lower() not in ALLOWED_EXT:
                            image_failed += 1
                            continue
                        
                        # Create unique filename
                        unique_filename = f"{uuidlib.uuid4()}{ext}"
                        
                        # Save image
                        PropertyImage.objects.create(
                            property=prop,
                            image=ContentFile(content, name=unique_filename)
                        )
                        saved_images += 1
                        image_processed += 1
                        
                    except Exception as e:
                        image_failed += 1
                        continue

            if saved_images == 0:
                # no valid images -> rollback this property
                # Delete any images that might have been created
                delete_property_images(prop)
                prop.delete()
                failed += 1
                if missing_images:
                    errors.append((idx, external_id, f'Missing images: {", ".join(missing_images)}'))
                else:
                    errors.append((idx, external_id, 'No valid images'))
                continue

            # record external_id for duplicates
            PropertyImportKey.objects.create(seller=request.user, external_id=external_id, property=prop)
            created += 1

        # Cleanup temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
        
        messages.success(request, f"Imported: {created}, Skipped: {skipped}, Failed: {failed}, Images OK: {image_processed}, Images Failed: {image_failed}")
        if errors:
            # Display a brief message; optionally generate a downloadable CSV later
            messages.warning(request, f"Errors in {len(errors)} rows (first shown): {errors[:3]}")
        return redirect('my_properties')

    return render(request, 'app/seller/import_properties.html')

# Buyer Property Detail View
def property_detail(request, property_id):
    property_obj = get_object_or_404(Property.objects.select_related('seller').filter(is_verified=True, is_hidden=False), id=property_id)
    images = PropertyImage.objects.filter(property=property_obj)
    context = {
        'property': property_obj,
        'images': images,
    }
    return render(request, 'app/property-single.html', context)

@require_http_methods(["GET"])
def property_brochure_pdf(request, property_id):
    import os
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    # ===================================================================
    # STYLING CONSTANTS (Refined for Premium Look)
    # ===================================================================
    COLOR_PRIMARY = colors.HexColor('#c0a062')       # Brushed Gold
    COLOR_PRIMARY_LIGHT = colors.HexColor('#f3efe5') # Light Gold/Beige (For accents)
    COLOR_INK = colors.HexColor('#222222')           # Charcoal (Main Text)
    COLOR_BG = colors.HexColor('#f9f7f4')             # Warm Off-white (Overall background)
    COLOR_GRAY_LIGHT = colors.HexColor('#e9e9e9')
    COLOR_GRAY_DARK = colors.HexColor('#444444')
    COLOR_WHITE = colors.white

    FONT_BOLD = 'Helvetica-Bold'
    FONT_NORMAL = 'Helvetica'
    FONT_ITALIC = 'Helvetica-Oblique'

    MARGIN = 2.0 * cm # Increased margin for a cleaner look
    PAGE_WIDTH, PAGE_HEIGHT = A4
    CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)
    FOOTER_HEIGHT = 50 # Reduced footer height

    # ===================================================================
    # UTILITY FUNCTIONS
    # ===================================================================



    def _scale_to_fill(img_w, img_h, target_w, target_h):
        """Scale image to fill bounds, maintaining aspect ratio (cropping)"""
        if img_w <= 0 or img_h <= 0:
            return 0, 0
        ratio = max(target_w / float(img_w), target_h / float(img_h))
        return img_w * ratio, img_h * ratio

    def _format_price(value):
        """Format price to ₹X,XX,XXX"""
        try:
            # Enforce comma separation and zero decimal points for clean presentation
            return f"₹{float(value):,.0f}" 
        except (ValueError, TypeError):
            return str(value)

    # ===================================================================
    # DRAWING PRIMITIVES (Refined)
    # ===================================================================

    def _draw_page_header(c, brand_name, page_num=None):
        """Draws the clean, elevated header with the Gold badge."""
        y = PAGE_HEIGHT - 35
        c.saveState()
        
        # Background (White box for a clean header area)
        c.setFillColor(COLOR_WHITE)
        c.rect(0, PAGE_HEIGHT - 70, PAGE_WIDTH, 70, fill=1, stroke=0)
        
        # Brand Name (Charcoal)
        c.setFont(FONT_BOLD, 22)
        c.setFillColor(COLOR_INK)
        c.drawString(MARGIN, y, brand_name)
        
        # Brochure Badge (Gold background, White text)
        badge_text = "PROPERTY BROCHURE"
        badge_width = c.stringWidth(badge_text, FONT_BOLD, 9) + 24
        c.setFillColor(COLOR_PRIMARY)
        c.roundRect(PAGE_WIDTH - MARGIN - badge_width, y - 10, badge_width, 20, 10, fill=1, stroke=0)
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(COLOR_WHITE)
        c.drawCentredString(PAGE_WIDTH - MARGIN - (badge_width / 2), y - 4, badge_text)

        # Page Number
        if page_num is not None:
            c.setFont(FONT_NORMAL, 10)
            c.setFillColor(COLOR_GRAY_DARK)
            c.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 55, f"Page {page_num}")
        
        # Clean Divider Line
        c.setStrokeColor(COLOR_GRAY_LIGHT)
        c.setLineWidth(1)
        c.line(MARGIN, PAGE_HEIGHT - 70, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 70)
        
        c.restoreState()
        return PAGE_HEIGHT - 70 # Return starting Y for content

    def _draw_page_footer(c):
        """Draws the subtle, branded footer."""
        c.saveState()
        
        # Simple Gold Divider Line
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(1.5)
        c.line(MARGIN, FOOTER_HEIGHT + 15, PAGE_WIDTH - MARGIN, FOOTER_HEIGHT + 15)
        
        # Text
        c.setFont(FONT_NORMAL, 9)
        c.setFillColor(COLOR_GRAY_DARK)
        c.drawString(MARGIN, FOOTER_HEIGHT - 5, "Confidential Property Details - PropKart")
        c.drawRightString(PAGE_WIDTH - MARGIN, FOOTER_HEIGHT - 5, "© All Rights Reserved")
        
        c.restoreState()

    def _draw_hero(c, x, y, width, prop, hero_img_obj):
        """Draws the hero section with a focus on hierarchy."""
        c.saveState()
        
        y -= 1.0 * cm # Extra space from header

        # --- Property Title ---
        style_title = ParagraphStyle(
            name='Title', fontName=FONT_BOLD, fontSize=26,
            textColor=COLOR_INK, leading=30, spaceAfter=8
        )
        p_title = Paragraph(prop.title, style_title)
        w, h_title = p_title.wrapOn(c, width * 0.7, 100) # Give it 70% width
        p_title.drawOn(c, x, y - h_title)
        y -= (h_title + 0.2 * cm)
        
        # --- Address ---
        address_text = f"{prop.location}, {prop.city}, {prop.state}"
        style_address = ParagraphStyle(
            name='Address', fontName=FONT_NORMAL, fontSize=12,
            textColor=COLOR_GRAY_DARK, leading=16
        )
        p_address = Paragraph(address_text, style_address)
        w, h_address = p_address.wrapOn(c, width * 0.7, 50)
        p_address.drawOn(c, x, y - h_address)
        y_text_end = y - h_address # End of text block

        # --- Price Tag (Gold Box) ---
        price_box_height = 50
        price_box_width = width * 0.35 # Fixed width
        price_box_x = x + width - price_box_width
        price_box_y = PAGE_HEIGHT - 70 - 1.0 * cm - price_box_height # Align with title block top

        c.setFillColor(COLOR_PRIMARY)
        c.roundRect(price_box_x, price_box_y, price_box_width, price_box_height, 8, fill=1, stroke=0)
        
        c.setFont(FONT_BOLD, 10)
        c.setFillColor(colors.white)
        c.drawString(price_box_x + 15, price_box_y + 30, "ASKING PRICE")
        
        c.setFont(FONT_BOLD, 18)
        c.drawString(price_box_x + 15, price_box_y + 10, _format_price(prop.price))
        
        y = y_text_end - (1.0 * cm) # Start of image space below text

        # --- Hero Image (with large rounding) ---
        if hero_img_obj:
            try:
                img_h_target = 200 # Fixed height
                img_w, img_h = hero_img_obj.getSize()
                draw_w, draw_h = _scale_to_fit(img_w, img_h, width, img_h_target)
                
                img_x = x + (width - draw_w) / 2
                
                # Clip path for rounded corners
                c.saveState()
                p = c.beginPath()
                p.roundRect(img_x, y - draw_h, draw_w, draw_h, 12) # Larger radius
                c.clipPath(p, stroke=0, fill=0)
                c.drawImage(hero_img_obj, img_x, y - draw_h, width=draw_w, height=draw_h, preserveAspectRatio=True)
                c.restoreState()
                
                y -= (draw_h + (1.0 * cm))
            except Exception:
                pass
                
        c.restoreState()
        return y

    def _draw_section_title(c, x, y, title):
        """Draws the section title with an elegant Gold underline."""
        c.saveState()
        
        y -= (0.5 * cm)
        
        # Title Text
        c.setFont(FONT_BOLD, 18)
        c.setFillColor(COLOR_INK)
        c.drawString(x, y, title.upper())
        
        # Gold Underline
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(2)
        c.line(x, y - 5, x + c.stringWidth(title.upper(), FONT_BOLD, 18), y - 5)
        
        c.restoreState()
        return y - (0.8 * cm)

    def _draw_specs(c, x, y, width, specs):
        """Draws the spec grid with a cleaner card design."""
        c.saveState()
        
        num_cols = 4
        gap = 0.5 * cm
        col_width = (width - (num_cols - 1) * gap) / num_cols
        row_height = 65
        
        current_x = x
        current_y = y
        
        for i, (icon, label, value) in enumerate(specs):
            if i > 0 and i % num_cols == 0:
                current_x = x
                current_y -= (row_height + gap)
            
            # Card background (Subtle light beige)
            c.setFillColor(COLOR_PRIMARY_LIGHT)
            c.roundRect(current_x, current_y - row_height, col_width, row_height, 6, fill=1, stroke=0)
            
            # Icon/Value
            c.setFont(FONT_BOLD, 16)
            c.setFillColor(COLOR_PRIMARY)
            c.drawString(current_x + 10, current_y - 25, str(value)[:18])
            
            # Label
            c.setFont(FONT_NORMAL, 9)
            c.setFillColor(COLOR_GRAY_DARK)
            c.drawString(current_x + 10, current_y - 45, label.upper())
            
            current_x += (col_width + gap)
            
        num_rows = (len(specs) + num_cols - 1) // num_cols
        final_y = y - (num_rows * row_height) - ((num_rows - 1) * gap)
        
        c.restoreState()
        return final_y - (0.5 * cm)

    def _draw_paragraph(c, x, y, text, width, font_size=11, color=COLOR_GRAY_DARK):
        """Draws a wrapped paragraph."""
        c.saveState()
        style = ParagraphStyle(
            name='Body', fontName=FONT_NORMAL, fontSize=font_size,
            textColor=color, alignment=TA_LEFT, leading=font_size * 1.6
        )
        p = Paragraph(text.replace('\n', '<br/>'), style)
        w, h = p.wrapOn(c, width, PAGE_HEIGHT)
        p.drawOn(c, x, y - h)
        c.restoreState()
        return y - h - (1.0 * cm) # Increased vertical padding

    def _draw_seller_card(c, x, y, width, seller_name, seller_email):
        """Draws the seller card, now including email."""
        c.saveState()
        
        card_height = 80 # Increased height to accommodate email
        card_y = y - card_height
        
        # Card background (White with a subtle Charcoal border)
        c.setFillColor(COLOR_WHITE)
        c.setStrokeColor(COLOR_GRAY_LIGHT)
        c.roundRect(x, card_y, width, card_height, 10, fill=1, stroke=1)
        
        avatar_x = x + 30
        avatar_y = card_y + (card_height / 2)
        
        # Avatar circle (Gold)
        c.setFillColor(COLOR_PRIMARY)
        c.circle(avatar_x, avatar_y, 22, fill=1, stroke=0)
        
        # Avatar initial
        initial = (seller_name[0] if seller_name else 'S').upper()
        c.setFont(FONT_BOLD, 18)
        c.setFillColor(COLOR_WHITE)
        c.drawCentredString(avatar_x, avatar_y - 7, initial)
        
        # --- Text Content ---
        text_x = avatar_x + 35
        
        # Seller Name
        c.setFont(FONT_BOLD, 14)
        c.setFillColor(COLOR_INK)
        c.drawString(text_x, card_y + 45, seller_name)
        
        # Email Label
        c.setFont(FONT_NORMAL, 9)
        c.setFillColor(COLOR_GRAY_DARK)
        c.drawString(text_x, card_y + 25, "Email:")
        
        # Seller Email (Italic, Charcoal)
        c.setFont(FONT_ITALIC, 11)
        c.setFillColor(COLOR_INK)
        c.drawString(text_x + 35, card_y + 25, seller_email or 'Not Provided')
        
        c.restoreState()
        return card_y - (1.0 * cm)

    def _draw_gallery(c, x, y, width, images, page_num_ref):
        """Draws the gallery grid with rounded image frames and a clean overlay."""
        c.saveState()
        
        num_cols = 3
        gap = 0.8 * cm # Increased gap
        cell_w = (width - (num_cols - 1) * gap) / num_cols
        cell_h = cell_w * 0.70 # Slightly wider aspect ratio
        
        current_x = x
        current_y = y
        
        for idx, img_obj in enumerate(images[:9]):
            # --- Page Break Check ---
            if current_y - cell_h < (MARGIN + FOOTER_HEIGHT):
                _draw_page_footer(c)
                c.showPage()
                page_num_ref[0] += 1
                current_y = _draw_page_header(c, "PropKart", page_num_ref[0])
                current_y -= MARGIN
                current_x = x
                
                # Redraw title for new page
                current_y = _draw_section_title(c, x, current_y, "Gallery (Continued)")
        
            if img_obj:
                try:
                    # Draw outer frame
                    c.setFillColor(COLOR_WHITE)
                    c.setStrokeColor(COLOR_GRAY_LIGHT)
                    c.roundRect(current_x, current_y - cell_h, cell_w, cell_h, 8, fill=1, stroke=1)
                    
                    # Clip and draw image
                    c.saveState()
                    p = c.beginPath()
                    p.roundRect(current_x, current_y - cell_h, cell_w, cell_h, 8)
                    c.clipPath(p, stroke=0, fill=0)
                    
                    iw, ih = img_obj.getSize()
                    draw_w, draw_h = _scale_to_fill(iw, ih, cell_w, cell_h)
                    offset_x = current_x + (cell_w - draw_w) / 2
                    offset_y = (current_y - cell_h) + (cell_h - draw_h) / 2
                    
                    c.drawImage(img_obj, offset_x, offset_y, width=draw_w, height=draw_h)
                    c.restoreState()
                    
                    # Overlay (Subtle Gradient effect)
                    c.setFillColor(COLOR_INK, 0.4) # Dark, slightly transparent
                    c.rect(current_x, current_y - cell_h, cell_w, 25, fill=1, stroke=0)
                    
                    # Overlay Text (Gold)
                    c.setFont(FONT_BOLD, 10)
                    c.setFillColor(COLOR_PRIMARY)
                    c.drawRightString(current_x + cell_w - 10, current_y - cell_h + 8, f"PHOTO {idx + 1}")
                    
                except Exception:
                    pass
            
            # Increment position
            current_x += (cell_w + gap)
            if (idx + 1) % num_cols == 0:
                current_x = x
                current_y -= (cell_h + gap)
        
        c.restoreState()
        return current_y


    # ===================================================================
    # MAIN DJANGO VIEW (Revised)
    # ===================================================================

    # NOTE: You must ensure 'Property', 'PropertyImage', and the related 'User'/'Seller'
    # models are imported and accessible in your actual Django environment.
    def property_brochure_pdf(request, property_id):
        
        # --- 1. Get Data ---
        prop = get_object_or_404(Property.objects.select_related('seller').filter(is_verified=True, is_hidden=False), id=property_id)
        
        # Get images
        image_paths = []
        for img in PropertyImage.objects.filter(property=prop).order_by('id'): # Order by ID for consistency
            try:
                if img.image and hasattr(img.image, 'path') and os.path.exists(img.image.path):
                    image_paths.append(img.image.path)
            except Exception:
                continue
                
        image_objects = [_safe_image(p) for p in image_paths]
        image_objects = [img for img in image_objects if img] # Filter out None
        hero_image = image_objects[0] if image_objects else None
        
        # Get seller info
        seller_name = "PropKart Agent"
        seller_email = "Contact Sales"
        if prop.seller:
            seller_name = f"{getattr(prop.seller, 'first_name', '')} {getattr(prop.seller, 'last_name', '')}".strip()
            seller_email = getattr(prop.seller, 'email', '')
            if not seller_name:
                seller_name = getattr(prop.seller, 'username', 'PropKart Agent')

        # --- 2. Setup PDF ---
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="propkart_{property_id}_brochure.pdf"'
        
        c = canvas.Canvas(response, pagesize=A4)
        c.setPageCompression(1)
        c.setTitle(f"{prop.title} - PropKart Brochure")
        
        page_number = [1] # Use a mutable list to track page number across functions

        # --- 3. Draw Content ---
        
        # Page 1 Header
        y = _draw_page_header(c, "PropKart", page_number[0])
        
        # --- Hero Section ---
        y = _draw_hero(c, MARGIN, y, CONTENT_WIDTH, prop, hero_image)

        # --- Specs Section ---
        # Check if we need to break page before drawing specs (Approx 180 points for specs)
        if y < MARGIN + FOOTER_HEIGHT + 180:
            _draw_page_footer(c)
            c.showPage()
            page_number[0] += 1
            y = _draw_page_header(c, "PropKart", page_number[0])
            y -= MARGIN
            
        y = _draw_section_title(c, MARGIN, y, "Key Specifications")
        
        specs = [
            ("🏠", "PROPERTY TYPE", str(prop.type).title()),
            ("🛏️", "BEDROOMS", prop.bedrooms or '—'),
            ("🚿", "BATHROOMS", prop.bathrooms or '—'),
            ("🚪", "TOTAL ROOMS", prop.rooms or '—'),
            ("📏", "DIMENSIONS", f"{prop.length or '—'} × {prop.width or '—'} ft"),
            ("🪑", "FURNISHED", "Yes" if prop.furnished else "No"),
            ("👁️", "VIEWS", prop.views or '—'),
            ("📅", "LISTED ON", prop.created_at.strftime('%b %d, %Y') if getattr(prop, 'created_at', None) else '—'),
        ]
        y = _draw_specs(c, MARGIN, y, CONTENT_WIDTH, specs)

        # --- Description Section ---
        # Check if we need to break page before drawing description (Approx 150 points for desc)
        if y < MARGIN + FOOTER_HEIGHT + 150:
            _draw_page_footer(c)
            c.showPage()
            page_number[0] += 1
            y = _draw_page_header(c, "PropKart", page_number[0])
            y -= MARGIN
            
        y = _draw_section_title(c, MARGIN, y, "Property Overview")
        desc = prop.description or 'No description provided.'
        y = _draw_paragraph(c, MARGIN, y, desc, CONTENT_WIDTH)

        # --- Seller Section ---
        # Check if we need to break page before drawing seller card (Approx 100 points)
        if y < MARGIN + FOOTER_HEIGHT + 100:
            _draw_page_footer(c)
            c.showPage()
            page_number[0] += 1
            y = _draw_page_header(c, "PropKart", page_number[0])
            y -= MARGIN
            
        y = _draw_section_title(c, MARGIN, y, "Contact Information")
        y = _draw_seller_card(c, MARGIN, y, CONTENT_WIDTH, seller_name, seller_email)

        # --- Gallery Section ---
        if image_objects:
            # Check if we need to break page before drawing gallery title
            if y < MARGIN + FOOTER_HEIGHT + 50:
                _draw_page_footer(c)
                c.showPage()
                page_number[0] += 1
                y = _draw_page_header(c, "PropKart", page_number[0])
                y -= MARGIN
                
            y = _draw_section_title(c, MARGIN, y, "Exclusive Gallery")
            # Gallery function handles its own internal page breaks
            _draw_gallery(c, MARGIN, y, CONTENT_WIDTH, image_objects, page_number)

        # --- 4. Finalize PDF ---
        _draw_page_footer(c)
        c.save()
        
        return response
    
@modal_login_required
def property_message(request, property_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

    prop = get_object_or_404(Property.objects.select_related('seller').filter(is_verified=True, is_hidden=False), id=property_id)

    if prop.seller_id == request.user.id:
        return JsonResponse({'success': False, 'error': 'Cannot message your own property'}, status=400)

    content = (request.POST.get('message') or '').strip()
    if not content:
        return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)

    # Basic rate limiting key (optional enhancement could use cache)
    # For now, just create the message
    msg = Message.objects.create(
        sender=request.user,
        receiver=prop.seller,
        property=prop,
        content=content,
    )

    return JsonResponse({
        'success': True,
        'message': msg.content,
        'timestamp': msg.sent_at.strftime('%b %d, %I:%M %p')
    })

@csrf_exempt
@require_http_methods(["POST"])
def chat_ask(request):
    """API endpoint for asking questions to the AI assistant"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Process the message
        chat_service = ChatService()
        result = chat_service.process_message(request.user, message)
        
        return JsonResponse({
            'success': True,
            'response': result['response'],
            'referenced_properties': result['referenced_properties'],
            'properties_found': result['properties_found'],
            'session_id': result['session_id']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def chat_history(request):
    """Get chat history for the current user"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session_id = request.GET.get('session_id')
        if session_id:
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        else:
            session = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-created_at').first()
        
        if not session:
            return JsonResponse({'messages': []})
        
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'type': msg.message_type,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'referenced_properties': msg.referenced_properties
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_list,
            'session_id': str(session.session_id)
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def chat_new_session(request):
    """Start a new chat session"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Deactivate current sessions
        ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Create new session
        chat_service = ChatService()
        session = chat_service.create_or_get_session(request.user)
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.session_id)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def chat_clear(request):
    """Clear current chat: deactivate session and delete its messages"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        # Find current active session
        session = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-created_at').first()
        if session:
            ChatMessage.objects.filter(session=session).delete()
            session.is_active = False
            session.save(update_fields=['is_active'])
        # Create a fresh session
        chat_service = ChatService()
        new_session = chat_service.create_or_get_session(request.user)
        return JsonResponse({'success': True, 'session_id': str(new_session.session_id)})
    except Exception as e:
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

@modal_login_required
@require_POST
def message_reply(request):
    content = (request.POST.get('message') or '').strip()
    property_id = request.POST.get('property_id')
    recipient_id = request.POST.get('recipient_id')

    if not content:
        return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
    try:
        property_id = int(property_id)
        recipient_id = int(recipient_id)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid parameters'}, status=400)

    prop = get_object_or_404(Property.objects.select_related('seller'), id=property_id)
    recipient = get_object_or_404(User, id=recipient_id)

    # Disallow self-messaging
    if request.user.id == recipient_id:
        return JsonResponse({'success': False, 'error': 'Cannot send message to yourself'}, status=400)

    # Only allow messages between the property seller and the other participant (buyer)
    if not (request.user.id == prop.seller_id or recipient_id == prop.seller_id):
        return JsonResponse({'success': False, 'error': 'Not allowed'}, status=403)

    msg = Message.objects.create(
        sender=request.user,
        receiver=recipient,
        property=prop,
        content=content,
    )
    # Create in-app notification for receiver
    try:
        Notification.objects.create(
            user=recipient,
            type='chat',
            title='New message received',
            message=f'{request.user.first_name} messaged you about {prop.title}',
            url=f"/seller/messages?property={prop.id}&buyer={request.user.id}" if recipient.id == prop.seller_id else f"/buyer/messages?property={prop.id}",
            meta={'property_id': prop.id, 'sender_id': request.user.id}
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'id': msg.id,
        'message': msg.content,
        'timestamp': msg.sent_at.strftime('%b %d, %I:%M %p')
    })


@require_http_methods(["GET"]) 
@modal_login_required
def notifications_list(request):
    status = request.GET.get('status', 'unread')
    qs = Notification.objects.filter(user=request.user)
    if status == 'unread':
        qs = qs.filter(is_read=False)
    qs = qs.order_by('-created_at')
    items = []
    for n in qs:
        items.append({
            'id': n.id,
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'url': n.url,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        })
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'items': items, 'unread': unread_count})


@require_http_methods(["POST"]) 
@modal_login_required
def notifications_mark_read(request):
    ids_raw = (request.POST.get('ids') or '').strip()
    ids = [int(x) for x in ids_raw.split(',') if x.strip().isdigit()]
    Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
    return JsonResponse({'success': True})


@require_http_methods(["POST"]) 
@modal_login_required
def notifications_mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@require_http_methods(["POST"])
@modal_login_required
def chat_delete_messages(request):
    """Delete selected messages in a conversation (by ids). Params: property_id, peer_id, ids (comma-separated)
       Only deletes messages SENT by the current user.
    """
    try:
        property_id = int(request.POST.get('property_id'))
        peer_id = int(request.POST.get('peer_id'))
        ids_raw = (request.POST.get('ids') or '').strip()
        ids = [int(x) for x in ids_raw.split(',') if x.strip().isdigit()]
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid parameters'}, status=400)

    prop = get_object_or_404(Property.objects.select_related('seller'), id=property_id)
    if not (request.user.id == prop.seller_id or peer_id == prop.seller_id):
        return JsonResponse({'success': False, 'error': 'Not allowed'}, status=403)

    from django.db.models import Q
    qs = (
        Message.objects.filter(id__in=ids, property_id=property_id, sender=request.user)
        .filter(Q(receiver_id=peer_id) | Q(sender_id=peer_id))
    )
    deleted = qs.count()
    qs.delete()
    return JsonResponse({'success': True, 'deleted': deleted})


@require_http_methods(["POST"])
@modal_login_required
def chat_clear_conversation(request):
    """Clear (delete) all messages SENT by the current user in a conversation between current user and peer for a property.
       Params: property_id, peer_id
    """
    try:
        property_id = int(request.POST.get('property_id'))
        peer_id = int(request.POST.get('peer_id'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid parameters'}, status=400)

    prop = get_object_or_404(Property.objects.select_related('seller'), id=property_id)
    if not (request.user.id == prop.seller_id or peer_id == prop.seller_id):
        return JsonResponse({'success': False, 'error': 'Not allowed'}, status=403)

    from django.db.models import Q
    qs = Message.objects.filter(property_id=property_id, sender=request.user).filter(
        Q(receiver_id=peer_id) | Q(sender_id=peer_id)
    )
    deleted = qs.count()
    qs.delete()
    return JsonResponse({'success': True, 'deleted': deleted})

def buyer_messages(request):
    if not request.user.is_authenticated:
        return redirect('login')

    property_id = request.GET.get('property')

    # Filter messages where user is involved, but exclude self-conversations
    base_qs = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).exclude(
        # Exclude messages where user is both sender and receiver (self-messages)
        sender=request.user, receiver=request.user
    )

    thread_keys = (
        base_qs.values('property_id')
              .annotate(last_time=Max('sent_at'))
              .order_by('-last_time')
    )

    threads = []
    for key in thread_keys:
        last_msg = (base_qs.filter(property_id=key['property_id'])
                            .order_by('-sent_at')
                            .select_related('property', 'sender', 'receiver', 'property__seller')
                            .first())
        if not last_msg:
            continue
        
        seller = last_msg.property.seller
        
        # Skip if user is the seller (they should only see this in seller messages, not buyer messages)
        if seller.id == request.user.id:
            continue
            
        unread_count = Message.objects.filter(property_id=key['property_id'], receiver=request.user, is_read=False).count()
        threads.append({
            'last': last_msg,
            'seller': seller,
            'unread_count': unread_count,
        })

    conversation = []
    selected_seller_id = None
    if property_id:
        prop = get_object_or_404(Property.objects.select_related('seller'), id=property_id)
        selected_seller_id = prop.seller_id
        conversation_qs = Message.objects.filter(property_id=property_id).filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('sent_at').select_related('sender', 'receiver', 'property')
        conversation = list(conversation_qs)
        conversation_qs.filter(receiver=request.user, is_read=False).update(is_read=True)

    context = {
        'threads': threads,
        'conversation': conversation,
        'selected_property_id': int(property_id) if property_id else None,
        'selected_seller_id': selected_seller_id,
    }
    return render(request, 'app/messages.html', context)

@require_http_methods(["GET"])
@modal_login_required
def chat_conversation(request):
    """Return messages for a conversation filtered by property and peer (other user).
    Query params:
      - property: property_id (int)
      - peer: user_id of the other participant (int)
      - after: ISO timestamp; if provided, return only messages created after this time
    """
    try:
        property_id = int(request.GET.get('property'))
        peer_id = int(request.GET.get('peer'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)

    prop = get_object_or_404(Property.objects.select_related('seller'), id=property_id)

    # Authorization: current user must be seller or peer must be seller
    if not (request.user.id == prop.seller_id or peer_id == prop.seller_id):
        return JsonResponse({'error': 'Not allowed'}, status=403)

    from django.db.models import Q
    qs = (Message.objects.filter(property_id=property_id)
          .filter(Q(sender_id=peer_id, receiver=request.user) | Q(sender=request.user, receiver_id=peer_id))
          .order_by('sent_at')
          .select_related('sender'))

    after = request.GET.get('after')
    if after:
        try:
            dt = parse_datetime(after)
            if dt is not None:
                qs = qs.filter(sent_at__gt=dt)
        except Exception:
            pass

    messages_payload = []
    for m in qs:
        messages_payload.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'content': m.content,
            'sent_at': m.sent_at.isoformat(),
        })

    # Mark as read for messages received by current user
    Message.objects.filter(id__in=[m['id'] for m in messages_payload if m['sender_id'] != request.user.id], is_read=False).update(is_read=True)

    return JsonResponse({'messages': messages_payload})

# Enquiry Views
def submit_enquiry(request, property_id):
    """Handle enquiry form submission"""
    property_obj = get_object_or_404(Property.objects.filter(is_verified=True, is_hidden=False), id=property_id)
    
    if request.method == 'POST':
        buyer_name = request.POST.get('buyer_name', '').strip()
        buyer_email = request.POST.get('buyer_email', '').strip()
        buyer_phone = request.POST.get('buyer_phone', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        errors = []
        if not buyer_name:
            errors.append("Name is required.")
        if not buyer_email:
            errors.append("Email is required.")
        if not buyer_phone:
            errors.append("Phone number is required.")
        if not message:
            errors.append("Message is required.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('property_detail', property_id=property_id)
        
        # Create enquiry
        enquiry = Enquiry.objects.create(
            property=property_obj,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            message=message
        )
        
        # Create a message in the messaging system
        try:
            if request.user.is_authenticated:
                # If user is logged in, create message from their account
                message_content = f"ENQUIRY: {message}\n\n---\nContact: {buyer_name} | {buyer_email} | {buyer_phone}"
                Message.objects.create(
                    sender=request.user,
                    receiver=property_obj.seller,
                    property=property_obj,
                    content=message_content
                )
            else:
                # For anonymous users, try to find existing user by email or create a guest message
                # Check if a user with this email exists
                try:
                    existing_user = User.objects.get(email=buyer_email)
                    message_content = f"ENQUIRY: {message}\n\n---\nContact: {buyer_name} | {buyer_email} | {buyer_phone}"
                    Message.objects.create(
                        sender=existing_user,
                        receiver=property_obj.seller,
                        property=property_obj,
                        content=message_content
                    )
                except User.DoesNotExist:
                    # Create a special enquiry message that doesn't require a sender user
                    # We'll store this as enquiry data and display it in messages
                    pass
        except Exception:
            pass
        
        # Create notification for seller
        try:
            Notification.objects.create(
                user=property_obj.seller,
                type='enquiry',
                title='New Property Enquiry',
                message=f'{buyer_name} sent an enquiry for {property_obj.title}',
                url=f'/seller/enquiries',
                meta={'enquiry_id': enquiry.id, 'property_id': property_obj.id}
            )
        except Exception:
            pass
        
        messages.success(request, "Your enquiry has been sent successfully! The seller will contact you soon.")
        return redirect('property_detail', property_id=property_id)
    
    return redirect('property_detail', property_id=property_id)

@modal_login_required
def delete_enquiry(request, enquiry_id):
    """Delete an enquiry (seller only)"""
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    
    # Check if current user is the seller of the property
    if enquiry.property.seller != request.user:
        messages.error(request, "You don't have permission to delete this enquiry.")
        return redirect('seller_enquiries')
    
    if request.method == 'POST' or request.method == 'GET':
        enquiry.delete()
        messages.success(request, "Enquiry deleted successfully.")
    
    return redirect('seller_enquiries')

@modal_login_required
def mark_enquiry_replied(request, enquiry_id):
    """Mark enquiry as replied"""
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    
    # Check if current user is the seller of the property
    if enquiry.property.seller != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    enquiry.status = 'replied'
    enquiry.save()
    
    return JsonResponse({'success': True})

# Property Visibility Toggle
@modal_login_required
def toggle_property_visibility(request, property_id):
    """Toggle property visibility (hide/show) for sellers"""
    if not request.user.is_seller:
        return JsonResponse({'success': False, 'error': 'Only sellers can manage property visibility'}, status=403)
    
    try:
        property_obj = Property.objects.get(id=property_id, seller=request.user)
        
        # Toggle the is_hidden field
        property_obj.is_hidden = not property_obj.is_hidden
        property_obj.save()
        
        status = "hidden" if property_obj.is_hidden else "visible"
        return JsonResponse({
            'success': True, 
            'is_hidden': property_obj.is_hidden,
            'message': f'Property is now {status} to buyers'
        })
        
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Property not found or you do not own this property'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Password Reset Views
def forget_password(request):
    """Handle forget password request"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'app/forget_password.html')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return render(request, 'app/forget_password.html')
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Create password reset token
        expires_at = timezone.now() + timedelta(minutes=15)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=otp_code,
            expires_at=expires_at
        )
        
        # Send OTP email
        try:
            html_content = render_to_string('emails/password_reset_otp.html', {
                'user': user,
                'otp_code': otp_code,
                'reset_token': reset_token
            })
            
            subject = 'Password Reset - PropKart'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]
            
            msg = EmailMultiAlternatives(subject, '', from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            messages.success(request, f'Password reset OTP has been sent to {email}. Please check your email.')
            return redirect('verify_password_reset_otp', token_id=reset_token.id)
            
        except Exception as e:
            print(f"Email sending error: {str(e)}")  # Debug logging
            reset_token.delete()  # Clean up if email fails
            messages.error(request, f'Failed to send email: {str(e)}')
            return render(request, 'app/forget_password.html')
    
    return render(request, 'app/forget_password.html')

def verify_password_reset_otp(request, token_id):
    """Verify OTP for password reset"""
    try:
        reset_token = PasswordResetToken.objects.get(id=token_id)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('forget_password')
    
    if not reset_token.is_valid():
        messages.error(request, 'This reset link has expired or been used.')
        return redirect('forget_password')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        
        if not entered_otp:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'app/verify_password_reset_otp.html', {'token_id': token_id})
        
        if entered_otp == reset_token.token:
            # OTP is correct, mark as used
            reset_token.is_used = True
            reset_token.save()
            
            # Store user ID in session for password reset
            request.session['password_reset_user_id'] = reset_token.user.id
            
            messages.success(request, 'OTP verified successfully! Please set your new password.')
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'app/verify_password_reset_otp.html', {'token_id': token_id})

def reset_password(request):
    """Handle password reset form"""
    user_id = request.session.get('password_reset_user_id')
    
    if not user_id:
        messages.error(request, 'Invalid reset session. Please request a new password reset.')
        return redirect('forget_password')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('forget_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'app/reset_password.html')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'app/reset_password.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'app/reset_password.html')
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Clear session
        del request.session['password_reset_user_id']
        
        messages.success(request, 'Password reset successfully! You can now login with your new password.')
        return redirect('login')
    
    return render(request, 'app/reset_password.html')

# Visit Request Views
def request_visit(request, property_id):
    """Handle visit request submission"""
    property_obj = get_object_or_404(Property.objects.filter(is_verified=True, is_hidden=False), id=property_id)
    
    if request.method == 'POST':
        # Get form data
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        alternative_date = request.POST.get('alternative_date') or None
        alternative_time = request.POST.get('alternative_time') or None
        visitor_name = request.POST.get('visitor_name', '').strip()
        visitor_phone = request.POST.get('visitor_phone', '').strip()
        visitor_email = request.POST.get('visitor_email', '').strip()
        message = request.POST.get('message', '').strip()
        visitor_count = int(request.POST.get('visitor_count', 1))
        
        # Validation
        errors = []
        if not all([preferred_date, preferred_time, visitor_name, visitor_phone, visitor_email]):
            errors.append("All required fields must be filled.")
        
        # Check if date is not in the past
        from datetime import datetime, date
        try:
            pref_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
            if pref_date < date.today():
                errors.append("Preferred date cannot be in the past.")
        except ValueError:
            errors.append("Invalid date format.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('property_detail', property_id=property_id)
        
        # Create visit request
        visit_request = VisitRequest.objects.create(
            property=property_obj,
            buyer=request.user if request.user.is_authenticated else None,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            alternative_date=alternative_date,
            alternative_time=alternative_time,
            visitor_name=visitor_name,
            visitor_phone=visitor_phone,
            visitor_email=visitor_email,
            message=message,
            visitor_count=visitor_count
        )
        
        # Create notification for seller
        try:
            Notification.objects.create(
                user=property_obj.seller,
                type='visit_request',
                title='New Visit Request',
                message=f'{visitor_name} requested a visit for {property_obj.title}',
                url=f'/seller/visit-requests',
                meta={'visit_request_id': visit_request.id, 'property_id': property_obj.id}
            )
        except Exception:
            pass
        
        messages.success(request, "Visit request sent successfully! The seller will contact you soon.")
        return redirect('property_detail', property_id=property_id)
    
    return redirect('property_detail', property_id=property_id)

@modal_login_required
def seller_visit_requests(request):
    """Seller dashboard for managing visit requests"""
    visit_requests = VisitRequest.objects.filter(
        property__seller=request.user
    ).select_related('property', 'buyer').order_by('-created_at')
    
    # Statistics
    total_requests = visit_requests.count()
    pending_requests = visit_requests.filter(status='pending').count()
    approved_requests = visit_requests.filter(status='approved').count()
    
    context = {
        'visit_requests': visit_requests,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
    }
    return render(request, 'app/seller/visit_requests.html', context)

@modal_login_required
def update_visit_request(request, request_id):
    """Update visit request status"""
    visit_request = get_object_or_404(VisitRequest, id=request_id)
    
    # Check permission
    if visit_request.property.seller != request.user:
        messages.error(request, "Permission denied.")
        return redirect('seller_visit_requests')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        seller_response = request.POST.get('seller_response', '')
        confirmed_date = request.POST.get('confirmed_date') or None
        confirmed_time = request.POST.get('confirmed_time') or None
        
        visit_request.status = status
        visit_request.seller_response = seller_response
        visit_request.confirmed_date = confirmed_date
        visit_request.confirmed_time = confirmed_time
        visit_request.save()
        
        # Create notification for buyer
        try:
            if visit_request.buyer:
                Notification.objects.create(
                    user=visit_request.buyer,
                    type='visit_response',
                    title=f'Visit Request {status.title()}',
                    message=f'Your visit request for {visit_request.property.title} has been {status}',
                    url=f'/buyer/visit-requests',
                    meta={'visit_request_id': visit_request.id}
                )
        except Exception:
            pass
        
        messages.success(request, f"Visit request {status} successfully.")
    
    return redirect('seller_visit_requests')

@modal_login_required
def buyer_visit_requests(request):
    """Buyer dashboard for viewing their visit requests"""
    visit_requests = VisitRequest.objects.filter(
        buyer=request.user
    ).select_related('property', 'property__seller').order_by('-created_at')
    
    # Statistics
    total_requests = visit_requests.count()
    pending_requests = visit_requests.filter(status='pending').count()
    approved_requests = visit_requests.filter(status='approved').count()
    
    context = {
        'visit_requests': visit_requests,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
    }
    return render(request, 'app/visit_requests.html', context)

@modal_login_required
def cancel_visit_request(request, request_id):
    """Cancel a visit request (buyer only)"""
    visit_request = get_object_or_404(VisitRequest, id=request_id)
    
    # Check permission
    if visit_request.buyer != request.user:
        messages.error(request, "Permission denied.")
        return redirect('buyer_visit_requests')
    
    if visit_request.status == 'pending':
        visit_request.status = 'cancelled'
        visit_request.save()
        messages.success(request, "Visit request cancelled successfully.")
    else:
        messages.error(request, "Cannot cancel this visit request.")
    
    return redirect('buyer_visit_requests')