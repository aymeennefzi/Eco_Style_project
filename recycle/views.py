from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import RecycledItem, DropPoint
from .forms import RecycledItemForm

def recycle(request):
    """Homepage view showing recent recycled items and featured drop points"""
    featured_points = DropPoint.objects.all()
    recent_items = RecycledItem.objects.filter(status='confirmed').order_by('-created_at')[:6]

    context = {
        'recent_items': recent_items,
        'featured_points': featured_points,
    }
    return render(request, 'shop/recycle/recycle.html', context)

@login_required
def my_recycled_items(request):
    """Display paginated list of user's recycled items"""
    items_list = RecycledItem.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(items_list, 9)  # Show 9 items per page
    page = request.GET.get('page')
    
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    
    context = {
        'recycled_items': items,
    }
    return render(request, 'shop/recycle/my_recycled_items.html', context)

@login_required
def donate_item(request):
    """Handle new item donation"""
    if request.method == 'POST':
        form = RecycledItemForm(request.POST, request.FILES)
        if form.is_valid():
            recycled_item = form.save(commit=False)
            recycled_item.user = request.user
            recycled_item.save()
            messages.success(request, 'Item submitted successfully for recycle!')
            return redirect('recycle:my_recycled_items')
    else:
        form = RecycledItemForm()
    
    context = {
        'form': form,
        'drop_points': DropPoint.objects.all(),
    }
    return render(request, 'shop/recycle/donate_item.html', context)

def drop_points_list(request):
    """Display paginated list of all drop points"""
    points_list = DropPoint.objects.all()
    paginator = Paginator(points_list, 6)  # Show 6 drop points per page
    page = request.GET.get('page')
    
    try:
        points = paginator.page(page)
    except PageNotAnInteger:
        points = paginator.page(1)
    except EmptyPage:
        points = paginator.page(paginator.num_pages)
        
    context = {
        'drop_points': points,
    }
    return render(request, 'shop/recycle/drop_points_list.html', context)

@login_required
def recycled_item_detail(request, item_id):
    """Display details of a specific recycled item"""
    item = get_object_or_404(RecycledItem, id=item_id, user=request.user)
    context = {
        'item': item,
    }
    return render(request, 'shop/recycle/recycled_item_details.html', context)

def drop_point_detail(request, point_id):
    """Display details of a specific drop point"""
    point = get_object_or_404(DropPoint, id=point_id)
    recent_items = RecycledItem.objects.filter(
        drop_point=point,
        status='confirmed'
    ).order_by('-created_at')[:5]
    
    context = {
        'point': point,
        'recent_items': recent_items,
    }
    return render(request, 'shop/recycle/drop_point_details.html', context)

""" def search(request):
    items = None
    points = None
    items_count = 0
    points_count = 0
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            items = RecycledItem.objects.filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            ).filter(status='confirmed')
            points = DropPoint.objects.filter(
                Q(name__icontains=keyword) |
                Q(location__icontains=keyword) |
                Q(description__icontains=keyword)
            )
            items_count = items.count()
            points_count = points.count()
    
    context = {
        'items': items,
        'points': points,
        'items_count': items_count,
        'points_count': points_count,
        'keyword': keyword if 'keyword' in request.GET else '',
    }
    return render(request, 'shop/recycle/search.html', context)
    """