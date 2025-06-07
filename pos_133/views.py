from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST  # Add this import
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Warehouse, Costprice, MarketPrice, Sale, Customer
from .forms import ProductForm, CostPriceForm, MarketPriceForm, SaleForm, CustomerForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User

# ...rest of the file remains the same...

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

@ensure_csrf_cookie
def login_user(request):
    # Force CSRF token creation
    get_token(request)
    
    if request.user.is_authenticated:
        return redirect('home')

    # Add debug logging
    print("Request Method:", request.method)
    print("CSRF Cookie:", request.COOKIES.get('csrftoken'))
    print("CSRF Header:", request.META.get('HTTP_X_CSRFTOKEN'))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    
    return render(request, 'registration/login.html', {
        'next': request.GET.get('next', '/')
    })







def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'home.html')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Warehouse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('pos_133.view_warehouse', raise_exception=True)
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse/warehouse_list.html', {'warehouses': warehouses})

@login_required 
@permission_required('pos_133.add_warehouse', raise_exception=True)
def warehouse_create(request):
    if request.method == 'POST':
        warehouse_w = request.POST.get('warehouse_w')
        location = request.POST.get('location')
        Warehouse.objects.create(warehouse_w=warehouse_w, location=location)
        messages.success(request, 'เพิ่มคลังสินค้าเรียบร้อยแล้ว')
        return redirect('warehouse_list')
    return render(request, 'warehouse/warehouse_form.html')

@login_required
@permission_required('pos_133.change_warehouse', raise_exception=True)
def warehouse_edit(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.warehouse_w = request.POST.get('warehouse_w')
        warehouse.location = request.POST.get('location')
        warehouse.save()
        messages.success(request, 'แก้ไขคลังสินค้าเรียบร้อยแล้ว')
        return redirect('warehouse_list')
    return render(request, 'warehouse/warehouse_form.html', {'warehouse': warehouse})

@login_required
@permission_required('pos_133.delete_warehouse', raise_exception=True)
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, 'ลบคลังสินค้าเรียบร้อยแล้ว')
        return redirect('warehouse_list')
    return render(request, 'warehouse/warehouse_confirm_delete.html', {'warehouse': warehouse})





@login_required
@permission_required('pos_133.view_product', raise_exception=True)
def product_list(request):
    products = Product.objects.all().order_by('productid')
    close_stock_products = products.filter(quantity_in_stock__lte=5)
    search_query = request.GET.get('search', '')
    
    # ค้นหาสินค้า
    
    if search_query:
        products = products.filter(
            Q(productid__icontains=search_query) |
            Q(pname__icontains=search_query)
        )
    
    # แบ่งหน้า
    paginator = Paginator(products, 5)  # 5 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_query': search_query,
    }
    if close_stock_products.exists():
        messages.warning(
            request, 
            f'พบสินค้าใกล้หมดสต็อก {close_stock_products.count()} รายการ'
        )
    
    return render(request, 'product/product_list.html', {
        'products': products,
        'close_stock_count': close_stock_products.count()
    })
    

@login_required
@permission_required('pos_133.add_product', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มสินค้าเรียบร้อยแล้ว')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product/product_form.html', {'form': form, 'title': 'Create Product'})

@login_required
@permission_required('pos_133.change_product', raise_exception=True)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
     # ตรวจสอบสิทธิ์การแก้ไข
    if product.stock_status == 'close_stock' and not request.user.is_superuser:
        messages.error(request, 'ไม่มีสิทธิ์แก้ไขสินค้าที่ปิดสต็อกแล้ว')
        return redirect('product_list')
        
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขรายการสินค้าสำเร็จ')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product/product_form.html', {
        'form': form,
        'title': 'แก้ไขสินค้า'
    })

@login_required
@permission_required('pos_133.delete_product', raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
   # ตรวจสอบสิทธิ์การลบ
    if product.stock_status == 'close_stock' and not request.user.is_superuser:
        messages.error(request, 'ไม่มีสิทธิ์ลบสินค้าที่ปิดสต็อกแล้ว')
        return redirect('product_list')
        
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'ลบรายการสินค้าสำเร็จ')
        return redirect('product_list')
    return render(request, 'product/product_confirm_delete.html', {'product': product})


@login_required

@require_POST
@permission_required('pos_133.change_product', raise_exception=True)
def update_product_status(request, product_id):
    try:
        data = json.loads(request.body)
        product = get_object_or_404(Product, pk=product_id)
        new_status = data.get('status')
        
        # Only allow status change if open or superuser
        if product.stock_status == 'close_stock' and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'ไม่สามารถเปลี่ยนสถานะสินค้าที่ปิดสต็อกแล้ว'
            })
        
        product.stock_status = new_status
        product.save(update_fields=['stock_status'])
        
        return JsonResponse({
            'success': True,
            'is_superuser': request.user.is_superuser,
            'new_status': new_status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    
@login_required
@require_POST
@permission_required('pos_133.change_product', raise_exception=True)
def product_confirm(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        if product.stock_status == 'open_stock':
            # เปลี่ยนสถานะเป็นปิดสต็อก
            product.stock_status = 'close_stock'
            product.save(update_fields=['stock_status'])
            messages.success(request, 'ยืนยันและปิดสต็อกสินค้าสำเร็จ')
        else:
            messages.error(request, 'สินค้านี้ถูกปิดสต็อกไปแล้ว')
        
        return redirect('product_list')
        
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
        return redirect('product_list')
    


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm
from django.db.models import ProtectedError
from django.db import IntegrityError

from .models import Customer

@login_required
@permission_required('pos_133.view_customer', raise_exception=True)
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer/customer_list.html', {'customers': customers})

@login_required
@permission_required('pos_133.add_customer', raise_exception=True)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'สร้างลูกค้าเรียบร้อยแล้ว')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer/customer_form.html', {'form': form, 'title': 'Create Customer'})

@login_required
@permission_required('pos_133.change_customer', raise_exception=True)
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขลูกค้าเรียบร้อยแล้ว')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer/customer_form.html', {'form': form, 'title': 'Edit Customer'})



@login_required
@permission_required('pos_133.delete_customer', raise_exception=True)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        try:
            customer.delete()
            messages.success(request, "ลบข้อมูลลูกค้าเรียบร้อยแล้ว")
            return redirect('customer_list')
        except IntegrityError:
            messages.error(request, "ไม่สามารถลบลูกค้าได้ เนื่องจากมีข้อมูลที่เกี่ยวข้องอยู่")
            return redirect('customer_list')
    return render(request, 'customer/customer_confirm_delete.html', {'customer': customer})







from django.http import HttpResponse
from .utils import generate_product_pdf
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
@permission_required('pos_133.view_product', raise_exception=True)
def export_selected_products_pdf(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_products')
        products = Product.objects.filter(pk__in=selected_ids)
        
        if products:
            buffer = generate_product_pdf(products)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="selected_products_qr_codes.pdf"'
            response.write(buffer.getvalue())
            return response
    
    messages.warning(request, 'กรุณาเลือกสินค้าที่ต้องการ ส่งออก')
    return redirect('product_list')







from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Costprice
from .forms import CostPriceForm

@login_required
@permission_required('pos_133.view_costprice', raise_exception=True)
def cost_price_list(request):
    costs = Costprice.objects.all().order_by('-date')
    return render(request, 'cost_price/cost_price_list.html', {'costs': costs})

@login_required
@permission_required('pos_133.add_costprice', raise_exception=True)
def cost_price_create(request):
    if request.method == 'POST':
        form = CostPriceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มราคาต้นทุนสำเร็จ')
            return redirect('cost_price_list')
    else:
        form = CostPriceForm()
    return render(request, 'cost_price/cost_price_form.html', {
        'form': form, 
        'title': 'เพิ่มราคาต้นทุน'
    })

@login_required
@permission_required('pos_133.change_costprice', raise_exception=True)
def cost_price_edit(request, pk):
    cost = get_object_or_404(Costprice, pk=pk)
    if request.method == 'POST':
        form = CostPriceForm(request.POST, instance=cost)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขราคาต้นทุนสำเร็จ')
            return redirect('cost_price_list')
    else:
        form = CostPriceForm(instance=cost)
    return render(request, 'cost_price/cost_price_form.html', {
        'form': form, 
        'title': 'แก้ไขราคาต้นทุน'
    })

@login_required
@permission_required('pos_133.delete_costprice', raise_exception=True)
def cost_price_delete(request, pk):
    cost = get_object_or_404(Costprice, pk=pk)
    if request.method == 'POST':
        cost.delete()
        messages.success(request, 'ลบราคาต้นทุนสำเร็จ')
        return redirect('cost_price_list')
    return render(request, 'cost_price/cost_price_confirm_delete.html', {'cost': cost})




@login_required

@permission_required('pos_133.view_marketprice', raise_exception=True)
def market_price_list(request):
    market_prices = MarketPrice.objects.all().order_by('id')
    return render(request, 'market_price/market_price_list.html', {
        'market_prices': market_prices
    })

@login_required
@permission_required('pos_133.add_marketprice', raise_exception=True)
def market_price_create(request):
    if request.method == 'POST':
        form = MarketPriceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มราคาตลาดสำเร็จ')
            return redirect('market_price_list')
    else:
        form = MarketPriceForm()
    return render(request, 'market_price/market_price_form.html', {
        'form': form,
        'title': 'เพิ่มราคาตลาด'
    })

@login_required
@permission_required('pos_133.change_marketprice', raise_exception=True)
def market_price_edit(request, pk):
    market_price = get_object_or_404(MarketPrice, pk=pk)
    if request.method == 'POST':
        form = MarketPriceForm(request.POST, instance=market_price)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขราคาตลาดสำเร็จ')
            return redirect('market_price_list')
    else:
        form = MarketPriceForm(instance=market_price)
    return render(request, 'market_price/market_price_form.html', {
        'form': form,
        'title': 'แก้ไขราคาตลาด'
    })

@login_required
@permission_required('pos_133.delete_marketprice', raise_exception=True)
def market_price_delete(request, pk):
    market_price = get_object_or_404(MarketPrice, pk=pk)
    if request.method == 'POST':
        market_price.delete()
        messages.success(request, 'ลบราคาตลาดสำเร็จ')
        return redirect('market_price_list')
    return render(request, 'market_price/market_price_confirm_delete.html', {
        'market_price': market_price
    })





@login_required
@permission_required('pos_133.view_sale', raise_exception=True)
def sale_list(request):
    sales = Sale.objects.all().order_by('-sale_date')
    paginator = Paginator(sales, 6)  # แบ่งหน้าให้แสดง 7 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'sale/sale_list.html', {'sales': sales, 'page_obj': page_obj})

@login_required 
@permission_required('pos_133.add_sale', raise_exception=True)
def sale_create(request):
    
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            try:
                sale = form.save(commit=False)
                product = Product.objects.get(pk=sale.productid.pk)
                  # ดึงข้อมูลใหม่จาก DB
                
                # Debug logs
                print("=== Debug การคำนวณสต็อก ===")
                print(f"รหัสสินค้า: {product.productid}")
                print(f"สต็อกเดิม: {product.quantity_in_stock}")
                print(f"จำนวนที่ขาย: {sale.sale_quantity}")

                if product.stock_status != 'close_stock':
                    messages.error(request, 'สามารถขายได้เฉพาะสินค้าที่ปิดสต็อกแล้วเท่านั้น')
                    return redirect('sale_list')
                
                # ตรวจสอบสต็อกก่อนการขาย
                if sale.sale_quantity <= product.quantity_in_stock:
                    # คำนวณสต็อกใหม่
                    current_stock = product.quantity_in_stock
                    sale_amount = sale.sale_quantity
                    new_stock = current_stock - sale_amount
                    
                    print(f"การคำนวณ: {current_stock} - {sale_amount} = {new_stock}")
                    
                    # Get latest market price
                    latest_price = MarketPrice.objects.filter(
                        pname=product.pname
                    ).latest('date')
                    sale.sale_price = latest_price
                    
                    # อัพเดทสต็อก
                    product.quantity_in_stock = new_stock
                    product.save(update_fields=['quantity_in_stock'])
                    
                    print(f"สต็อกหลังอัพเดท: {product.quantity_in_stock}")
                    
                    # บันทึกการขาย
                    sale.save()
                    
                    messages.success(request, f'บันทึกการขายสำเร็จ (สต็อกเหลือ: {new_stock})')
                    return redirect('sale_list')
                else:
                    messages.error(request, f'สินค้าในสต็อกมีไม่เพียงพอ (เหลือ {product.quantity_in_stock} ชิ้น)')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
                print(f"Error: {str(e)}")
    else:
        form = SaleForm()
        # ดึงเฉพาะสินค้าที่ปิดสต็อกและมี stock > 0
        products = Product.objects.filter(
            quantity_in_stock__gt=0,
            stock_status='close_stock'
        ).select_related('pname').order_by('pname')
        
        print("Debug - จำนวนสินค้าที่พร้อมขาย:", products.count())  # เพิ่ม debug log
        for p in products:
            print(f"- {p.pname}: {p.quantity_in_stock} ชิ้น (status: {p.stock_status})")

    return render(request, 'sale/sale_form.html', {
        'form': form,
        'products': products,
        'title': 'สร้างรายการขาย'
    })
    

@login_required
@permission_required('pos_133.change_sale', raise_exception=True)
def sale_edit(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    old_quantity = sale.sale_quantity

    if sale.payment_status == 'paid' and not request.user.is_superuser:
        messages.error(request, 'ไม่สามารถแก้ไขรายการที่ชำระเงินแล้ว')
        return redirect('sale_list')
    
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            try:
                new_sale = form.save(commit=False)
                product = new_sale.productid
                
                # คำนวณความต่างของจำนวนสินค้า
                quantity_difference = new_sale.sale_quantity - old_quantity
                
                # คำนวณจำนวนสินค้าคงเหลือหลังการแก้ไข
                new_stock = product.quantity_in_stock - quantity_difference
                
                # ตรวจสอบว่าสต็อกไม่ติดลบ
                if new_stock < 0:
                    raise ValueError(f'สินค้าในสต็อกไม่เพียงพอ (เหลือ {product.quantity_in_stock} ชิ้น)')
                
                # บันทึกการขายก่อน
                new_sale.save()
                
                # อัพเดทสต็อกหลังจากบันทึกการขายสำเร็จ
                product.quantity_in_stock = new_stock
                product.save()
                
                messages.success(request, 'แก้ไขการขายสำเร็จ')
                return redirect('sale_list')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sale/sale_form.html', {
        'form': form,
        'title': 'แก้ไขการขาย'
    })

@login_required
@permission_required('pos_133.delete_sale', raise_exception=True)
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    
    # Check if sale is paid and user is not superuser
    if sale.payment_status == 'paid' and not request.user.is_superuser:
        messages.error(request, 'ไม่สามารถลบรายการที่ชำระเงินแล้ว')
        return redirect('sale_list')
        
    if request.method == 'POST':
        # คืนสินค้ากลับเข้าสต็อก
        product = sale.productid
        product.quantity_in_stock += sale.sale_quantity
        product.save()
        
        sale.delete()
        messages.success(request, 'ลบรายการขายสำเร็จ')
        return redirect('sale_list')
    return render(request, 'sale/sale_confirm_delete.html', {'sale': sale})



from django.views.decorators.http import require_POST

@login_required
@require_POST
@permission_required('pos_133.change_sale', raise_exception=True)
def toggle_payment_status(request, pk):
    try:
        sale = get_object_or_404(Sale, pk=pk)
        
        # เพิ่มการตรวจสอบสิทธิ์
        if sale.payment_status == 'paid' and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'ไม่มีสิทธิ์เปลี่ยนสถานะรายการที่ชำระเงินแล้ว'
            }, status=403)
        
        # Toggle payment status
        if sale.payment_status == 'pending':
            sale.payment_status = 'paid'
        elif sale.payment_status == 'paid' and request.user.is_superuser:
            sale.payment_status = 'pending'
        
        sale.save()
        
        return JsonResponse({
            'success': True,
            'new_status': sale.payment_status,
            'is_superuser': request.user.is_superuser
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    


# ใน views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@require_http_methods(["POST"])
@login_required
@permission_required('pos_133.change_product', raise_exception=True)
def update_product_status(request, product_id):
    try:
        data = json.loads(request.body)
        product = Product.objects.get(pk=product_id)
        current_status = data.get('current_status')
        new_status = data.get('status')

        # ถ้าไม่ใช่ superuser และพยายามเปลี่ยนจากปิดเป็นเปิด
        if not request.user.is_superuser and current_status == 'close_stock':
            return JsonResponse({
                'success': False,
                'error': 'ไม่สามารถเปลี่ยนสถานะได้เนื่องจากสต๊อกถูกปิดแล้ว'
            })

        product.stock_status = new_status
        product.save()
        
        return JsonResponse({
            'success': True,
            'is_superuser': request.user.is_superuser
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    

from django.shortcuts import render, get_object_or_404
from .models import Sale

def sale_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    context = {
        'sale': sale,
        'company_name': 'POS Maliwong133',
        'company_address': 'ที่อยู่ร้าน...',
        'company_phone': 'เบอร์โทร...',
    }
    return render(request, 'sale/invoice.html', context)
#==================================================================
from django.shortcuts import render

def create_invoice_html(request, sales):
    # สร้างข้อมูลที่ต้องการส่งไปยังเทมเพลต
    total_revenue = sum(sale.revenue for sale in sales)
    context = {
        'sales': sales,
        'total_revenue': total_revenue,
        'company_name': 'POS Maliwong133',
        'company_address': 'ที่อยู่ร้าน...',
        'company_phone': 'เบอร์โทร...',
    }
    # เรนเดอร์ HTML
    return render(request, 'sale/invoice.html', context)



def generate_invoice(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        sale_ids = data.get('sales', [])
        
        if not sale_ids:
            return JsonResponse({'success': False, 'error': 'ไม่มีรายการขายที่เลือก'})

        # ดึงข้อมูลรายการขายที่เลือก
        sales = Sale.objects.filter(pk__in=sale_ids)

        # เรนเดอร์ HTML สำหรับใบแจ้งหนี้
        return create_invoice_html(request, sales)
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

from collections import defaultdict
from django.shortcuts import render
from .models import Sale

def invoice_view(request):
    sales_ids = request.GET.get('sales', '').split(',')
    sales = Sale.objects.filter(pk__in=sales_ids)

    # จัดกลุ่มข้อมูลตามลูกค้า
    grouped_sales = defaultdict(list)
    for sale in sales:
        grouped_sales[sale.customerid.first_name].append(sale)

    # สร้างข้อมูลสำหรับเทมเพลต
    invoices = []
    for customer_name, customer_sales in grouped_sales.items():
        total_revenue = sum(sale.revenue for sale in customer_sales)
        invoices.append({
            'customer_name': customer_name,
            'sales': customer_sales,
            'total_revenue': total_revenue,
        })

    context = {
        'invoices': invoices,
        'company_name': 'POS Maliwong133',
        'company_address': 'ที่อยู่ร้าน...',
        'company_phone': 'เบอร์โทร...',
    }
    return render(request, 'sale/invoice.html', context)
    

#===================================================================
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import timedelta
import json
from .models import Sale, Product, Customer, Expense
from django.db.models import ExpressionWrapper

@login_required
def dashboard(request):
    today = timezone.now().date()

    # ข้อมูลลูกค้าและสต็อก
    customer_count = Customer.objects.count()
    stock_summary = Product.objects.filter(
        quantity_in_stock__gt=0
    ).values(
        'productid',
        'pname__pname',
        'warehouse_w__warehouse_w',
        'quantity_in_stock',
    ).annotate(
        total_stock=Sum('quantity_in_stock')
    ).order_by('productid')
    
    # สรุปข้อมูลวันนี้
    daily_summary = Sale.objects.filter(
        sale_date__date=today
    ).aggregate(
        total_revenue=Cast(
            Sum('revenue'), 
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        total_quantity=Sum('sale_quantity'),
        total_cost=Sum(
            ExpressionWrapper(
                F('sale_quantity') * F('sale_price__market_price') * 0.7,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    )

    # คำนวณกำไรวันนี้
    revenue = daily_summary['total_revenue'] or 0
    cost = daily_summary['total_cost'] or 0
    profit = revenue - cost
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0

    # ข้อมูลรายเดือน 3 เดือนล่าสุด
    months = []
    monthly_data = []
    for i in range(3):
        date = today - timedelta(days=30*i)
        month_name = date.strftime('%B %Y')
        year = date.year
        month = date.month

        # ยอดขายและต้นทุน
        monthly_stats = Sale.objects.filter(
            sale_date__year=year,
            sale_date__month=month
        ).aggregate(
            revenue=Cast(
                Sum('revenue'), 
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            cost=Sum(
                ExpressionWrapper(
                    F('sale_quantity') * F('sale_price__market_price') * 0.7,
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ),
            quantity=Sum('sale_quantity')
        )
        month_revenue = monthly_stats['revenue'] or 0
        month_cost = monthly_stats['cost'] or 0

        # ค่าใช้จ่าย
        month_expense = Expense.objects.filter(
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # กำไร = ยอดขาย - (ต้นทุน + ค่าใช้จ่าย)
        month_profit = month_revenue - (month_cost + month_expense)
        margin = (month_profit / month_revenue * 100) if month_revenue > 0 else 0

        monthly_data.append({
            'month': month_name,
            'revenue': month_revenue,
            'cost': month_cost,
            'expense': month_expense,
            'profit': month_profit,
            'margin': margin
        })
        months.append(month_name)

    # เรียงข้อมูลจากเก่าไปใหม่
    months.reverse()
    monthly_data.reverse()

    context = {
        'today_summary': {
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'margin': profit_margin,
            'quantity': daily_summary['total_quantity'] or 0
        },
        'monthly_data': monthly_data,
        'months': json.dumps(months),
        'monthly_sales': [d['revenue'] for d in monthly_data],
        'monthly_costs': [d['cost'] for d in monthly_data],
        'monthly_expenses': [d['expense'] for d in monthly_data],
        'monthly_profits': [d['profit'] for d in monthly_data],
        'customer_count': customer_count,
        'stock_summary': stock_summary
    }

    return render(request, 'dashboard.html', context)


#===================================================================


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quatation
from .forms import QuatationForm

@login_required
@permission_required('pos_133.view_quatation', raise_exception=True)
def quatation_list(request):
    quatations = Quatation.objects.all().order_by('-date')
    return render(request, 'quatation/quatation_list.html', {'quatations': quatations})

@login_required
@permission_required('pos_133.add_quatation', raise_exception=True)
def quatation_create(request):
    if request.method == 'POST':
        form = QuatationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มใบเสนอราคาสำเร็จ')
            return redirect('quatation_list')
    else:
        form = QuatationForm()
    return render(request, 'quatation/quatation_form.html', {'form': form, 'title': 'เพิ่มใบเสนอราคา'})

@login_required
@permission_required('pos_133.change_quatation', raise_exception=True)
def quatation_edit(request, pk):
    quatation = get_object_or_404(Quatation, pk=pk)
    if request.method == 'POST':
        form = QuatationForm(request.POST, instance=quatation)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขใบเสนอราคาสำเร็จ')
            return redirect('quatation_list')
    else:
        form = QuatationForm(instance=quatation)
    return render(request, 'quatation/quatation_form.html', {'form': form, 'title': 'แก้ไขใบเสนอราคา'})

@login_required
@permission_required('pos_133.delete_quatation', raise_exception=True)
def quatation_delete(request, pk):
    quatation = get_object_or_404(Quatation, pk=pk)
    if request.method == 'POST':
        quatation.delete()
        messages.success(request, 'ลบใบเสนอราคาสำเร็จ')
        return redirect('quatation_list')
    return render(request, 'quatation/quatation_confirm_delete.html', {'quatation': quatation})





from django.shortcuts import render, get_object_or_404
from .models import Quatation

@login_required
@permission_required('pos_133.view_quatation', raise_exception=True)
def quatation_invoice(request, pk):
    quatation = get_object_or_404(Quatation, pk=pk)
    serial_number = pk  # หรือกำหนดค่าตามที่คุณต้องการ
    context = {
        'quatation': quatation,
        'serial_number': serial_number,
        'company_name': 'POS Maliwong133',
        'company_address': 'ที่อยู่ร้าน...',
        'company_phone': 'เบอร์โทร...',
    }
    return render(request, 'quatation/invoice.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Quatation

@login_required
def quatation_summary(request):
    ids = request.GET.get('ids')
    if not ids:
        return render(request, 'quatation/quatation_list.html', {
            'error_message': 'กรุณาเลือกใบเสนอราคาก่อนดำเนินการ',
            'quatations': Quatation.objects.all().order_by('-date')
        })
    
    ids_list = ids.split(',')
    quatations = Quatation.objects.filter(pk__in=ids_list)
    
    summary = []
    for quatation in quatations:
        customer_summary = next((item for item in summary if item['customer'] == quatation.customerid), None)
        if not customer_summary:
            customer_summary = {
                'customer': quatation.customerid,
                'date': quatation.date,
                'products': {},
                'total_price': 0,
            }
            summary.append(customer_summary)
        
        product = quatation.productid
        if product not in customer_summary['products']:
            customer_summary['products'][product] = {
                'quantity': 0,
                'unit_price': quatation.sale_price,
                'total_price': 0,
            }
        customer_summary['products'][product]['quantity'] += quatation.sale_quantity
        customer_summary['products'][product]['total_price'] += quatation.total_price
        customer_summary['total_price'] += quatation.total_price
    
    return render(request, 'quatation/summary.html', {
        'summary': summary
    })


#===========================================================================================
from django.shortcuts import render, get_object_or_404, redirect
from .models import Expense
from .forms import ExpenseForm

@login_required
@permission_required('pos_133view_expense', raise_exception=True)
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'expense/expense_list.html', {'expenses': expenses})
@login_required
@permission_required('pos_133.add_expense', raise_exception=True)
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expense/expense_form.html', {'form': form})
@login_required
@permission_required('pos_133.change_expense', raise_exception=True)
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expense/expense_form.html', {'form': form})
@login_required
@permission_required('pos_133.delete_expense', raise_exception=True)
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete() 
        return redirect('expense_list')
    return render(request, 'expense/expense_confirm_delete.html', {'expense': expense})