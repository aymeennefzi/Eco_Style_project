from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Product, Category
from cart.views import _cart_id
from cart.models import CartItem
from .models import ReviewRating
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from .models import ProductGallery

def home(request):
    products = Product.objects.all().filter(is_available=True)
    
    context = {
        'products' : products,
    }
    return render(request, 'shop/index.html', context)


def shop(request, category_slug=None):
    categories = None
    products = None
    

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products_count = products.count()
        
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        products_count = products.count()
        
    
    for product in products:
        reviews = ReviewRating.objects.order_by('-updated_at').filter(product_id=product.id, status=True)

    context = {
        'category_slug': category_slug,
        'products' : paged_products,
        'products_count': products_count,
        
    }
    return render(request, 'shop/shop/shop.html', context)



def product_details(request, category_slug, product_details_slug):
    from .models import Wishlist, WishlistItem, Notification
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_details_slug)
        
        # Check if the product is in the cart
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Product.DoesNotExist:
        return render(request, '404.html')  # Render a 404 page if the product does not exist

    # Check if the product was previously ordered by the user
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
        
        try:
            wishlist = request.user.wishlist  
            in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product=single_product).exists()
        except Wishlist.DoesNotExist:
            in_wishlist = False

        # Check if the user has a notification for the product
        notification = Notification.objects.filter(user=request.user, product=single_product).first()
        have_notification = notification is not None
    else:
        orderproduct = None
        in_wishlist = False
        notification = None
        have_notification = False

    # Fetch reviews and gallery images for the product
    reviews = ReviewRating.objects.order_by('-updated_at').filter(product_id=single_product.id, status=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    # Pass the variables to the template context
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'in_wishlist': in_wishlist,
        'notification': notification,  # Add this line
        'have_notification': have_notification,  # Add this line
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'shop/shop/product_details.html', context)



# 9DIMA

# def product_details(request, category_slug, product_details_slug):
#     try:
#         single_product = Product.objects.get(category__slug=category_slug, slug=product_details_slug)
        
#         in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
#     except Exception as e:
#         return e

#     if request.user.is_authenticated:
#         try:
#             orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
#         except OrderProduct.DoesNotExist:
#             orderproduct = None
#     else:
#         orderproduct = None

#     reviews = ReviewRating.objects.order_by('-updated_at').filter(product_id=single_product.id, status=True)
#     product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

#     context = {
#         'single_product': single_product,
#         'in_cart': in_cart,
#         'orderproduct':orderproduct,
#         'reviews': reviews,
#         'product_gallery':product_gallery,
#     }
#     return render(request, 'shop/shop/product_details.html', context)


def search(request):
    products_count = 0
    products = None
    paged_products = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword :
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            
            products_count = products.count()
            
    
    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'shop/shop/search.html', context)



def review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you, your review updated!')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you, your review Posted!')
                return redirect(url)







#AZIZ
def add_to_wishlist(request, product_id):
    from shop.models import Wishlist, WishlistItem
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    messages.success(request, 'Product has been added to your wishlist successfully.')

    
    # Check if the product is already in the wishlist
    if not WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
        WishlistItem.objects.create(wishlist=wishlist, product=product)
    
    return redirect('/shop/aa/aaa/')


def remove_from_wishlist(request, product_id):
    from shop.models import Wishlist, WishlistItem
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    messages.success(request, 'Product has been removed from your wishlist successfully.')

    
    WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
    return redirect('/shop/aa/aaa/')


def wishlist_view(request):
    from . models import Wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.all()  
    return render(request, 'shop/shop/wishlist.html', {'wishlist': wishlist, 'items': items})



def is_in_wishlist(request, product_id):
    from shop.models import Wishlist, WishlistItem
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse

    user = request.user  # Get the currently logged-in user
    product = get_object_or_404(Product, id=product_id)  # Get the product or return 404 if not found
    
    try:
        # Check if the user has a wishlist and if it contains the product
        wishlist = user.wishlist  # Assuming 'wishlist' is the related name in User's wishlist relation
        item_exists = WishlistItem.objects.filter(wishlist=wishlist, product=product).exists()
    except Wishlist.DoesNotExist:
        # If the user doesn't have a wishlist, they don't have any items in it
        item_exists = False

    return JsonResponse({'in_wishlist': item_exists})






from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Notification
from .forms import NotificationForm,NotificationUpdateForm

def list_notifications(request):
    notifications = Notification.objects.all()
    data = [{"id": n.id, "user": n.user.username, "product": n.product.name, "created_at": n.created_at, "is_read": n.is_read, "message": n.message, "notify_on_sale": n.notify_on_sale} for n in notifications]
    return JsonResponse(data, safe=False)

def get_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    data = {"id": notification.id, "user": notification.user.username, "product": notification.product.name, "created_at": notification.created_at, "is_read": notification.is_read, "message": notification.message, "notify_on_sale": notification.notify_on_sale}
    return JsonResponse(data)





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import NotificationForm
from .models import Notification





from django.shortcuts import redirect

def create_notification(request):
    print("Request POST data:", request.POST)
    form = NotificationForm(request.POST)
    if form.is_valid():
        notification = form.save()
        return redirect('shop:product_details', category_slug=notification.product.category.slug, product_details_slug=notification.product.slug)
    else:
        print("Form errors:", form.errors)
        errors = {field: error.get_json_data() for field, error in form.errors.items()}
        return JsonResponse(errors, status=400)




def check_notification(request, user_id, product_id):
    from accounts.models import Account
    try:
        user = Account.objects.get(id=user_id)
        product = Product.objects.get(id=product_id)
        notification_exists = Notification.objects.filter(user=user, product=product).exists()
        return JsonResponse({"notification_exists": notification_exists})
    except (Account.DoesNotExist, Product.DoesNotExist):
        return HttpResponseBadRequest("User or Product does not exist")
    


def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    product = notification.product
    notification.delete()
    return redirect('shop:product_details', category_slug=product.category.slug, product_details_slug=product.slug)

def update_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    form = NotificationUpdateForm(request.POST, instance=notification) 
    if form.is_valid():
        notification = form.save()
        return redirect('shop:product_details', category_slug=notification.product.category.slug, product_details_slug=notification.product.slug)
    else:
        print("Form errors:", form.errors)
        errors = {field: error.get_json_data() for field, error in form.errors.items()}
        return JsonResponse(errors, status=400)





#ai

# def churn_prediction_view(request):
#     from .forms import ChurnPredictionForm
#     from model_utils import load_model
#     print("Request method:", request.method)
#     prediction = None
#     if request.method == 'POST':
#         form = ChurnPredictionForm(request.POST)
#         if form.is_valid():
#             model = load_model()
#             # Extract the data from the form
#             input_data = form.cleaned_data
#             features = [
#                 input_data['age'],
#                 input_data['gender'],
#                 input_data['item_purchased'],
#                 input_data['category'],
#                 input_data['purchase_amount'],
#                 input_data['location'],
#                 input_data['size'],
#                 input_data['color'],
#                 input_data['season'],
#                 input_data['review_rating'],
#                 input_data['subscription_status'],
#                 input_data['shipping_type'],
#                 input_data['discount_applied'],
#                 input_data['promo_code_used'],
#                 input_data['previous_purchases'],
#                 input_data['payment_method'],
#                 input_data['frequency_of_purchases'],
#             ]

#             # Prepare the data for prediction (ensure it matches the training format)
#             features = [features]  # Create a 2D array
#             prediction = model.predict(features)

#     else:
#         form = ChurnPredictionForm()

#     return render(request, 'shop/shop/product_details.html')
