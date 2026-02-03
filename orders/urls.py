from django.urls import path
from . import views
app_name = 'orders'
urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('', views.order_list, name='order_list'),
    path('stripe/checkout/<int:order_id>/', views.stripe_checkout, name='stripe_checkout'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/<int:order_id>/', views.payment_cancel, name='payment_cancel'),

]