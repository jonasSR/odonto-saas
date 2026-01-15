from django import forms
from .models import Patient
from .models import Appointment
from .models import Doctor



class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'dob', 'gender', 'contact', 'address', 'surgery', 'medication', 'medication_details', 'allergies']
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance and instance.pk:
            self.fields['dob'].disabled = True


class DoctorForm(forms.ModelForm):
    cro = forms.CharField(
        max_length=20, 
        label='CRO', 
        required=True, 
        help_text='Número do CRO do médico',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o número do CRO'})
    )
    genero = forms.ChoiceField(
        choices=Doctor.GENDER_CHOICES, 
        label='Gênero', 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Doctor
        fields = ['nome', 'especialidade', 'contato', 'email', 'endereco', 'data_cadastro', 'cro', 'genero', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome'}),
            'especialidade': forms.Select(choices=Doctor.SPECIALTY_CHOICES, attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o contato'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite o e-mail'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite o endereço'}),
            'data_cadastro': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Data de Cadastro'}),
        }



class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'reason']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }     