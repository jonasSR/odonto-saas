from django.urls import path
from app_odonto import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('interface/', views.interface_view, name='interface'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('add_appointments/', views.appointments_view, name='add_appointments'),
    path('search_appointments/', views.consultas_marcadas_view, name='search_appointments'),
    path('reschedule_appointment/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel_appointment/', views.cancel_appointment, name='cancel_appointment'),
    path('patients/', views.patients_view, name='patients'), #OK
    path('add-patient/', views.add_patient_view, name='add_patient'), #OK
    path('search_patient/', views.search_patient_view, name='search_patient'), #OK
    path('edit_patient/<int:patient_id>/', views.edit_patient, name='edit_patient'), #OK
    path('treatments/', views.treatments_view, name='treatments'),
    path('billing/', views.billing_view, name='billing'),
    path('reports/', views.reports_view, name='reports'),
    path('config/', views.config_view, name='config'),
    path('change_password/', views.change_password_view, name='change_password'), #OK
    path('logout/', views.logout_view, name='logout'), #OK
    path('add-doctor/', views.add_doctor_view, name='add_doctor'),
    path('list-doctors/', views.list_doctors_view, name='list_doctors'),
    path('update_doctor_status/<int:pk>/', views.update_doctor_status, name='update_doctor_status'),
    path('edit-doctor/<int:pk>/', views.edit_doctor_view, name='edit_doctor'),

]