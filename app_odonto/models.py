from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
import random


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),  # Opcional, se você quiser permitir outras opções
    ]

    name = models.CharField(max_length=100)
    dob = models.DateField()
    contact = models.CharField(max_length=50)
    address = models.TextField()
    
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,  # Permite que o campo seja opcional
        null=True     # Permite que o campo seja nulo no banco de dados
    )
    surgery = models.TextField(blank=True, null=True)
    medication = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        default='nao'
    )
    medication_details = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    
    def __str__(self):
        return self.name



class Billing(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Billing on {self.date} - {self.amount}"


class Alert(models.Model):
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Expense on {self.date} - {self.amount}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Agendada'),
        ('cancelled', 'Cancelada'),
        ('rescheduled', 'Remarcada'),
    ]
    

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    reason = models.TextField()
    protocol_number = models.CharField(max_length=12, unique=True, blank=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    cancel_reason = models.TextField(null=True, blank=True)
    new_date = models.DateTimeField(null=True, blank=True)  # Data remarcada, se aplicável


    def save(self, *args, **kwargs):
        if not self.protocol_number:
            self.protocol_number = self.generate_protocol_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_protocol_number():
        while True:
            # Gera um número aleatório de 12 dígitos
            number = f'{random.randint(100000000000, 999999999999)}'
            # Verifica se o número é único
            if not Appointment.objects.filter(protocol_number=number).exists():
                return number

    def __str__(self):
        return f"Consulta com {self.patient.name} em {self.date} - Protocolo {self.protocol_number}"
    

class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    SPECIALTY_CHOICES = [
        ('dentist', 'Dentista'),
        ('orthodontist', 'Ortodontista'),
        ('surgeon', 'Cirurgião'),
        ('other', 'Outro'),
    ]
    
    nome = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=50, choices=SPECIALTY_CHOICES)
    contato = models.CharField(max_length=50)
    email = models.EmailField()
    endereco = models.TextField()
    data_cadastro = models.DateField()
    cro = models.CharField(max_length=20)
    genero = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')  # Novo campo
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome