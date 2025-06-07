import math
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ตรวจสอบและลงทะเบียนฟอนต์
def initialize_fonts():
    FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts')
    font_files = {
        'THSarabun': 'THSarabun.ttf',
        'THSarabunBold': 'THSarabun-Bold.ttf'
    }
    
    for font_name, font_file in font_files.items():
        font_path = os.path.join(FONT_PATH, font_file)
        if not os.path.exists(font_path):
            raise Exception(
                f"ไม่พบไฟล์ฟอนต์ {font_file}\n"
                f"กรุณาดาวน์โหลดและวางไว้ใน: {FONT_PATH}"
            )
        pdfmetrics.registerFont(TTFont(font_name, font_path))

# เรียกใช้ฟังก์ชันตรวจสอบฟอนต์
initialize_fonts()

def get_thai_style():
    """สร้างและคืนค่าสไตล์สำหรับภาษาไทย"""
    styles = getSampleStyleSheet()
    
    # สร้างสไตล์สำหรับหัวข้อภาษาไทย
    styles.add(ParagraphStyle(
        name='ThaiTitle',
        fontName='THSarabunBold',
        fontSize=16,
        leading=20,
        alignment=1,
        spaceAfter=20,
    ))
    
    # สร้างสไตล์สำหรับเนื้อหาภาษาไทย
    styles.add(ParagraphStyle(
        name='Thai',
        fontName='THSarabun',
        fontSize=14,
        leading=16,
    ))
    
    # สร้างสไตล์สำหรับป้ายกำกับ QR Code
    styles.add(ParagraphStyle(
        name='ThaiLabel',
        fontName='THSarabun',
        fontSize=8,
        leading=10,
        alignment=1,
    ))
    
    return styles

def generate_qr_code(data):
    """สร้าง QR Code จากข้อมูล"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def generate_product_pdf(products):
    """สร้าง PDF ที่มี QR Code ของสินค้าตามจำนวนในสต็อก"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = get_thai_style()
    
    # กำหนดขนาดและระยะห่าง
    qr_size = 2.5 * cm  # ขนาด 2x2 cm
    horizontal_spacing = 0.5 * cm  # ระยะห่างแนวนอน
    vertical_spacing = 0.5 * cm    # ระยะห่างแนวตั้ง
    margin = 0.05 * cm  # ระยะขอบกระดาษ
    
    # คำนวณจำนวน QR Code ต่อแถว
    usable_width = A4[0] - (0.05 * margin)
    qr_per_row = math.floor(usable_width / (qr_size + horizontal_spacing))
    
    # เพิ่มหัวข้อ
    elements.append(Paragraph("รายการ QR Code สินค้า", styles['ThaiTitle']))
    elements.append(Spacer(1, 0.5*cm))
    
    # สร้างลิสต์ของ QR codes ทั้งหมดตามจำนวนสินค้า
    all_qr_codes = []
    for product in products:
        # สร้าง QR Code ตามจำนวนสินค้าในสต็อก
        for _ in range(product.quantity_in_stock):
            qr_data = f"""
รหัส: {product.productid}
สินค้า: {product.pname}
คลัง: {product.warehouse_w}
"""
            # สร้าง QR Code
            qr_image = generate_qr_code(qr_data)
            img = Image(BytesIO(qr_image))
            img.drawHeight = qr_size
            img.drawWidth = qr_size
            
            # สร้างป้ายกำกับ
            label = Paragraph(
                f"{product.productid}<br/>{product.pname}", 
                styles['ThaiLabel']
            )
            
            all_qr_codes.append((img, label))
    
    # จัดเรียง QR codes เป็นตาราง
    for i in range(0, len(all_qr_codes), qr_per_row):
        batch = all_qr_codes[i:i + qr_per_row]
        table_data = []
        qr_codes_row = []
        labels_row = []
        
        for img, label in batch:
            qr_codes_row.append(img)
            labels_row.append(label)
        
        # เพิ่มแถว QR Codes และป้ายกำกับ
        if qr_codes_row:
            table_data.append(qr_codes_row)
            table_data.append(labels_row)
            
            # สร้างตารางสำหรับแถวปัจจุบัน
            col_widths = [qr_size] * len(qr_codes_row)
            table = Table(table_data, colWidths=col_widths)
            
            # จัดสไตล์ตาราง
            table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), horizontal_spacing/2),
                ('RIGHTPADDING', (0,0), (-1,-1), horizontal_spacing/2),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, vertical_spacing))
    
    # เพิ่มสรุปจำนวน QR Code ที่สร้าง
    summary = Paragraph(
        f"จำนวน QR Code ทั้งหมด: {len(all_qr_codes)} รายการ",
        styles['Thai']
    )
    elements.append(summary)
    
    # สร้าง PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer