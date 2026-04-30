from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Member', 'Member'),
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    locality = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    google_map_link = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Member')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    points = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    is_blocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    # date_joined is provided by AbstractUser

    def __str__(self):
        return f"{self.username} ({self.role})"
        
    @property
    def badge(self):
        if self.average_rating >= 4.5:
            return "Top Contributor"
        elif self.average_rating >= 4.0:
            return "Trusted Member"
        return "Active Member"

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Approved', 'Approved'),
        ('Closed', 'Closed'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    is_active = models.BooleanField(default=True)
    report_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class BorrowRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='borrow_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    reason = models.TextField()
    preferred_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_message = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.item.title} by {self.requester.username}"

class BorrowHistory(models.Model):
    borrow_request = models.OneToOneField(BorrowRequest, on_delete=models.CASCADE, related_name='history')
    collected_on = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"History for {self.borrow_request}"

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.item.title}"

class ItemReport(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Dismissed', 'Dismissed'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.item.title} by {self.reported_by.username}"
