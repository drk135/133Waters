from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee, EmployeeAttachment
from .forms import EmployeeForm
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime
from datetime import datetime
from calendar import monthrange
from django.http import JsonResponse
import csv
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import permission_required
@login_required
def dashboard_view(request):
    # Get current month's first day
    today = timezone.now()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    context = {
        'total_employees': Employee.objects.count(),
        'total_documents': EmployeeAttachment.objects.count(),
        'new_employees': Employee.objects.filter(hire_date__gte=month_start).count(),
        'recent_employees': Employee.objects.order_by('-hire_date')[:5],
    }
    return render(request, 'ems/dashboard.html', context)

# Employee Views
@login_required
@permission_required('ems.view_employee', raise_exception=True) 
def emp_list_view(request):
    employees = Employee.objects.all().order_by('employee_id')
    return render(request, 'ems/emp_list.html', {
        'employees': employees,
        'document_types': EmployeeAttachment.DOCUMENT_TYPES
    })
@login_required
@permission_required('ems.add_employee', raise_exception=True)
def emp_create_view(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มชื่อพนักงานสำเร็จ!')
            return redirect('ems:emp_list')
    else:
        form = EmployeeForm()
    return render(request, 'ems/emp_form.html', {
        'form': form, 
        'title': 'Add New Employee'
    })
@login_required
@permission_required('ems.change_employee', raise_exception=True)
def emp_edit_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'ปรับปรุงชื่อพนักงานสำเร็จ!')
            return redirect('ems:emp_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'ems/emp_form.html', {
        'form': form, 
        'title': f'Edit Employee: {employee.employee_id}'
    })
@login_required
@permission_required('ems.delete_employee', raise_exception=True)
def emp_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'ลบชื่อพนักงานสำเร็จ!')
        return redirect('ems:emp_list')
    return render(request, 'ems/emp_confirm_delete.html', {
        'employee': employee
    })

@login_required
@permission_required('ems.view_employeeattachment', raise_exception=True)
def emp_upload_doc(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        attachment = EmployeeAttachment(
            employee=employee,
            document_type=request.POST['document_type'],
            title=request.POST['title'],
            file=request.FILES['file'],
            notes=request.POST.get('notes', '')
        )
        attachment.save()
        messages.success(request, 'เพิ่มเอกสารพนักงานสำเร็จ.')
        return redirect('ems:emp_edit', pk=pk)
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
@permission_required('ems.delete_employeeattachment', raise_exception=True)
def emp_delete_doc(request, pk):
    if request.method == 'POST':
        doc = get_object_or_404(EmployeeAttachment, pk=pk)
        employee_id = doc.employee.pk
        doc.delete()
        messages.success(request, 'ลบเอกสารพนักงานสำเร็จ.')
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
@permission_required('ems.change_employee', raise_exception=True)
def emp_edit_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'ปรับปรุงเอกสารพนักงานสำเร็จ!')
            return redirect('ems:emp_list')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'ems/emp_form.html', {
        'form': form,
        'title': f'Edit Employee: {employee.employee_id}',
        'employee': employee,
        'document_types': EmployeeAttachment.DOCUMENT_TYPES
    })











@login_required

def emp_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=employees_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    writer = csv.writer(response)
    # Only include fields that exist in your Employee model
    writer.writerow([
        'employee_id',
        'first_name',
        'last_name',
        'email',
        'position',
        'hire_date'
    ])
    
    employees = Employee.objects.all()
    for employee in employees:
        writer.writerow([
            employee.employee_id,
            employee.first_name,
            employee.last_name,
            employee.email,
            employee.position,
            employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else ''
        ])
    
    return response




import qrcode
import base64
from io import BytesIO

@login_required
def emp_card_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Generate QR code with employee info
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"ID: {employee.employee_id}\nName: {employee.first_name} {employee.last_name}\nPosition: {employee.position}")
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'employee': employee,
        'qr_code': qr_code
    }
    return render(request, 'ems/emp_card.html', context)










from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import Attendance, Employee
from .forms import AttendanceForm

from django.db.models import Q

@login_required
@permission_required('ems.view_attendance', raise_exception=True)
def attendance_list(request):
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Base queryset with employee data
    attendance_list = Attendance.objects.all().select_related('employee')
    
    # Apply search filter if query exists
    if search_query:
        attendance_list = attendance_list.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )
    
    # Order by date descending
    attendance_list = attendance_list.order_by('date')
    
    # Count by status
    total_count = attendance_list.count()
    present_count = attendance_list.filter(status='present').count()
    absent_count = attendance_list.filter(status='absent').count()
    late_count = attendance_list.filter(status='late').count()
    
    # Pagination
    paginator = Paginator(attendance_list, 5)
    page = request.GET.get('page')
    attendances = paginator.get_page(page)
    
    context = {
        'attendances': attendances,
        'search_query': search_query,
        'total_count': total_count,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
    }
    
    return render(request, 'ems/attendance_list.html', context)

@login_required
@permission_required('ems.add_attendance', raise_exception=True)
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'สร้างข้อมูลเรียบร้อย.')
            return redirect('ems:attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'ems/attendance_form.html', {
        'form': form,
        'title': 'Add Attendance Record'
    })

@login_required
@permission_required('ems.change_attendance', raise_exception=True)
def attendance_edit(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'สร้างข้อมูลเรียบร้อย.')
            return redirect('ems:attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'ems/attendance_form.html', {
        'form': form,
        'title': 'Edit Attendance Record'
    })

@login_required
@permission_required('ems.delete_attendance', raise_exception=True)
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'สร้างข้อมูลเรียบร้อย')
        return redirect('ems:attendance_list')
    return render(request, 'ems/attendance_confirm_delete.html', {'attendance': attendance})



@login_required
@permission_required('ems.import_attendance', raise_exception=True)
def attendance_import(request):
    if request.method == 'POST' and request.FILES.get('attendance_file'):
        csv_file = request.FILES['attendance_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('ems:attendance_list')
        
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        success_count = 0
        error_count = 0
        errors = []

        try:
            for row in reader:
                try:
                    # Get employee
                    employee = Employee.objects.get(employee_id=row['Employee ID'])
                    
                    # Try different date formats
                    date_formats = ['%Y-%m-%d', '%d/%m/%y', '%d-%m-%Y', '%d/%m/%Y']
                    attendance_date = None
                    
                    for date_format in date_formats:
                        try:
                            attendance_date = datetime.strptime(row['Date'], date_format).date()
                            break
                        except ValueError:
                            continue
                    
                    if attendance_date is None:
                        raise ValueError(f"Invalid date format: {row['Date']}")
                    
                    # Parse times
                    clock_in = datetime.strptime(row['Clock In'], '%H:%M').time() if row['Clock In'] else None
                    clock_out = datetime.strptime(row['Clock Out'], '%H:%M').time() if row['Clock Out'] else None
                    
                    # Create or update attendance record
                    attendance, created = Attendance.objects.update_or_create(
                        employee=employee,
                        date=attendance_date,
                        defaults={
                            'clock_in': clock_in,
                            'clock_out': clock_out,
                            'status': row.get('Status', 'present')
                        }
                    )
                    success_count += 1
                    
                except Employee.DoesNotExist:
                    error_count += 1
                    errors.append(f"Employee ID {row['Employee ID']} not found")
                except ValueError as e:
                    error_count += 1
                    errors.append(f"Error in row {success_count + error_count + 1}: {str(e)}")
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error in row {success_count + error_count + 1}: {str(e)}")

            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} attendance records.')
            if error_count > 0:
                messages.warning(request, f'Failed to import {error_count} records.')
                for error in errors[:5]:
                    messages.error(request, error)
                if len(errors) > 5:
                    messages.error(request, f'...and {len(errors) - 5} more errors')
                    
        except Exception as e:
            messages.error(request, f'Error reading CSV file: {str(e)}')
            
    return redirect('ems:attendance_list')

@login_required
@permission_required('ems.export_attendance', raise_exception=True)
def attendance_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Employee Name', 'Date', 'Clock In', 'Clock Out', 'Status'])
    
    attendances = Attendance.objects.all().select_related('employee')
    for attendance in attendances:
        writer.writerow([
            attendance.employee.employee_id,
            f"{attendance.employee.first_name} {attendance.employee.last_name}",
            attendance.date.strftime('%Y-%m-%d'),
            attendance.clock_in.strftime('%H:%M') if attendance.clock_in else '',
            attendance.clock_out.strftime('%H:%M') if attendance.clock_out else '',
            attendance.status
        ])
    
    return response




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Psalary
from .forms import PsalaryForm

@login_required
@permission_required('ems.view_psalary', raise_exception=True)
def psalary_list_view(request):
    # Initialize base queryset
    psalaries = Psalary.objects.all().select_related('employee')
    paginator = Paginator(psalaries, 5)  # แบ่งหน้า, 5 รายการต่อหน้า
    page_number = request.GET.get('page')  # ดึงหมายเลขหน้าจาก URL
    page_obj = paginator.get_page(page_number)  # ดึงหน้าที่ต้องการแสดง
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    selected_year = request.GET.get('year', '')
    selected_month = request.GET.get('month', '')
    
    # Apply filters
    if search_query:
        psalaries = psalaries.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )
    
    if selected_year:
        psalaries = psalaries.filter(year=selected_year)
    
    if selected_month:
        psalaries = psalaries.filter(month=selected_month)
    
    # Get unique years and months for filters
    years = Psalary.objects.dates('created_at', 'year').values_list('year', flat=True).distinct()
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), 
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    # Order and paginate
    psalaries = psalaries.order_by('-year', '-month')
    paginator = Paginator(psalaries, 5)  # Show 5 records per page
    page = request.GET.get('page', 1)
    psalaries = paginator.get_page(page)
    
    context = {
        'psalaries': psalaries,
        'years': years,
        'months': months,
        'search_query': search_query,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'psalaries': page_obj,  # ส่งข้อมูลที่แบ่งหน้าไปยังเทมเพลต
    }
    
    return render(request, 'ems/psalary_list.html', context)

@login_required
@permission_required('ems.add_psalary', raise_exception=True)
def psalary_create(request):
    if request.method == 'POST':
        form = PsalaryForm(request.POST)
        if form.is_valid():
            psalary = form.save(commit=False)
            # Convert year from string to integer before saving
            psalary.year = int(form.cleaned_data['year'])
            psalary.save()
            messages.success(request, 'สร้างรายการเงินเดือนสำเร็จ...')
            return redirect('ems:psalary_list')
    else:
        form = PsalaryForm()
    return render(request, 'ems/psalary_form.html', {
        'form': form,
        'title': 'Create Salary Record'
    })

@login_required
@permission_required('ems.change_psalary', raise_exception=True)
def psalary_edit(request, pk):
    psalary = get_object_or_404(Psalary, pk=pk)
    if request.method == 'POST':
        form = PsalaryForm(request.POST, instance=psalary)
        if form.is_valid():
            psalary = form.save(commit=False)
            psalary.year = int(form.cleaned_data['year'])
            psalary.save()
            messages.success(request, 'Salary record updated successfully.')
            return redirect('ems:psalary_list')
    else:
        form = PsalaryForm(instance=psalary)
    return render(request, 'ems/psalary_form.html', {
        'form': form,
        'title': 'Edit Salary Record'
    })

@login_required
@permission_required('ems.delete_psalary', raise_exception=True)
def psalary_delete(request, pk):
    psalary = get_object_or_404(Psalary, pk=pk)
    if request.method == 'POST':
        psalary.delete()
        messages.success(request, 'Salary record deleted successfully.')
        return redirect('ems:psalary_list')
    return render(request, 'ems/psalary_confirm_delete.html', {'psalary': psalary})

@login_required
@permission_required('ems.view_psalary', raise_exception=True)
def get_employee_base_salary(request):
    employee_id = request.GET.get('employee_id')
    try:
        employee = Employee.objects.get(id=employee_id)
        return JsonResponse({'base_salary': str(employee.base_salary)})
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    

from django.http import JsonResponse
from datetime import datetime
import calendar

@login_required
@permission_required('ems.view_employee', raise_exception=True)
def get_employee_working_data(request):
    employee_id = request.GET.get('employee_id')
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    try:
        employee = Employee.objects.get(id=employee_id)
        # Get the first and last day of the month
        first_day = datetime(int(year), int(month), 1)
        _, last_day = calendar.monthrange(int(year), int(month))
        last_date = datetime(int(year), int(month), last_day)
        
        # Get actual days worked (excluding Sundays)
        days_worked = Attendance.objects.filter(
            employee=employee,
            date__range=(first_day, last_date),
            status='present'
        ).exclude(
            date__week_day=1  # Sunday is 1 in Django's week_day lookup
        ).count()
        
        # Calculate hours worked (8 hours per day)
        hours_worked = days_worked * 8
        
        return JsonResponse({
            'days_worked': days_worked,
            'hours_worked': hours_worked
        })
        
    except (Employee.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    



@login_required
@permission_required('ems.view_employee', raise_exception=True)
def get_employee_working_data(request):
    employee_id = request.GET.get('employee_id')
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))
    
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # Get working data
        working_data = Attendance.get_monthly_working_data(employee, year, month)
        
        # Get overtime data
        overtime_data = Attendance.get_monthly_overtime(employee, year, month)
        
        # Combine the data
        response_data = {
            'days_worked': working_data['actual_days'],
            'hours_worked': working_data['actual_hours'],
            'm_sat_overtime_hrs': overtime_data['mon_sat_ot'],
            'sun_overtime_hrs': overtime_data['sun_ot']
        }
        
        return JsonResponse(response_data)
        
    except (Employee.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@login_required
@permission_required('ems.view_psalary', raise_exception=True)
def psalary_print(request, pk):
    psalary = get_object_or_404(Psalary, pk=pk)
    context = {
        'psalary': psalary,
        'company_name': 'บริษัทมะลิวงษ์-สมาร์ทโซลูชั่น จำกัด',
        'company_address': 'เลขที่ 133 หมู่ที่ 15 หมู่บ้านวังไทร ตำบลหนองหลวง อำเภอลานกระบือ จังหวดกำแพงเพชร 62170',
    }
    return render(request, 'ems/psalary_slip_print.html', context)