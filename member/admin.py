from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Item, BorrowRequest, BorrowHistory, Review, ItemReport

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Options', {'fields': ('phone', 'locality', 'pincode', 'google_map_link', 'role', 'profile_image', 'points', 'average_rating', 'is_blocked')}),
    )
    list_display = ('username', 'email', 'role', 'points', 'average_rating', 'is_blocked')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'owner', 'status', 'is_active', 'report_count', 'created_at')
    list_filter = ('status', 'is_active', 'category')
    search_fields = ('title', 'description')

class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'requester', 'status', 'preferred_date', 'requested_at')
    list_filter = ('status',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
admin.site.register(BorrowRequest, BorrowRequestAdmin)
admin.site.register(BorrowHistory)
admin.site.register(Review)
admin.site.register(ItemReport)
