from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Role, Location, Manufacturer, Drug, Pharmacy, PharmacyInventory, RequestLog,
    InventorySearchLog
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin configuration for the User model."""
    # Define the fields to display in the list view
    list_display = ('contact_number', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'role')
    search_fields = ('contact_number', 'full_name')
    ordering = ('contact_number',)

    # Customize the fields displayed on the add/change form
    fieldsets = (
        (None, {'fields': ('contact_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'role')}),
        ('Permissions', {
            'fields': ('is_active', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fields for the 'add user' form
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name', 'role',)}),
    )
    # Since we removed username, we must tell the admin which field to use
    readonly_fields = ('date_joined', 'last_login', 'is_staff', 'is_superuser')


@admin.register(InventorySearchLog)
class InventorySearchLogAdmin(admin.ModelAdmin):
    """Admin view for InventorySearchLog."""
    list_display = ('user', 'ip_address', 'timestamp', 'query_params')
    list_filter = ('timestamp', 'user')
    search_fields = ('query_params', 'user__contact_number')
    readonly_fields = ('user', 'ip_address', 'timestamp', 'query_params')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Role)
admin.site.register(Location)
admin.site.register(Manufacturer)
admin.site.register(Drug)
admin.site.register(Pharmacy)
admin.site.register(PharmacyInventory)
admin.site.register(RequestLog)
