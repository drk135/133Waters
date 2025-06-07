from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError




    
class Costprice(models.Model):
    id = models.AutoField(primary_key=True)  # รหัสต้นทุน
    pname = models.CharField(max_length=20,unique=True)  # ชื่อสินค้า
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)  # ต้นทุนสินค้า
    product_type = models.CharField(max_length=25)  # ประเภทสินค้า
    date = models.DateTimeField(auto_now_add=True)  # วันที่บันทึกต้นทุน

    class Meta:
        [           
            ("can_add_costprice", "Can add cost price"),
            ("can_view_costprice", "Can view cost price"),
            ("can_edit_costprice", "Can edit cost price"),
            ("can_delete_costprice", "Can delete cost price"),
        ]

    def __str__(self):
        return f"{self.pname}"

    


class Warehouse(models.Model):
    id = models.AutoField(primary_key=True)  # รหัสคลังสินค้า
    warehouse_w = models.CharField(max_length=255, unique=True)  # ชื่อคลังสินค้า
    location = models.TextField()  # ที่ตั้งคลังสินค้า
    class Meta:
        [
            ("can_add_warehouse", "Can add warehouse"),
            ("can_view_warehouse", "Can view warehouse"),
            ("can_edit_warehouse", "Can edit warehouse"),
            ("can_delete_warehouse", "Can delete warehouse"),
        ]
    def __str__(self):
        return self.warehouse_w

class Product(models.Model):
    STOCK_STATUS_CHOICES = [
        ('open stock', 'เปิดสต็อก'),
        ('close stock', 'ปิดสต็อก'),
    ]
    id = models.AutoField(primary_key=True)  # รหัสสินค้า
    productid = models.CharField(max_length=255)  # รหัสสินค้า
    pname = models.ForeignKey(
        Costprice, 
        on_delete=models.CASCADE,
        related_name='products_by_name'  # เพิ่ม related_name
    )  # ชื่อสินค้า
    
    quantity_in_stock = models.PositiveIntegerField()  # จำนวนเก็บสินค้า    
    warehouse_w = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # ที่ผลิต
    qr_code = models.CharField(max_length=255, null=True, blank=True)  # QR Code field
    stock_status = models.CharField(max_length=50,
        choices=STOCK_STATUS_CHOICES,
        default='open stock'  # สถานะสินค้า
    )
    manufacture_date = models.DateField(auto_now_add=True)  # วันที่ผลิต
    def can_edit_delete(self, user):
        """Check if product can be edited or deleted"""
        return self.stock_status == 'open_stock' or user.is_superuser
    # ...existing save and __str__ methods...
    class Meta:
        [
            ("can_add_product", "Can add product"),
            ("can_view_product", "Can view product"),
            ("can_edit_product", "Can edit product"),
            ("can_delete_product", "Can delete product"),
        ]
    def __str__(self):
        return f"{self.productid} - {self.pname}"
    
    def save(self, *args, **kwargs):
        if not self.productid:
            # Generate product ID if not set (new product)
            date_str = datetime.now().strftime('%d%m%y')
            
            # หาเลขล่าสุดจากทั้งหมด ไม่จำกัดวัน
            last_product = Product.objects.order_by('-productid').first()
            
            if last_product and '-' in last_product.productid:
                try:
                    last_number = int(last_product.productid.split('-')[-1])
                    next_number = last_number + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1
                
            # Format: DDMMYY-XXXX where XXXX is continuous number
            self.productid = f"{date_str}-{str(next_number).zfill(4)}"
        
        super().save(*args, **kwargs)

    def check_stock(self, quantity):
        """ตรวจสอบจำนวนสินค้าในสต็อก"""
        return self.quantity_in_stock >= quantity

    def update_stock(self, quantity):
        """อัพเดทจำนวนสินค้าในสต็อก"""
        self.quantity_in_stock -= quantity
        self.save(update_fields=['quantity_in_stock'])

    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def confirm(self, user):
        if not self.is_confirmed:
            self.is_confirmed = True
            self.confirmed_at = timezone.now()
            self.save()




class MarketPrice(models.Model):    
    id = models.AutoField(primary_key=True)  # รหัสราคา
    pname = models.ForeignKey(Costprice, on_delete=models.CASCADE)  # ชื่อสินค้า
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        [
            ("can_add_marketprice", "Can add market price"),
            ("can_view_marketprice", "Can view market price"),
            ("can_edit_marketprice", "Can edit market price"),
            ("can_delete_marketprice", "Can delete market price"),
        ]
    def __str__(self):
        return f"{self.pname}"

 

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    customerid = models.CharField(max_length=255, unique=True)  # รหัสลูกค้า
    first_name = models.CharField(max_length=255)  # ชื่อ
    last_name = models.CharField(max_length=255)  # นามสกุล
    address = models.TextField()  # ที่อยู่
    phone_number = models.CharField(max_length=20)  # เบอร์โทร
    class Meta:
        [
            ("can_add_customer", "Can add customer"),
            ("can_view_customer", "Can view customer"),
            ("can_edit_customer", "Can edit customer"),
            ("can_delete_customer", "Can delete customer"),
        ]
    def save(self, *args, **kwargs):
        if not self.customerid:
            # สร้างรหัสลูกค้าอัตโนมัติ
            prefix = "133"  # รหัสนำหน้า
            date_str = datetime.now().strftime('%m%y')  # เดือนและปี (MMYY)
            
            # ค้นหาลูกค้าที่มีรหัสขึ้นต้นด้วยเดือนและปีเดียวกัน
            today_customers = Customer.objects.filter(
                customerid__startswith=f"{prefix}-{date_str}"
            ).count()
            
            # สร้างรหัสในรูปแบบ 133-MMYY-XXXX
            self.customerid = f"{prefix}-{date_str}-{str(today_customers + 1).zfill(4)}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customerid} - {self.first_name} {self.last_name}"
    

from django.utils import timezone

class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'รอชำระเงิน'),
        ('paid', 'ชำระแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]
    
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)
    customerid = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sale_code = models.CharField(max_length=20, unique=True, blank=True)
    sale_quantity = models.PositiveIntegerField()
    sale_price = models.ForeignKey(
        MarketPrice, 
        on_delete=models.CASCADE, 
        related_name='market_price_by_product'
    )
    revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    def save(self, *args, **kwargs):
        if not self.sale_code:
            date_str = timezone.now().strftime('%m%d')
            today_sales = Sale.objects.filter(
                sale_code__startswith=f"133-{date_str}"
            ).count()
            self.sale_code = f"133-{date_str}-{str(today_sales + 1).zfill(4)}"

        # Calculate revenue
        self.revenue = self.sale_quantity * self.sale_price.market_price
        
        is_new_sale = self.pk is None
        
        if is_new_sale:
            # ตรวจสอบสต็อกก่อนบันทึก
            if self.productid.check_stock(self.sale_quantity):
                # บันทึกการขายและอัพเดทสต็อก
                super().save(*args, **kwargs)
                self.productid.update_stock(self.sale_quantity)
            else:
                # ถ้าสินค้าไม่พอ ให้แจ้งเตือนแบบ ValidationError
                raise ValidationError({
                    'sale_quantity': f'สินค้าในสต็อกมีไม่พอ มีสินค้าเหลือ {self.productid.quantity_in_stock} ชิ้น'
                })
        else:
            # กรณีแก้ไขการขาย ไม่ต้องตรวจสอบสต็อก
            super().save(*args, **kwargs)


class Quatation(models.Model):
    id = models.AutoField(primary_key=True)  # รหัสใบเสนอราคา
    customerid = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)  # รหัสลูกค้า
    productid = models.ForeignKey(MarketPrice, on_delete=models.DO_NOTHING)  # รหัสสินค้า   
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # ราคาที่เสนอราคา
    sale_quantity = models.PositiveIntegerField()  # จำนวนที่เสนอราคา
    date = models.DateTimeField(auto_now_add=True)  # วันที่เสนอราคา
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # ราคาทั้งหมด
    class Meta:
        [
            ("can_add_quatation", "Can add quotation"),
            ("can_view_quatation", "Can view quotation"),
            ("can_edit_quatation", "Can edit quotation"),
            ("can_delete_quatation", "Can delete quotation"),
        ]
    def save(self, *args, **kwargs):
        # ดึงราคาจาก MarketPrice อัตโนมัติ
        if self.productid and not self.sale_price:
            self.sale_price = self.productid.market_price

        # คำนวณราคาทั้งหมด (จำนวน * ราคาต่อหน่วย)
        self.total_price = self.sale_quantity * self.sale_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customerid} - {self.productid} - {self.sale_quantity}" 
    



#================================================================================================
class Expense(models.Model):
    id = models.AutoField(primary_key=True)  # รหัสค่าใช้จ่าย
    expense_type = models.CharField(max_length=255)  # ประเภทค่าใช้จ่าย
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # จำนวนเงิน
    date = models.DateTimeField(auto_now_add=True)  # วันที่บันทึกค่าใช้จ่าย
    invoices = models.FileField(upload_to='invoices/', null=True, blank=True)  # ไฟล์ใบแจ้งหนี้
    class Meta:
        [
            ("can_add_expense", "Can add expense"),
            ("can_view_expense", "Can view expense"),
            ("can_edit_expense", "Can edit expense"),
            ("can_delete_expense", "Can delete expense"),
        ]
    def __str__(self):
        return f"{self.expense_type} - {self.amount}"