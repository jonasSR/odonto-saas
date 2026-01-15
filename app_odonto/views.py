from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from .models import Patient, Appointment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PatientForm
from .forms import AppointmentForm
from .models import Appointment, Patient, Alert, Billing, Expense
from django.utils.timezone import now
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone
from datetime import datetime, time
from django.db.models import Sum
from .models import Doctor
from .forms import DoctorForm
from django.http import JsonResponse

# @login_required
# def some_view(request):  #OK
#     return render(request, 'template.html')

# LOGIN
def login_view(request): # OK
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Corrigido para chamar a função de login do Django
                return redirect('interface')
            else:
                return render(request, 'login/login.html', {'error': 'Nome de usuário ou senha inválidos'})
        else:
            return render(request, 'login/login.html', {'error': 'Por favor, preencha todos os campos.'})
    return render(request, 'login/login.html')

# ESQUECI A SENHA
@login_required
def change_password_view(request):  # OK
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            return redirect('config')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'change_password/change_password.html', {'form': form})

# REGISTRAR
def register_view(request): # OK
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if username and password and password_confirm:
            if password == password_confirm:
                if User.objects.filter(username=username).exists():
                    return render(request, 'register/register.html', {'error': 'Nome de usuário já existe'})
                else:
                    User.objects.create_user(username=username, password=password)
                    return redirect('login')
            else:
                return render(request, 'register/register.html', {'error': 'As senhas não coincidem'})
        else:
            return render(request, 'register/register.html', {'error': 'Por favor, preencha todos os campos.'})
    return render(request, 'register/register.html')


def interface_view(request):
    today = timezone.localdate()
    
    # Consultas Futuras
    upcoming_appointments = Appointment.objects.filter(date__gte=today).order_by('date')[:5]

    # Pacientes Recentes
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    # Alertas e Notificações
    alerts = Alert.objects.filter(date__gte=today).order_by('-date')[:5]

    context = {
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
        'alerts': alerts,
    }

    return render(request, 'interface/interface.html', context)


def appointments_view(request):
    patients = Patient.objects.all()
    selected_patient = None
    patient_details = None

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            # Gere e defina o número de protocolo
            appointment.protocol_number = Appointment.generate_protocol_number()
            appointment.save()
            # Adicione a mensagem de sucesso
            messages.success(request, f'Consulta marcada com sucesso! Número do Protocolo: {appointment.protocol_number}')
            return redirect('appointments')  # Redireciona após salvar
    else:
        form = AppointmentForm()

    if 'patient' in request.GET:
        patient_id = request.GET.get('patient')
        try:
            selected_patient = Patient.objects.get(id=patient_id)
            patient_details = {
                'name': selected_patient.name,
                'dob': selected_patient.dob,
                'contact': selected_patient.contact,
                'address': selected_patient.address,
                'surgery': selected_patient.surgery,
                'medication': selected_patient.medication,
                'medication_details': selected_patient.medication_details,
                'allergies': selected_patient.allergies,
            }
        except Patient.DoesNotExist:
            selected_patient = None

    context = {
        'form': form,
        'patients': patients,
        'selected_patient': selected_patient,
        'patient_details': patient_details,
    }
    return render(request, 'appointments/add_appointments.html', context)


def consultas_marcadas_view(request):
    appointments = Appointment.objects.all()  # Filtre conforme necessário
    context = {
        'appointments': appointments,
    }
    return render(request, 'appointments/search_appointments.html', context)


def reschedule_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointmentId')
        new_date = request.POST.get('newDate')
        reason = request.POST.get('reason')

        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Verificar se a consulta já foi cancelada
        if appointment.status == 'cancelled':
            return HttpResponse("Não é possível remarcar uma consulta que foi cancelada.", status=400)

        # Atualizar a consulta
        appointment.date = new_date
        appointment.new_date = new_date
        appointment.reason = reason
        appointment.status = 'rescheduled'
        appointment.save()

        return redirect('search_appointments')
    return HttpResponse("Método não permitido.", status=405)


def cancel_appointment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointmentId')
        reason = request.POST.get('reason')

        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Verificar se a consulta já foi cancelada
        if appointment.status == 'cancelled':
            return HttpResponse("A consulta já está cancelada.", status=400)

        # Atualizar a consulta
        appointment.status = 'cancelled'
        appointment.cancel_reason = reason
        appointment.save()

        return redirect('search_appointments')
    return HttpResponse("Método não permitido.", status=405)

# PACIENTES
def patients_view(request): # OK
    patients = Patient.objects.all()
    return render(request, 'patients/patients.html', {'patients': patients})


def add_patient_view(request): # OK
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente cadastrado com sucesso!")
            return redirect('add_patient')
        else:
            print("Form errors:", form.errors)
    else:
        form = PatientForm()
    
    return render(request, 'patients/patients.html', {'form': form})


def search_patient_view(request): # OK
    search = request.GET.get('search')
    if search:
        patients = Patient.objects.filter(name__icontains=search)
    else:
        patients = Patient.objects.all()
    
    return render(request, 'patients/search_patient.html', {'patients': patients})


def edit_patient(request, patient_id): # OK
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('search_patient')
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patients/edit_patient.html', {'form': form, 'patient': patient})


# DASHBOARD
def dashboard_view(request): # OK
    return render(request, 'dashboard/dashboard.html')


def dashboard_view(request): # OK
    today = timezone.now().date()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        if start_date_str:
            start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        else:
            start_date = timezone.make_aware(datetime.combine(today.replace(day=1), time.min))
    except (ValueError, TypeError):
        start_date = timezone.make_aware(datetime.combine(today.replace(day=1), time.min))

    try:
        if end_date_str:
            end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d')) + timedelta(days=1) - timedelta(seconds=1)
        else:
            end_date = timezone.make_aware(datetime.combine(today, time.max))
    except (ValueError, TypeError):
        end_date = timezone.make_aware(datetime.combine(today, time.max))

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    total_appointments = Appointment.objects.filter(date__range=[start_date, end_date]).count()
    rescheduled_appointments = Appointment.objects.filter(status='rescheduled', date__range=[start_date, end_date]).count()
    canceled_appointments = Appointment.objects.filter(status='cancelled', date__range=[start_date, end_date]).count()
    future_appointments = Appointment.objects.filter(date__gt=today).count()

    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()

    from django.db.models import Count
    top_patients = Patient.objects.annotate(appointments_count=Count('appointment')).order_by('-appointments_count')[:5]

    context = {
        'start_date': start_date.date(),
        'end_date': end_date.date(),
        'total_patients': total_patients,
        'rescheduled_appointments': rescheduled_appointments,
        'canceled_appointments': canceled_appointments,
        'total_appointments': total_appointments,
        'total_doctors': total_doctors,
        'top_patients': top_patients,
    }
    
    return render(request, 'dashboard/dashboard.html', context)



# TRATAMENTOS
def treatments_view(request):
    return render(request, 'treatments/treatments.html')


def billing_view(request):
    return render(request, 'billing/billing.html')


def reports_view(request):
    return render(request, 'reports/reports.html')


def config_view(request): #FALTA ALGUMAS COISAS
    return render(request, 'config/config.html')

# SAIR
def logout_view(request): # OK
    # Realiza o logout do usuário
    auth_logout(request)
    # Redireciona para a página de login
    return redirect('login')



def add_doctor_view(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico cadastrado com sucesso!')
            return redirect('list_doctors')
        else:
            print(form.errors)  # Isso imprimirá os erros de validação no console.
    else:
        form = DoctorForm()
    return render(request, 'medicos/add_doctor.html', {'form': form})

def list_doctors_view(request):
    doctors = Doctor.objects.all()
    return render(request, 'medicos/list_doctors.html', {'doctors': doctors})


def edit_doctor_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.nome = request.POST.get('name')
        doctor.especialidade = request.POST.get('specialty')
        doctor.email = request.POST.get('email')
        doctor.contato = request.POST.get('contact')
        doctor.endereco = request.POST.get('address')
        doctor.genero = request.POST.get('gender')
        doctor.save()
        messages.success(request, 'Médico atualizado com sucesso!')
        return redirect('list_doctors')
    return render(request, 'medicos/edit_doctor.html', {'doctor': doctor})


def update_doctor_status(request, pk):
    if request.method == 'POST':
        try:
            doctor = Doctor.objects.get(pk=pk)
            new_status = request.POST.get('ativo') == 'true'
            doctor.ativo = new_status
            doctor.save()
            return JsonResponse({'success': True})
        except Doctor.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Médico não encontrado'})
    return JsonResponse({'success': False, 'error': 'Método não permitido'})