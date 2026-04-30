from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Count
from django.db.models.functions import Lower
from django.http import HttpResponseForbidden

from .models import User, Category, Item, BorrowRequest, BorrowHistory, Review, ItemReport
from .forms import (
    CustomUserCreationForm,
    ProfileUpdateForm,
    CategoryForm,
    ItemForm,
    BorrowRequestForm,
    ReviewForm,
    ItemReportForm
)
from datetime import datetime

# Decorators for role-based access
def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'Admin':
            return HttpResponseForbidden("Admin access required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def member_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'Member':
            return HttpResponseForbidden("Member access required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Public Views
def landing_page(request):
    featured_items = Item.objects.filter(status='Available', is_active=True).order_by('-created_at')[:6]
    top_members = User.objects.filter(role='Member').order_by('-average_rating', '-points')[:5]
    categories = Category.objects.all()
    return render(request, 'member/landing.html', {
        'featured_items': featured_items,
        'top_members': top_members,
        'categories': categories,
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = 'Member'
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'member/register.html', {'form': form})

# Simple login using django's built in view isn't easily customized to handle is_blocked, so we write our own.
from django.contrib.auth.forms import AuthenticationForm
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_blocked:
                messages.error(request, "Your account has been blocked.")
                return render(request, 'member/login.html', {'form': form})
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'member/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def dashboard_view(request):
    if request.user.role == 'Admin':
        return render(request, 'member/admin_dashboard.html', {
            'total_users': User.objects.filter(role='Member').count(),
            'total_items': Item.objects.count(),
            'total_requests': BorrowRequest.objects.count(),
        })
    else:
        return render(request, 'member/member_dashboard.html', {
            'total_items': Item.objects.filter(owner=request.user).count(),
            'available_items': Item.objects.filter(owner=request.user, status='Available').count(),
            'pending_requests': BorrowRequest.objects.filter(item__owner=request.user, status='Pending').count(),
        })

@login_required
@login_required
def explore_view(request):
    items = Item.objects.filter(status='Available', is_active=True).exclude(owner=request.user)

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    locality = request.GET.get('locality')
    sort_by = request.GET.get('sort')

    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if category_id:
        items = items.filter(category_id=category_id)

    if locality:
        items = items.filter(owner__locality=locality)

    if sort_by == 'rating':
        items = items.order_by('-owner__average_rating')
    elif sort_by == 'newest':
        items = items.order_by('-created_at')

    categories = Category.objects.all()

    # NEW: distinct localities from active members
    localities = User.objects.filter(
        role='Member',
        is_blocked=False
    ).exclude(locality__isnull=True).exclude(locality__exact='') \
     .values_list('locality', flat=True).distinct().order_by('locality')

    return render(request, 'member/explore.html', {
        'items': items,
        'categories': categories,
        'localities': localities
    })

@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    related_items = Item.objects.filter(category=item.category, status='Available', is_active=True).exclude(id=item.id)[:4]
    
    context = {'item': item, 'related_items': related_items}
    
    if item.owner == request.user:
        context['incoming_requests'] = item.borrow_requests.filter(status='Pending')
        
    return render(request, 'member/item_detail.html', context)

@login_required
@member_required
def request_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, status='Available', is_active=True)
    if item.owner == request.user:
        messages.error(request, "You cannot request your own item.")
        return redirect('item_detail', item_id=item.id)
        
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            borrow_request = form.save(commit=False)
            borrow_request.item = item
            borrow_request.requester = request.user
            borrow_request.save()
            messages.success(request, "Borrow request sent.")
            return redirect('explore')
    else:
        form = BorrowRequestForm()
    return render(request, 'member/request_form.html', {'form': form, 'item': item})

@login_required
def report_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.item = item
            report.reported_by = request.user
            report.save()
            
            item.report_count += 1
            item.save()
            messages.success(request, "Item reported successfully.")
            return redirect('item_detail', item_id=item.id)
    else:
        form = ItemReportForm()
    return render(request, 'member/report_form.html', {'form': form, 'item': item})

def leaderboard_view(request):
    top_members = User.objects.filter(
        role='Member',
        is_blocked=False,
        average_rating__gt=0,
        points__gt=0
    ).order_by('-average_rating', '-points')[:3]

    return render(request, 'member/leaderboard.html', {
        'top_members': top_members
    })

@login_required
def profile_view(request):
    return redirect('user_profile', username=request.user.username)

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    items_shared = Item.objects.filter(owner=user).count()
    items_avail = Item.objects.filter(owner=user, status='Available').count()
    reviews = Review.objects.filter(item__owner=user)
    
    return render(request, 'member/profile.html', {
        'profile_user': user,
        'items_shared': items_shared,
        'items_avail': items_avail,
        'reviews': reviews,
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'member/profile_edit.html', {'form': form})

# Member Views
@login_required
@member_required
def my_items(request):
    items = Item.objects.filter(owner=request.user)
    return render(request, 'member/my_items.html', {'items': items})

@login_required
@member_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            messages.success(request, "Item added.")
            return redirect('my_items')
    else:
        form = ItemForm()
    return render(request, 'member/item_form.html', {'form': form})

@login_required
@member_required
def edit_item(request, item_id):
    item = get_object_or_404(
    Item,
    id=item_id,
    owner=request.user,
    status='Available'   # Only editable if available
)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated.")
            return redirect('my_items')
    else:
        form = ItemForm(instance=item)
    return render(request, 'member/item_form.html', {'form': form, 'is_edit': True})

@login_required
@member_required
def my_requests(request):
    requests = BorrowRequest.objects.filter(requester=request.user)
    return render(request, 'member/my_requests.html', {'requests': requests})

@login_required
@member_required
def incoming_requests(request):
    requests = BorrowRequest.objects.filter(item__owner=request.user, status='Pending')
    return render(request, 'member/incoming_requests.html', {'requests': requests})

@login_required
@member_required
def approve_request(request, req_id):
    req = get_object_or_404(BorrowRequest, id=req_id, item__owner=request.user)
    if req.item.status != 'Available':
        messages.error(request, "Item is no longer available.")
        return redirect('incoming_requests')

    req.status = 'Approved'
    req.approved_at = datetime.now()
    req.save()
    
    req.item.status = 'Approved'
    req.item.save()
    
    BorrowHistory.objects.create(borrow_request=req)
    
    # Reject other pending requests for this item
    BorrowRequest.objects.filter(item=req.item, status='Pending').exclude(id=req.id).update(
        status='Rejected', rejection_message="Item approved for another user."
    )
    
    messages.success(request, "Request approved.")
    return redirect('incoming_requests')

@login_required
@member_required
def reject_request(request, req_id):
    req = get_object_or_404(BorrowRequest, id=req_id, item__owner=request.user)
    if request.method == 'POST':
        message = request.POST.get('rejection_message', '')
        req.status = 'Rejected'
        req.rejection_message = message
        req.save()
        messages.success(request, "Request rejected.")
        return redirect('incoming_requests')
    return render(request, 'member/reject_form.html', {'req': req})

@login_required
@member_required
def mark_collected(request, req_id):
    req = get_object_or_404(
        BorrowRequest,
        id=req_id,
        requester=request.user,   # FIXED
        status='Approved'
    )

    req.history.collected_on = datetime.now()
    req.history.save()

    messages.success(request, "Item marked as collected.")
    return redirect('my_requests')

@login_required
@member_required
def review_item(request, req_id):
    req = get_object_or_404(BorrowRequest, id=req_id, requester=request.user, status='Approved')
    
    if not req.history.collected_on:
        messages.error(request, "You can only review after collecting the item.")
        return redirect('my_requests')
        
    if req.reviewed:
        messages.error(request, "You have already reviewed this item.")
        return redirect('my_requests')
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = req.item
            review.reviewer = request.user
            review.save()
            
            req.reviewed = True
            req.save()
            
            req.history.closed_at = datetime.now()
            req.history.save()
            
            req.item.status = 'Closed'
            req.item.save()
            
            # Update user stats
            owner = req.item.owner
            owner.points += 10
            
            all_reviews = Review.objects.filter(item__owner=owner)
            total_rating = sum(r.rating for r in all_reviews)
            owner.average_rating = total_rating / all_reviews.count()
            owner.save()
            
            messages.success(request, "Review submitted successfully.")
            return redirect('my_requests')
    else:
        form = ReviewForm()
    return render(request, 'member/review_form.html', {'form': form, 'item': req.item})

# Admin Views
@login_required
@admin_required
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'member/admin_categories.html', {'categories': categories})

@login_required
@admin_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'member/category_form.html', {'form': form})

@login_required
@admin_required
def manage_users(request):
    users = User.objects.filter(role='Member')
    return render(request, 'member/admin_users.html', {'users': users})

@login_required
@admin_required
def toggle_block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    status = "blocked" if user.is_blocked else "unblocked"
    messages.success(request, f"User {status}.")
    return redirect('manage_users')

@login_required
@admin_required
def all_items(request):
    items = Item.objects.all()
    return render(request, 'member/admin_items.html', {'items': items})

@login_required
@admin_required
def toggle_item_active(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.is_active = not item.is_active
    item.save()
    status = "activated" if item.is_active else "deactivated"
    messages.success(request, f"Item {status}.")
    return redirect('all_items')

@login_required
@admin_required
def all_borrow_records(request):
    records = BorrowHistory.objects.select_related(
        'borrow_request',
        'borrow_request__item',
        'borrow_request__requester',
        'borrow_request__item__owner'
    ).all()

    return render(request, 'member/admin_borrow_records.html', {
        'records': records
    })

@login_required
@admin_required
def monitor_reviews(request):
    reviews = Review.objects.all()
    return render(request, 'member/admin_reviews.html', {'reviews': reviews})
