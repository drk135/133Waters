from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import date
from decimal import Decimal
from datetime import datetime, date, timedelta, time

class Employee(models.Model):
    employee_id = models.CharField(max_length=9, unique=True, help_text="Format: 133MMYY## (MM=month 01-12, YY=year, ##=sequence 01-99)", blank=True, null=True)  # รหัสพนักงาน
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField()
    position = models.CharField(max_length=100)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account = models.CharField(max_length=20, blank=True, null=True)  # บัญชีธนาคาร
    bank_name = models.CharField(max_length=100, blank=True, null=True)  # ชื่อธนาคาร
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)  # รูปพนักงาน
    class Meta:[
        ("can_add_employee", "Can add employee"),
        ("can_view_employee", "Can view employee"),
        ("can_edit_employee", "Can edit employee"),
        ("can_delete_employee", "Can delete employee"),
    ]
    def save(self, *args, **kwargs):
        if not self.employee_id:
            today = timezone.now()
            month = today.strftime('%m')
            year = today.strftime('%y')
            prefix = f"133{month}{year}"
            last_employee = Employee.objects.filter(
                employee_id__startswith=prefix
            ).order_by('-employee_id').first()
            
            if last_employee:
                last_seq = int(last_employee.employee_id[-2:])
                new_seq = str(last_seq + 1).zfill(2)
            else:
                new_seq = "01"
                
            self.employee_id = f"{prefix}{new_seq}"
            print(f"Generated Employee ID: {self.employee_id}")  # Debugging
        
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.employee_id:
            return
            
        # ตรวจสอบรหัสพนักงาน
        if not self.employee_id.startswith("133"):
            raise ValidationError({
                "employee_id": "รหัสพนักงานต้องขึ้นต้นด้วย '133'"
            })
        
        if len(self.employee_id) != 9:
            raise ValidationError({
                "employee_id": "รหัสพนักงานต้องมีความยาว 9 ตัวอักษร"
            })
        
        try:
            month = self.employee_id[3:5]
            year = self.employee_id[5:7]
            sequence = self.employee_id[7:9]

            if not (month.isdigit() and year.isdigit() and sequence.isdigit()):
                raise ValidationError({
                    "employee_id": "เดือน ปี และลำดับต้องเป็นตัวเลขเท่านั้น"
                })

            month_val = int(month)
            if month_val < 1 or month_val > 12:
                raise ValidationError({
                    "employee_id": "เดือนต้องอยู่ระหว่าง 01-12"
                })

            seq_val = int(sequence)
            if seq_val < 1 or seq_val > 99:
                raise ValidationError({
                    "employee_id": "ลำดับต้องอยู่ระหว่าง 01-99"
                })

        except ValueError:
            raise ValidationError({
                "employee_id": "รูปแบบรหัสพนักงานไม่ถูกต้อง"
            })
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.employee_id})"

class EmployeeAttachment(models.Model):
    DOCUMENT_TYPES = [
        ('resume', 'Resume/CV'),
        ('contract', 'Employment Contract'),
        ('certificate', 'Certificates'),
        ('id_card', 'ID Card Copy'),
        ('education', 'Education Documents'),
        ('other', 'Other Documents'),
    ]

    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES
    )
    file = models.FileField(
        upload_to='employee_documents/'
    )
    title = models.CharField(
        max_length=255,
        help_text="Brief description of the document"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the document"
    )
    class meta:[
        ("can_add_employee_document", "Can add employee document"),
        ("can_view_employee_document", "Can view employee document"),
        ("can_edit_employee_document", "Can edit employee document"),
        ("can_delete_employee_document", "Can delete employee document"),
    ]
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Employee Document"
        verbose_name_plural = "Employee Documents"

    def __str__(self):
        return f"{self.employee.employee_id} - {self.get_document_type_display()} - {self.title}"

    def file_size(self):
        """Returns the file size in MB"""
        if self.file:
            return f"{self.file.size / (1024 * 1024):.2f} MB"
        return "0 MB"
    

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)
    class meta:[
        ("can_add_attendance", "Can add attendance"),
        ("can_view_attendance", "Can view attendance"),
        ("can_edit_attendance", "Can edit attendance"),
        ("can_delete_attendance", "Can delete attendance"),
    ]
    class Meta:
        ordering = ['-date', 'employee']
        unique_together = ['employee', 'date']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"

    def clean(self):
        if self.clock_in and self.clock_out:
            if self.clock_out < self.clock_in:
                raise ValidationError("Clock out time cannot be earlier than clock in time")

    def clean(self):
        if self.clock_in and self.clock_out:
            if self.clock_out < self.clock_in:
                raise ValidationError("Clock out time cannot be earlier than clock in time")

    @staticmethod
    def get_working_days(employee, start_date, end_date):
        """
        Calculate working days (excluding Sundays) between start_date and end_date
        for a specific employee
        """
        working_days = Attendance.objects.filter(
            employee=employee,
            date__range=(start_date, end_date),
            status='present'
        ).exclude(
            date__week_day=1  # Sunday is 1 in Django's week_day lookup
        ).count()
        
        return working_days   



    def calculate_working_hours(self):
        """Calculate total working hours excluding lunch break"""
        if not self.clock_in or not self.clock_out:
            return 0

        # Convert times to datetime for calculation
        date_obj = self.date
        clock_in_dt = datetime.combine(date_obj, self.clock_in)
        clock_out_dt = datetime.combine(date_obj, self.clock_out)
        
        # Handle overnight shifts
        if clock_out_dt < clock_in_dt:
            clock_out_dt += timedelta(days=1)

        # Define lunch break period (12:00-13:00)
        lunch_start = datetime.combine(date_obj, time(12, 0))
        lunch_end = datetime.combine(date_obj, time(13, 0))

        # Calculate total duration
        total_duration = clock_out_dt - clock_in_dt

        # Calculate lunch break duration
        if (clock_in_dt <= lunch_start and clock_out_dt >= lunch_end):
            # Full lunch break
            lunch_duration = timedelta(hours=1)
        elif (clock_in_dt <= lunch_end and clock_out_dt >= lunch_end):
            # Partial lunch break (started work during lunch)
            lunch_duration = lunch_end - clock_in_dt
        elif (clock_in_dt <= lunch_start and clock_out_dt >= lunch_start):
            # Partial lunch break (ended work during lunch)
            lunch_duration = clock_out_dt - lunch_start
        else:
            # No lunch break overlap
            lunch_duration = timedelta(0)

        # Calculate actual working hours
        working_hours = (total_duration - lunch_duration).total_seconds() / 3600
        return working_hours

    def calculate_overtime_hours(self):
        """Calculate overtime hours with different rates for weekdays and Sundays"""
        if not self.clock_in or not self.clock_out or self.status != 'present':
            return 0

        working_hours = self.calculate_working_hours()
        overtime_hours = max(0, working_hours - 8)

        if overtime_hours > 0:
            # Check if it's Sunday (isoweekday() returns 7 for Sunday)
            if self.date.isoweekday() == 7:
                # Sunday rate: 1 hour = 2 hours
                return overtime_hours * 2
            else:
                # Mon-Sat rate: 1 hour = 1.5 hours
                return overtime_hours * 1.5
        return 0

    @classmethod
    def get_monthly_overtime(cls, employee, year, month):
        """Calculate total overtime hours with different rates for Mon-Sat and Sunday"""
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        # Get all attendance records for the month
        records = cls.objects.filter(
            employee=employee,
            date__range=(first_day, last_day),
            status='present'
        )

        # Calculate overtime separately for weekdays and Sundays
        mon_sat_ot = 0
        sun_ot = 0

        for record in records:
            working_hours = record.calculate_working_hours()
            overtime = max(0, working_hours - 8)

            if overtime > 0:
                if record.date.isoweekday() == 7:  # Sunday
                    sun_ot += overtime * 2  # Sunday rate
                else:
                    mon_sat_ot += overtime * 1.5  # Mon-Sat rate

        return {
            'mon_sat_ot': round(mon_sat_ot, 1),
            'sun_ot': round(sun_ot, 1),
            'total_ot': round(mon_sat_ot + sun_ot, 1)
        }
    
    @classmethod
    def get_monthly_working_data(cls, employee, year, month):
        """Get actual days and hours worked in a month"""
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        # Get all present attendance records for the month
        records = cls.objects.filter(
            employee=employee,
            date__range=(first_day, last_day),
            status='present'
        )

        # Calculate actual days (count of attendance records)
        actual_days = records.count()

        # Calculate total hours worked
        total_hours = 0
        for record in records:
            total_hours += record.calculate_working_hours()

        return {
            'actual_days': actual_days,
            'actual_hours': round(total_hours, 1)
        }


class Psalary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)    
    plan_days_worked = models.PositiveIntegerField()
    days_worked = models.PositiveIntegerField()
    plan_hrs_worked = models.PositiveIntegerField()
    hrs_worked = models.PositiveIntegerField()
    m_sat_overtime_hrs = models.PositiveIntegerField(default=0)
    sun_overtime_hrs = models.PositiveIntegerField(default=0)
    holiday_overtime_hrs = models.PositiveIntegerField(default=0)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid')
    ]
    
    # ...existing fields...
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Payment Status'
    )
    paid_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Payment Date'
    )
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']
        verbose_name = 'Salary'
        verbose_name_plural = 'Salaries'

    def calculate_net_salary(self):
        """Calculate net salary including overtime and deductions"""
        # Convert rates to Decimal
        MON_SAT_RATE = Decimal('1.5')
        SUNDAY_RATE = Decimal('2.0')
        HOLIDAY_RATE = Decimal('3.0')
        HOURS_PER_DAY = Decimal('8')
        DAYS_PER_MONTH = Decimal('30')

        # Calculate hourly rate
        hourly_rate = self.base_salary / DAYS_PER_MONTH / HOURS_PER_DAY

        # Calculate overtime pay
        m_sat_ot = Decimal(str(self.m_sat_overtime_hrs)) * hourly_rate * MON_SAT_RATE
        sun_ot = Decimal(str(self.sun_overtime_hrs)) * hourly_rate * SUNDAY_RATE
        holiday_ot = Decimal(str(self.holiday_overtime_hrs)) * hourly_rate * HOLIDAY_RATE
        
        # Calculate actual salary based on days worked
        actual_salary = (self.base_salary / Decimal(str(self.plan_days_worked))) * Decimal(str(self.days_worked))
        
        # Total salary before deductions
        total_salary = actual_salary + m_sat_ot + sun_ot + holiday_ot
        
        # Deductions
        total_deductions = self.tax_deduction + self.social_security + self.other_deduction
        
        # Net salary
        return total_salary - total_deductions
    
    MONTHS = {
        1: 'January', 2: 'February', 3: 'March',
        4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September',
        10: 'October', 11: 'November', 12: 'December'
    }

    def get_month_display(self):
        return self.MONTHS.get(self.month, '')
    
def calculate_working_hours(self):
        """Calculate total working hours for the day"""
        if self.clock_in and self.clock_out:
            # Convert times to datetime for proper calculation
            in_dt = datetime.combine(self.date, self.clock_in)
            out_dt = datetime.combine(self.date, self.clock_out)
            
            # If clock_out is earlier than clock_in, assume it's next day
            if out_dt < in_dt:
                out_dt += timedelta(days=1)
            
            # Calculate duration in hours
            duration = out_dt - in_dt
            return duration.total_seconds() / 3600  # Convert to hours
        return 0

def calculate_overtime_hours(self):
        """Calculate overtime hours if worked more than 8 hours in a day"""
        if self.clock_in and self.clock_out:
            # Convert times to datetime for calculation
            date_obj = self.date
            clock_in_dt = datetime.combine(date_obj, self.clock_in)
            clock_out_dt = datetime.combine(date_obj, self.clock_out)
            
            # If clock_out is earlier than clock_in, assume it's next day
            if clock_out_dt < clock_in_dt:
                clock_out_dt += timedelta(days=1)
            
            # Calculate total hours worked
            total_hours = (clock_out_dt - clock_in_dt).total_seconds() / 3600
            
            # Return overtime hours if more than 8 hours worked
            return max(0, total_hours - 8)
        return 0

@classmethod
def get_monthly_overtime(cls, employee, year, month):
        """Calculate total overtime hours for Mon-Sat in a specific month"""
        # Get month range
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get all attendance records for Mon-Sat
        records = cls.objects.filter(
            employee=employee,
            date__range=(first_day, last_day),
            status='present'
        ).exclude(
            date__week_day=1  # Exclude Sundays (1 = Sunday in Django)
        )
        
        # Calculate total overtime
        total_overtime = 0
        for record in records:
            total_overtime += record.calculate_overtime_hours()
        
        return int(total_overtime)  # Convert to integer hours

class Meta:[
        ("can_add_salary", "Can add salary"),
        ("can_view_salary", "Can view salary"),
        ("can_edit_salary", "Can edit salary"),
        ("can_delete_salary", "Can delete salary"),     
    ]