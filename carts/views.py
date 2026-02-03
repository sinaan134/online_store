from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart,Cartitem

def get_cart(user):
    cart,created=Cart.objects.get_or_create(user=user)
    return cart

@login_required
def add_to_cart(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    cart=get_cart(request.user)
    cart_item,created=Cartitem.objects.get_or_create(cart=cart,product=product)
    if not created :
        cart_item.quantity+=1
    cart_item.save()

    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart=get_cart(request.user)
    items=cart.items.all()

    total=sum(item.total_price() for item in items)

    return render(request,'carts/cart_detail.html',{ 'cart':cart,'items':items,'total':total})

@login_required
def remove_from_cart(request,item_id):
    item=get_object_or_404(Cartitem,id=item_id)
    item.delete()
    return redirect('cart_detail')

@login_required
def update_cart_quantity(request,item_id):
    item=get_object_or_404(Cartitem,id=item_id)
    if request.method=='POST':
        quantity=int(request.POST.get('quantity'))
        if quantity>0:
            item.quantity=quantity
            item.save()
    return redirect('cart_detail')

