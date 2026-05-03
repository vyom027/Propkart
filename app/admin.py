from django.contrib import admin
from django.urls import reverse, path
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from .models import User, Property, Message, PropertyImage, VisitRequest, Wishlist,SellerRequest, Notification, Enquiry, Contact
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from .models import (
    User, Property, PropertyImage, Message, Wishlist, 
    Notification, Enquiry, VisitRequest, Contact, SellerRequest,
    PropertyImportKey, PasswordResetToken, ChatSession, ChatMessage
)

# ===== USER ADMIN (Enhanced) =====
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_buyer', 'is_seller', 'is_staff')
    list_filter = ('is_buyer', 'is_seller', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'mobile')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('mobile', 'city', 'state', 'country', 'address', 'profile_picture', 'is_buyer', 'is_seller')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'mobile', 'city', 'state', 'country', 'is_buyer', 'is_seller')
        }),
    )

admin.site.register(User, CustomUserAdmin)

# ===== PROPERTY IMAGE INLINE =====
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    can_delete = True
    verbose_name = "Property Image"
    verbose_name_plural = "Property Images"

# ===== PROPERTY ADMIN (With Inline Images) =====
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "type", "price", "city", "is_verified", "views", "created_at", "moderation_actions")
    list_filter = ("is_verified", "type", "furnished", "is_hidden", "city", "state", "created_at")
    search_fields = ("title", "location", "seller__username", "seller__email", "city")
    readonly_fields = ("created_at", "views", "viewers")
    ordering = ("-id",)
    
    # Add inline images
    inlines = [PropertyImageInline]

    actions = ["approve_properties", "reject_properties", "hide_properties", "show_properties"]

    # Fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'title', 'description', 'type')
        }),
        ('Pricing & Location', {
            'fields': ('price', 'location', 'city', 'state', 'country')
        }),
        ('Property Details', {
            'fields': ('length', 'width', 'rooms', 'bedrooms', 'bathrooms', 'furnished')
        }),
        ('Status & Visibility', {
            'fields': ('is_verified', 'is_hidden', 'views', 'viewers')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def approve_properties(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"Approved {updated} properties.")
    approve_properties.short_description = "Approve selected properties"

    def reject_properties(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"Rejected {updated} properties.")
    reject_properties.short_description = "Reject selected properties"
    
    def hide_properties(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"Hidden {updated} properties.")
    hide_properties.short_description = "Hide selected properties"
    
    def show_properties(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request, f"Shown {updated} properties.")
    show_properties.short_description = "Show selected properties"

    # Inline buttons per row
    def moderation_actions(self, obj):
        approve_url = reverse("admin:app_property_approve", args=[obj.id])
        reject_url = reverse("admin:app_property_reject", args=[obj.id])
        
        if obj.is_verified:
            return format_html(
                '<span style="color:green;">✓ Approved</span> | '
                '<a class="button" href="{}">Reject</a>',
                reject_url,
            )
        else:
            return format_html(
                '<a class="button" href="{}" style="margin-right:6px;">Approve</a>'
                '<span style="color:red;">✗ Not Verified</span>',
                approve_url,
            )
    moderation_actions.short_description = "Actions"
    moderation_actions.allow_tags = True

    # Custom admin URLs for inline actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:property_id>/approve/',
                self.admin_site.admin_view(self.approve_single_view),
                name='app_property_approve',
            ),
            path(
                '<int:property_id>/reject/',
                self.admin_site.admin_view(self.reject_single_view),
                name='app_property_reject',
            ),
        ]
        return custom_urls + urls

    def approve_single_view(self, request, property_id):
        obj = get_object_or_404(Property, id=property_id)
        obj.is_verified = True
        obj.save(update_fields=["is_verified"])
        self.message_user(request, f"Approved '{obj.title}'.")
        return redirect(request.META.get("HTTP_REFERER", reverse("admin:app_property_changelist")))

    def reject_single_view(self, request, property_id):
        obj = get_object_or_404(Property, id=property_id)
        obj.is_verified = False
        obj.save(update_fields=["is_verified"])
        self.message_user(request, f"Rejected '{obj.title}'.")
        return redirect(request.META.get("HTTP_REFERER", reverse("admin:app_property_changelist")))
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('seller')

# ===== PROPERTY IMAGE ADMIN (Standalone) =====
@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'image_preview', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('property__title',)
    readonly_fields = ('uploaded_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'property__seller')

# ===== MESSAGE ADMIN =====

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'property', 'is_read', 'sent_at')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__email', 'receiver__email', 'property__title', 'content')
    readonly_fields = ('sent_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver', 'property')

# ===== WISHLIST ADMIN =====
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'property__title')
    readonly_fields = ('added_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'property')

# ===== NOTIFICATION ADMIN =====

class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "title", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("title", "message", "user__email")
    readonly_fields = ("created_at",)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Marked {updated} notifications as read.")
    mark_as_read.short_description = "Mark as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"Marked {updated} notifications as unread.")
    mark_as_unread.short_description = "Mark as unread"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# ===== ENQUIRY ADMIN =====
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("buyer_name", "buyer_email", "property", "status", "created_at")
    list_filter = ("status", "created_at", "property__type")
    search_fields = ("buyer_name", "buyer_email", "property__title", "message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    actions = ['mark_as_replied', 'mark_as_closed']
    
    fieldsets = (
        ('Buyer Information', {
            'fields': ('buyer_name', 'buyer_email', 'buyer_phone')
        }),
        ('Enquiry Details', {
            'fields': ('property', 'message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(status='replied')
        self.message_user(request, f"Marked {updated} enquiries as replied.")
    mark_as_replied.short_description = "Mark as replied"
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f"Marked {updated} enquiries as closed.")
    mark_as_closed.short_description = "Mark as closed"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'property__seller')

# ===== VISIT REQUEST ADMIN =====
@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ("visitor_name", "property", "preferred_date", "preferred_time", "status", "created_at")
    list_filter = ("status", "created_at", "preferred_date", "property__type")
    search_fields = ("visitor_name", "visitor_email", "visitor_phone", "property__title", "buyer__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    actions = ['approve_requests', 'reject_requests', 'mark_completed']
    
    fieldsets = (
        ('Visitor Information', {
            'fields': ('visitor_name', 'visitor_email', 'visitor_phone', 'visitor_count')
        }),
        ('Property & Buyer', {
            'fields': ('property', 'buyer')
        }),
        ('Visit Details', {
            'fields': ('preferred_date', 'preferred_time', 'alternative_date', 'alternative_time', 'message')
        }),
        ('Status & Response', {
            'fields': ('status', 'seller_response', 'confirmed_date', 'confirmed_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def approve_requests(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"Approved {updated} visit requests.")
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"Rejected {updated} visit requests.")
    reject_requests.short_description = "Reject selected requests"
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"Marked {updated} visits as completed.")
    mark_completed.short_description = "Mark as completed"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'buyer', 'property__seller')

# ===== CONTACT ADMIN =====
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    actions = ["mark_as_in_progress", "mark_as_resolved", "mark_as_closed"]
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status="in_progress")
        self.message_user(request, f"Marked {updated} contacts as in progress.")
    mark_as_in_progress.short_description = "Mark selected contacts as in progress"
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status="resolved")
        self.message_user(request, f"Marked {updated} contacts as resolved.")
    mark_as_resolved.short_description = "Mark selected contacts as resolved"
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status="closed")
        self.message_user(request, f"Marked {updated} contacts as closed.")
    mark_as_closed.short_description = "Mark selected contacts as closed"
    
    fieldsets = (
        ("Contact Information", {
            "fields": ("name", "email", "subject")
        }),
        ("Message", {
            "fields": ("message",)
        }),
        ("Status & Admin Notes", {
            "fields": ("status", "admin_notes")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )


# ===== ADMIN SITE CUSTOMIZATION =====
admin.site.site_header = "Propkart Admin"
admin.site.site_title = "Propkart Admin Portal"
admin.site.index_title = "Welcome to Propkart Administration"