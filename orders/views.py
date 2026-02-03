from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from carts.models import Cart
from .models import Order, OrderItem
import stripe
from django.conf import settings
from django.urls import reverse
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        return redirect('cart_detail')

    total = sum(item.total_price() for item in cart_items)

    payment_method = request.POST.get('payment_method', 'cod')

    order = Order.objects.create(
        user=request.user,
        total_price=total,
        payment_method=payment_method,
        is_paid=False
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    
    cart_items.delete()
    if payment_method == 'cod':
        return redirect('orders:order_detail', order_id=order.id)  
    return redirect('orders:stripe_checkout', order_id=order.id)

@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    for item in order.items.all():
        item.total_price = item.quantity * item.price
    return render(request, 'orders/order_detail.html', {
        'order': order
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })


@login_required
def stripe_checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        return redirect('orders:order_detail', order_id=order.id)

    line_items = []

    for item in order.items.all():   
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse('orders:payment_success', args=[order.id])
        ),
        cancel_url=request.build_absolute_uri(
            reverse('orders:payment_cancel', args=[order.id])
        ),
    )

    order.stripe_session_id = session.id
    order.save()

    return redirect(session.url)

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.is_paid = True
    order.save()

    return render(request, 'orders/payment_success.html', {
        'order': order
    })


@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment_cancel.html', {
        'order': order
    })

