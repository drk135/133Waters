from django import forms
from .models import Product

from django import forms
from .models import Product, Warehouse, Customer, Sale, Costprice, MarketPrice
from django.utils import timezone

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['pname',   'quantity_in_stock', 'warehouse_w']
        # Remove productid from fields as it will be auto-generated
        widgets = {
            'pname': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
                    
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),           
            'warehouse_w': forms.Select(attrs={'class': 'form-control'}),
        }
   

from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'phone_number']  # ไม่รวม customerid
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

        
from django import forms
from django.core.exceptions import ValidationError
from .models import Sale



class CostPriceForm(forms.ModelForm):
    class Meta:
        model = Costprice
        fields = ['pname', 'cost_price', 'product_type']
        labels = {
            'pname': 'ชื่อสินค้า',
            'cost_price': 'ราคาต้นทุน',  # เพิ่มลูกน้ำ
            'product_type': 'ประเภทสินค้า'  # เพิ่มลูกน้ำ
        }
        widgets = {
            'pname': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'ระบุชื่อสินค้า'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'ระบุราคาต้นทุน'
            }),
            'product_type': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'ระบุประเภทสินค้า'
            })
        }
        error_messages = {
            'pname': {
                'required': 'กรุณาระบุชื่อสินค้า'
            },
            'cost_price': {
                'required': 'กรุณาระบุราคาต้นทุน',
                'min_value': 'ราคาต้นทุนต้องมากกว่า 0'
            },  # เพิ่มลูกน้ำ
            'product_type': {
                'required': 'กรุณาระบุประเภทสินค้า'
            }
        }  # ปิด error_messages ให้ถูกต้อง




class MarketPriceForm(forms.ModelForm):
    class Meta:
        model = MarketPrice
        fields = ['pname', 'market_price']
        labels = {
            'pname': 'ชื่อสินค้า',
            'market_price': 'ราคาตลาด (บาท)'
        }
        widgets = {
            'pname': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'market_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'ระบุราคาตลาด'
            })
        }



class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter products to show only those with closed stock status
        self.fields['productid'].queryset = Product.objects.filter(stock_status='close_stock')
        self.fields['productid'].empty_label = "-- เลือกสินค้า --"
    class Meta:
        model = Sale
        fields = ['productid', 'customerid', 'sale_quantity', 'payment_status']
        labels = {
            'productid': 'สินค้า',
            'customerid': 'ลูกค้า',
            'sale_quantity': 'จำนวน',
            'payment_status': 'สถานะการชำระเงิน'
        }
        widgets = {
            'productid': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'customerid': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'sale_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True
            }),
            'payment_status': forms.Select(attrs={
                'class': 'form-select'
            })
        }




from django import forms
from .models import Quatation

class QuatationForm(forms.ModelForm):
    class Meta:
        model = Quatation
        fields = ['customerid', 'productid', 'sale_quantity']
        labels = {
            'customerid': 'ลูกค้า',
            'productid': 'สินค้า',
            'sale_quantity': 'จำนวน',
            'sale_price': 'ราคาขาย'
        }
        widgets = {
            'customerid': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'productid': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'sale_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True
            })
           
        }



#================================================================================
from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'invoices']
        widgets = {  # แก้จาก wigets เป็น widgets
            'expense_type': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'ระบุประเภทค่าใช้จ่าย'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'ระบุจำนวนเงิน'
            }),
            'invoices': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'expense_type': 'ประเภทค่าใช้จ่าย',
            'amount': 'จำนวนเงิน',
            'invoices': 'ไฟล์ใบแจ้งหนี้'
        }