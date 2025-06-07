from django.urls import path
from . import views
from django.contrib.auth.decorators import user_passes_test

def can_edit_paid_sale(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

urlpatterns = [
    path('warehouse/', views.warehouse_list, name='warehouse_list'),
    path('warehouse/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouse/<int:pk>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('warehouse/<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),



    path('product/', views.product_list, name='product_list'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),


    path('customer/', views.customer_list, name='customer_list'),
    path('customer/create/', views.customer_create, name='customer_create'),
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),   


    path('products/export-selected/', views.export_selected_products_pdf, name='export_selected_products_pdf'),


    path('sale/', views.sale_list, name='sale_list'),
    path('sale/add/', views.sale_create, name='sale_create'),
    path('sale/<int:pk>/edit/', views.sale_edit, name='sale_edit'),
    path('sale/<int:pk>/delete/', views.sale_delete, name='sale_delete'),


    path('market-price/', views.market_price_list, name='market_price_list'),
    path('market-price/add/', views.market_price_create, name='market_price_create'),
    path('market-price/<int:pk>/edit/', views.market_price_edit, name='market_price_edit'),
    path('market-price/<int:pk>/delete/', views.market_price_delete, name='market_price_delete'),



    path('cost-price/', views.cost_price_list, name='cost_price_list'),
    path('cost-price/add/', views.cost_price_create, name='cost_price_create'),
    path('cost-price/<int:pk>/edit/', views.cost_price_edit, name='cost_price_edit'),
    path('cost-price/<int:pk>/delete/', views.cost_price_delete, name='cost_price_delete'),


    path('sale/<int:pk>/toggle-payment/', views.toggle_payment_status, name='toggle_payment_status'),
                

    # ...existing URL patterns...
    path('sale/<int:pk>/edit/', 
        user_passes_test(can_edit_paid_sale)(views.sale_edit), 
        name='sale_edit'),
    path('sale/<int:pk>/delete/', 
        user_passes_test(can_edit_paid_sale)(views.sale_delete), 
        name='sale_delete'),

    
    
    path('sale/generate-invoice/', views.generate_invoice, name='generate_invoice'),
    path('sale/invoice/', views.invoice_view, name='invoice_view'),





    
    path('product/<int:pk>/confirm/', views.product_confirm, name='product_confirm'),

    # ใน urls.py
    path('products/<int:product_id>/update-status/', views.update_product_status, name='update_product_status'),
    path('product/<int:pk>/confirm/', views.product_confirm, name='product_confirm'),

    path('<int:pk>/invoice/', views.sale_invoice, name='sale_invoice'),



    path('dashboard/', views.dashboard, name='dashboard'),



    path('quatation/', views.quatation_list, name='quatation_list'),
    path('quatation/add/', views.quatation_create, name='quatation_create'),
    path('quatation/<int:pk>/edit/', views.quatation_edit, name='quatation_edit'),
    path('quatation/<int:pk>/delete/', views.quatation_delete, name='quatation_delete'),


    

    path('quatation/<int:pk>/invoice/', views.quatation_invoice, name='quatation_invoice'),
   
    path('quatation/summary/', views.quatation_summary, name='quatation_summary'),



     path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

]