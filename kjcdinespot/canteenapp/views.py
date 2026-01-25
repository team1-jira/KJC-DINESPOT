from django.shortcuts import render, redirect, get_object_or_404
from main.models import User, Block, Canteen, Contact
from .models import Item, CartItem, Reviews, Payment
from django.http import Http404
from django.utils.timezone import now
from django.contrib import messages
from .forms import CanteenForm, UserForm, BlockForm, ItemForm
from django.db.models import Sum
from django.db.models import Count
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import render_to_string
from decimal import Decimal  
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.utils import timezone


def get_usernotifications(request):
    user_id = request.session.get('user_id') or request.user.id
    user = get_object_or_404(User, pk=user_id)
    """Fetches order status updates for the logged-in user."""
    today = now().date()
    
    notifications = CartItem.objects.filter(
        user=user,
        ordered=True,
        ordered_date__date=today,  
        status__in=['Ready', 'Delivered']  
    ).values_list('item__title', 'status') 

    notifications_list = [
        f"Your order '{item_title}' is now {status}."
        for item_title, status in notifications
    ]

    return JsonResponse({
        "count": len(notifications_list),
        "orders": notifications_list
    })

def get_notifications(request):
    user_id = request.session.get('user_id') or request.user.id
    caterer = get_object_or_404(User, pk=user_id)
    
    try:
        canteen = Canteen.objects.get(caterer=caterer)
        today = timezone.now().date()
        orders = CartItem.objects.filter(
            item__canteen=canteen,
            ordered=True, 
            status='Preparing',
            ordered_date__date=today
        )

        new_orders_count = orders.count()
        order_details = [
            f"Order {order.id} : {order.quantity} x {order.item.title}"
            for order in orders
        ]

        return JsonResponse({'count': new_orders_count, 'orders': order_details})
    except Canteen.DoesNotExist:
        return JsonResponse({'count': 0, 'orders': []})

def block_list(request):
    blocks = Block.objects.prefetch_related('canteens').all()
    return render(request, 'block_list.html', {'blocks': blocks})

def block_canteens(request, block_id):
    block = get_object_or_404(Block, id=block_id)
    canteens = Canteen.objects.filter(block=block)
    return render(request, 'canteen_list.html', {
        'block': block,
        'block_name': block.block_name,
        'canteens': canteens,
    })
def canteen_menu(request, canteen_id):
    user_id = request.session.get('user_id') or request.user.id
    user = get_object_or_404(User, pk=user_id)
    canteen = get_object_or_404(Canteen, id=canteen_id)

    items = Item.objects.filter(canteen=canteen).prefetch_related("reviews")

    if request.method == "POST":
        selected_category = request.POST.get("category", "All")
        if selected_category and selected_category != "All":
            items = items.filter(category=selected_category)

    return render(request, 'canteen_menu.html', {'user': user, 'canteen': canteen, 'items': items})
def add_review(request, item_id):
    if request.method == "POST":
        user_id = request.session.get('user_id') or request.user.id
        user = get_object_or_404(User, pk=user_id)
        item = get_object_or_404(Item, id=item_id)
        review_text = request.POST.get('review', '').strip()
        rating = request.POST.get('rating')

        if not review_text or not rating:
            return render(request, 'canteen_menu.html', {'error': 'Review and rating are required.'})

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return render(request, 'canteen_menu.html', {'error': 'Rating must be between 1 and 5.'})
        except ValueError:
            return render(request, 'canteen_menu.html', {'error': 'Invalid rating value.'})

        Reviews.objects.create(
            item=item,
            user=user,
            review=review_text,
            rating=rating
        )

        return redirect('canteen_menu', canteen_id=item.canteen.id)  
    
def caterer_main(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:login')

    user = get_object_or_404(User, pk=user_id)
    canteen = Canteen.objects.filter(caterer=user).first()

    if canteen:
        items = Item.objects.filter(canteen=canteen)
        orders = CartItem.objects.filter(item__canteen=canteen, ordered=True)
        total_earnings = canteen.revenue
        total_delivered = orders.filter(status='Delivered').count()
        total_pending = orders.filter(status__in=['Preparing', 'Ready']).count()
        today_orders = orders.filter(ordered_date__date=now().date())
        today_earnings = today_orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        today_earnings *= today_orders.first().item.price if today_orders.exists() else 0
        today_delivered = today_orders.filter(status='Delivered').count()
        today_pending = today_orders.filter(status__in=['Preparing', 'Ready']).count()
        category_counts = orders.values('item__category').annotate(count=Count('id'))
        categories = [c['item__category'] for c in category_counts]
        category_values = [c['count'] for c in category_counts]

    else:
        items = []
        total_earnings = total_delivered = total_pending = 0
        today_earnings = today_delivered = today_pending = 0
        categories, category_values = [], []

    return render(request, 'caterer_main.html', {
        'user': user,
        'canteen': canteen,
        'items': items,
        'total_earnings': total_earnings,
        'total_delivered': total_delivered,
        'total_pending': total_pending,
        'today_earnings': today_earnings,
        'today_delivered': today_delivered,
        'today_pending': today_pending,
        'categories': categories,
        'category_values': category_values,
    })


def manage_users(request):
    search_name = request.GET.get('search_name', '')
    if search_name:
        users = User.objects.filter(name__icontains=search_name).order_by('name')
    else:
        users = User.objects.all().order_by('name')
    return render(request, 'manage_user.html', {'users': users, 'search_name': search_name})

def manage_blocks(request):
    search_name = request.GET.get('search_name', '')
    if search_name:
        blocks = Block.objects.filter(block_name__icontains=search_name).order_by('block_name')
    else:
        blocks = Block.objects.all().order_by('block_name')
    return render(request, 'manage_block.html', {'blocks': blocks, 'search_name': search_name})

def manage_canteen(request):
    search_name = request.GET.get('search_name', '')
    if search_name:
        canteens = Canteen.objects.filter(canteen_name__icontains=search_name).order_by('canteen_name')
    else:
        canteens = Canteen.objects.all().order_by('canteen_name')
    return render(request, 'manage_canteen.html', {'canteens': canteens, 'search_name': search_name})

def delete_canteen(request, id):
    if request.method == 'POST':
        canteen = get_object_or_404(Canteen, id=id)
        canteen.delete()
        return redirect('manage_canteen')
    return redirect('manage_canteen')

def add_canteen(request):
    if request.method == 'POST':
        form = CanteenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_canteen')
    else:
        form = CanteenForm()
    return render(request, 'add_canteen.html', {'form': form})

def update_canteen(request, id):
    canteen = get_object_or_404(Canteen, id=id)
    if request.method == 'POST':
        form = CanteenForm(request.POST, instance=canteen)
        if form.is_valid():
            form.save()
            return redirect('manage_canteen')
    else:
        form = CanteenForm(instance=canteen)
    return render(request, 'update_canteen.html', {'form': form, 'canteen': canteen})

def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User added successfully!")
            return redirect('manage_users')
    else:
        form = UserForm()
    return render(request, 'add_user.html', {'form': form})

def update_user(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect('manage_users')
    else:
        form = UserForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'user':user})

def delete_user(request, id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=id)
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('manage_users')
    return redirect('manage_users')

def add_block(request):
    if request.method == 'POST':
        form = BlockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_blocks')
    else:
        form = BlockForm()
    return render(request, 'add_block.html', {'form': form})

def update_block(request, pk):
    block = get_object_or_404(Block, pk=pk)
    if request.method == 'POST':
        form = BlockForm(request.POST, instance=block)
        if form.is_valid():
            form.save()
            return redirect('manage_blocks')
    else:
        form = BlockForm(instance=block)
    return render(request, 'update_block.html', {'form': form, 'block': block})

def delete_block(request, pk):
    block = get_object_or_404(Block, pk=pk)
    block.delete()
    messages.success(request, "Block deleted successfully!")
    return redirect('manage_blocks')
def manage_items(request):
    user_id = request.session.get('user_id') or request.user.id
    user = get_object_or_404(User, pk=user_id)
    canteen = get_object_or_404(Canteen, caterer=user)
    search_title = request.GET.get('search_title', '')

    if search_title:
        items = Item.objects.filter(canteen=canteen, title__icontains=search_title)
    else:
        items = Item.objects.filter(canteen=canteen)

    context = {
        'items': items,
        'canteen': canteen,
        'search_title': search_title
    }
    return render(request, 'manage_items.html', context)

def add_item(request):
    user_id = request.session.get('user_id') or request.user.id
    caterer = get_object_or_404(User, pk=user_id)
    canteen = get_object_or_404(Canteen, caterer=caterer)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.caterer = caterer  
            item.canteen = canteen  
            item.save()  
            return redirect('manage_items')  
    else:
        form = ItemForm()

    context = {
        'form': form,
        'canteen': canteen
    }
    return render(request, 'add_item.html', context)


def process_payment(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    cart_items = CartItem.objects.filter(user=user, ordered=False)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty! Add items before proceeding.")
        return redirect('view_cart')
    
    payment_method = request.POST.get('payment_method')  
    total_payment = sum(Decimal(item.subtotal()) for item in cart_items) 
    status = "Completed" if payment_method in ["UPI", "Card"] else "Pending"  

    with transaction.atomic():
       
        payment = Payment.objects.create(
            user=user,
            amount=total_payment,
            payment_method=payment_method,
            payment_status=status,
            payment_date=now()
        )

        
        for cart_item in cart_items:
            cart_item.ordered = True
            cart_item.ordered_date = now()
            cart_item.payment_status = status
            cart_item.payment = payment  
            cart_item.save()
            canteen = cart_item.item.canteen  
            canteen.revenue += Decimal(cart_item.subtotal())  
            canteen.save()

        payment.cart_items.set(cart_items)
        html_content = render(request, 'bill.html', {
        'user': user,
        'payment': payment,
        'cart_items': cart_items,
        'total_payment': total_payment
         }).content.decode('utf-8')


    return JsonResponse({"status": "success", "bill_html": html_content})

def update_item(request, item_id):
    user_id = request.session.get('user_id') or request.user.id
    caterer = get_object_or_404(User, pk=user_id)
    item = get_object_or_404(Item, pk=item_id, canteen__caterer=caterer)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('manage_items')  
    else:
        form = ItemForm(instance=item)

    return render(request, 'update_item.html', {'form': form, 'item': item})


def delete_item(request, item_id):
    user_id = request.session.get('user_id') or request.user.id
    caterer = get_object_or_404(User, pk=user_id)
    item = get_object_or_404(Item, pk=item_id, canteen__caterer=caterer)

    if request.method == "POST":
        item.delete()  
        return redirect('manage_items') 

    context = {
        'item': item,
    }
    return render(request, 'delete_item.html', context)

def add_to_cart(request, item_id):
    user_id = request.session.get('user_id')  
    user = get_object_or_404(User, id=user_id)
    item = get_object_or_404(Item, id=item_id)

    cart_item, created = CartItem.objects.get_or_create(user=user, item=item, ordered=False)

    if not created:
        cart_item.quantity += 1  
        cart_item.save()
    else:
        cart_item.quantity = 1  
        cart_item.save()

    return redirect('view_cart')  

def view_cart(request):
    user_id = request.session.get('user_id') 
    user = get_object_or_404(User, id=user_id)
    cart_items = CartItem.objects.filter(user=user, ordered=False)

    total_price = sum(item.subtotal() for item in cart_items)
    total_pieces = sum(item.quantity for item in cart_items)
    num_boxes = len(cart_items)

    canteen = cart_items.first().item.canteen if cart_items.exists() else None

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_pieces': total_pieces,
        'num_boxes': num_boxes,
        'canteen': canteen,
    }
    return render(request, "cart.html", context)

def remove_from_cart(request, pk):
    user_id = request.session.get('user_id') or request.user.id
    user = User.objects.get(id=user_id)
    cart_item = CartItem.objects.get(pk=pk, user=user, ordered=False)
    cart_item.delete()
    return redirect('view_cart')


def update_cart_quantity(request, pk, action):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    cart_item = get_object_or_404(CartItem, pk=pk, user=user, ordered=False)
    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1

    cart_item.save()
    return redirect('view_cart')

def checkout(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    cart_items = CartItem.objects.filter(user=user, ordered=False)

    if cart_items.exists():
        cart_items.update(ordered=True)
        messages.success(request, "Your order has been placed successfully! ✅")

    return redirect('order-summary') 

def order_summary(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)

    orders = CartItem.objects.filter(user=user, ordered=True).order_by('-ordered_date')

    for order in orders:
        order.review_exists = order.item.reviews.exists()
        order.payment_status = order.payment.payment_status if order.payment else 'Pending'

    return render(request, 'order_summary.html', {'orders': orders})

def caterer_orders(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    canteen = get_object_or_404(Canteen, caterer=user)
    orders = CartItem.objects.filter(item__canteen=canteen, ordered=True).exclude(status='Delivered').order_by('-ordered_date')

    return render(request, 'caterer_orders.html', {'orders': orders})


def completed_orders(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    canteen = get_object_or_404(Canteen, caterer=user)
    orders = CartItem.objects.filter(item__canteen=canteen, ordered=True, status='Delivered').order_by('-ordered_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)
    if start_date and end_date:
        orders = orders.filter(ordered_date__range=[start_date, end_date])

    return render(request, 'completed_orders.html', {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date
    })


def active_orders(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    canteen = get_object_or_404(Canteen, caterer=user)

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")

        order = get_object_or_404(CartItem, id=order_id)

        if order.item.canteen == canteen:
            order.status = new_status
            if new_status == "Delivered":
                order.delivery_date = now()
                order.ordered = True  
                order.payment_status= "Completed"
            order.save()

    orders = CartItem.objects.filter(item__canteen=canteen, ordered=True).exclude(status="Delivered")
    return render(request, "caterer_orders.html", {"orders": orders})

def caterer_reviews(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id) 
    try:
        canteen = Canteen.objects.get(caterer=user) 
        items = Item.objects.filter(canteen=canteen)  
        reviews = Reviews.objects.filter(item__in=items).select_related('user', 'item') 
    except Canteen.DoesNotExist:
        reviews = []  
    return render(request, 'review.html', {'reviews': reviews})
