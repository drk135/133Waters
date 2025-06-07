from django import forms
from .models import Employee, EmployeeAttachment
from django.core.exceptions import ValidationError
from datetime import datetime


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [ 'first_name', 'last_name', 'email', 
                 'phone_number', 'hire_date', 'position', 'base_salary', 'bank_account','bank_name',
                 'profile_picture']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
  
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
                'employee_id': 'รหัสพนักงาน',
                'first_name': 'ชื่อ',
                'last_name': 'นามสกุล', 
                'email': 'อีเมล',
                'phone_number': 'เบอร์โทรศัพท์',
                'hire_date': 'วันที่เริ่มงาน',
                'position': 'ตำแหน่ง',
                'base_salary': 'เงินเดือน',
                'bank_account': 'บัญชีธนาคาร',
                'bank_name': 'ชื่อธนาคาร',
                'profile_picture': 'รูปประจำตัว'
            }





from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'clock_in', 'clock_out', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'clock_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'clock_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



from django import forms
from .models import Psalary

class PsalaryForm(forms.ModelForm):
    MONTHS = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December')
    ]

    month = forms.ChoiceField(choices=MONTHS, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
     # Generate year choices (current year and 5 years back)
    current_year = datetime.now().year
    YEARS = [(year, str(year)) for year in range(current_year - 4, current_year + 3)]

    month = forms.ChoiceField(
        choices=MONTHS, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    year = forms.ChoiceField(
        choices=YEARS,
        initial=current_year,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Psalary
        fields = ['employee', 'month', 'year', 'base_salary', 'plan_days_worked', 
                 'days_worked', 'plan_hrs_worked', 'hrs_worked', 'm_sat_overtime_hrs',
                 'sun_overtime_hrs', 'holiday_overtime_hrs', 'tax_deduction',
                 'social_security', 'other_deduction']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 12
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000
            }),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'plan_days_worked': forms.NumberInput(attrs={'class': 'form-control'}),
            'days_worked': forms.NumberInput(attrs={'class': 'form-control'}),
            'plan_hrs_worked': forms.NumberInput(attrs={'class': 'form-control'}),
            'hrs_worked': forms.NumberInput(attrs={'class': 'form-control'}),
            'm_sat_overtime_hrs': forms.NumberInput(attrs={'class': 'form-control'}),
            'sun_overtime_hrs': forms.NumberInput(attrs={'class': 'form-control'}),
            'holiday_overtime_hrs': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'social_security': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_deduction': forms.NumberInput(attrs={'class': 'form-control'})
        }
