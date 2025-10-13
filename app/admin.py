from django.contrib import admin
from django.urls import reverse, path
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from .models import User, Property, Message, PropertyImage, VisitRequest, Wishlist,SellerRequest, Notification, Enquiry

admin.site.register(User)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "type", "price", "is_verified", "created_at", "moderation_actions")
    list_filter = ("is_verified", "type", "furnished", "created_at")
    search_fields = ("title", "location", "seller__username")
    ordering = ("-id",)

    actions = ["approve_properties", "reject_properties"]

    def approve_properties(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"Approved {updated} properties.")
    approve_properties.short_description = "Approve selected properties"

    def reject_properties(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"Rejected {updated} properties.")
    reject_properties.short_description = "Reject selected properties"

    # Inline buttons per row
    def moderation_actions(self, obj):
        approve_url = reverse("admin:app_property_approve", args=[obj.id])
        reject_url = reverse("admin:app_property_reject", args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="margin-right:6px;">Approve</a>'
            '<a class="button" href="{}">Reject</a>',
            approve_url,
            reject_url,
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

admin.site.register(Message)
admin.site.register(PropertyImage)
admin.site.register(Wishlist)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "title", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("title", "message", "user__email")

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("buyer_name", "buyer_email", "property", "status", "created_at")
    list_filter = ("status", "created_at", "property__type")
    search_fields = ("buyer_name", "buyer_email", "property__title", "message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'property__seller')

@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ("visitor_name", "property", "preferred_date", "preferred_time", "status", "created_at")
    list_filter = ("status", "created_at", "preferred_date", "property__type")
    search_fields = ("visitor_name", "visitor_email", "visitor_phone", "property__title")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    
    fieldsets = (
        ("Visitor Information", {
            "fields": ("visitor_name", "visitor_email", "visitor_phone", "visitor_count")
        }),
        ("Property & Buyer", {
            "fields": ("property", "buyer")
        }),
        ("Visit Details", {
            "fields": ("preferred_date", "preferred_time", "alternative_date", "alternative_time", "message")
        }),
        ("Status & Response", {
            "fields": ("status", "seller_response", "confirmed_date", "confirmed_time")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'buyer', 'property__seller')

admin.site.register(SellerRequest)
admin.site.site_header = "Propkart Admin"
admin.site.site_title = "Propkart Admin Portal"
