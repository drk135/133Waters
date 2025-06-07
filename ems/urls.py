from django.urls import path
from . import views
from django.conf.urls.static import static


app_name = 'ems'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # Add this line at the top
    # Employee URLs - prefix with emp_
    path('employee/', views.emp_list_view, name='emp_list'),
    path('employee/add/', views.emp_create_view, name='emp_add'),
    path('employee/<int:pk>/edit/', views.emp_edit_view, name='emp_edit'),
    path('employee/<int:pk>/delete/', views.emp_delete_view, name='emp_delete'),
    path('employee/<int:pk>/upload/', views.emp_upload_doc, name='emp_upload_doc'),
    path('document/<int:pk>/delete/', views.emp_delete_doc, name='emp_delete_doc'),  


    path('employee/<int:pk>/card/', views.emp_card_view, name='emp_card'),

    

    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('attendance/import/', views.attendance_import, name='attendance_import'),
    path('attendance/export/', views.attendance_export, name='attendance_export'),


   
    
    
    # Salary paths
    path('psalary/', views.psalary_list_view, name='psalary_list'),
    path('psalary/add/', views.psalary_create, name='psalary_create'),
    path('psalary/<int:pk>/edit/', views.psalary_edit, name='psalary_edit'),
    path('psalary/<int:pk>/delete/', views.psalary_delete, name='psalary_delete'),
    path('psalary/<int:pk>/print/', views.psalary_print, name='psalary_print'),
    #path('psalary/<int:pk>/mark-paid/', views.psalary_mark_paid, name='psalary_mark_paid'),
    
    # API endpoints
    path('get-employee-base-salary/', views.get_employee_base_salary, name='get_employee_base_salary'),
    path('get-employee-working-data/', views.get_employee_working_data, name='get_employee_working_data'),

    path('psalary/<int:pk>/print/', views.psalary_print, name='psalary_print'),

    
    
]