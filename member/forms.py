from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Category, Item, BorrowRequest, Review, ItemReport

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'locality', 'pincode')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'locality', 'pincode', 'role')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone', 'locality', 'google_map_link', 'profile_image')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'locality': forms.TextInput(attrs={'class': 'form-input'}),
            'google_map_link': forms.URLInput(attrs={'class': 'form-input'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
        }

class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['reason', 'preferred_date']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

class ItemReportForm(forms.ModelForm):
    class Meta:
        model = ItemReport
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
