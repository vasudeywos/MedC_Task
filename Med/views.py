from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from users.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AppointmentForm,PrescriptionForm
from django.shortcuts import get_object_or_404, render, redirect
from .forms import AppointmentUpdateForm,BillForm
from .models import Appointment,Doctor_Profiles,Prescription,Bill
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

@login_required
def createappointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            messages.success(request, 'Appointment application submitted successfully!')
            return redirect('patient_pg')
    else:
        form = AppointmentForm()

    context = {
        'form': form,
    }

    return render(request, 'Med/appointment.html', context)

def all_Appointments(request):
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments
    }
    return render(request,'Med/allappnts.html',context )


def updtappointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    bills=Bill.objects.get(appointment=appointment)
    patient=appointment.patient
    info=Profile.objects.get(user=patient)

    # Check if the user has permission to update the appointment
    if not request.user.is_staff and appointment.patient != request.user:
        return redirect('profile')  # Redirect unauthorized users

    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, user=request.user,instance=appointment)
        if form.is_valid() and request.user.is_patient:
            form.save()
            if bills.amount == appointment.Pay_amount:
                appointment.status = 'completed'
                appointment.save()
            return redirect('patient_pg')
        if form.is_valid() and request.user.is_staff:
            form.save()
            return redirect('staff_pg')
    else:
        form = AppointmentUpdateForm(instance=appointment)


    context = {
        'form': form,
        'bills':bills,
        'user':request.user,
        'info':info,
    }

    return render(request, 'Med/apptupdt.html', context)

class DoctorListView(ListView):
    model=Doctor_Profiles
    template_name = 'Med/doclist.html'    # <app>/<model>_<viewtype>.html
    context_object_name = 'docs'

class DoctorDetailView(DetailView):
        model = Doctor_Profiles
        template_name = 'Med/doc_detail.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            doctor = self.object
            appointments = Appointment.objects.filter(Doctors_for_appnt=doctor)
            context['appointments'] = appointments
            return context


class DoctorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Doctor_Profiles
    fields=['name','specialization','contact_info']
    template_name = 'Med/doc_form.html'
    success_url = reverse_lazy('doc_list')

    def form_valid(self, form):
         return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff

class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Doctor_Profiles
    fields = ['name', 'specialization', 'contact_info']
    template_name = 'Med/doc_update.html'
    success_url = reverse_lazy('doc_list')

    def form_valid(self, form):
         return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class DoctorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Doctor_Profiles
    template_name = 'Med/doc_delete.html'
    success_url = reverse_lazy('doc_list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class PresciptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'Med/upload.html'
    success_url = reverse_lazy('staff_pg')


def download(request, presc_id):
    appointment = get_object_or_404(Appointment, pk=presc_id)
    document =appointment.Prescription
    response = HttpResponse(document.document, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.document.name}"'
    return response


def Createbill(request, appnt_id):
    appointment = get_object_or_404(Appointment, pk=appnt_id)

    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.appointment = appointment
            bill.save()
            return redirect('staff_pg')
    else:
        form = BillForm()

    context = {
        'form': form,
        'appointment': appointment
    }

    return render(request, 'Med/createbill.html', context)

def all_Bills(request):
    bills = Bill.objects.all()
    context = {
        'bills': bills
    }
    return render(request,'Med/allbills.html',context )