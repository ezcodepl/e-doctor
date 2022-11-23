import calendar
import locale
from itertools import groupby

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserCreationForm, RegisterUserForm, UserUpdateForm, PatientUpdateForm, PatientRegisterForm, DoctorsSchedule
from .models import News, Patient, DoctorSchedule
from django.contrib.auth.models import User
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from calendar import HTMLCalendar




# Create your views here.

# Home links
################################################################################################
def home(request):
    return render(request, "vita/home.html")

def terminarz(request):
    today = date.today()
    month = calendar.month(today.year, today.month)
    obj = calendar.Calendar()
    locale.setlocale(locale.LC_TIME, 'pl_PL')

    get_schedule = DoctorSchedule.objects.all()

    if get_schedule:
        calendars = obj.itermonthdays(today.year, today.month)
    else:
        #messages.warning(request, ("Nie znaleziono terminarza na wybrany miesiąc"))
        calendars = obj.itermonthdays(today.year, today.month)
    months = calendar.month_name[1:]

    months_number = [1,2,3,4,5,6,7,8,9,10,11,12]

    tc = calendar.HTMLCalendar(firstweekday=0)
    cal = tc.formatmonth(today.year, today.month)

    context = {
        'today': today,
        'months': months,
        'calendars': calendars,
        'cal': cal,
        'months_number': months_number
    }
    return render(request, "vita/panel/terminarz.html", context)
def panel(request, date):

    today = today = date.today()
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    context = {
        'today': today,
        'get_date': get_date
    }
    return render(request, "vita/panel/admbase.html", context)

def test(request):

    return render(request, "vita/test.html")


def new_visit(request):
    return render(request, "vita/patient/new_visit.html")


def appointments(request):
    return render(request, "vita/patient/appointments.html")


def history(request):
    return render(request, "vita/patient/history.html")


def news(request):
    all_news = News.objects.all().order_by('-data_wpisu').values()

    return render(request, "vita/news.html", {'all_news': all_news})

def laseroterapia(request):
    return render(request, "vita/laseroterapia.html")

def elektroterapia(request):
    return render(request, "vita/elektroterapia.html")

def krioterapia(request):
    return render(request, "vita/krioterapia.html")

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        pp_form = PatientRegisterForm(request.POST)

        last_id_patient = Patient.objects.all().values('id_patient')  # check id_patient

        if form.is_valid() and pp_form.is_valid():
            form.save()  # save user form

            # login user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)

            # set next id_patient number
            if last_id_patient is not None:
                next_id_patient = 1
            else:
                next_id_patient = last_id_patient[0]['id_patient'] + 1

            pp_form_obj = pp_form.save(commit=False)
            pp_form_obj.user = request.user
            pp_form_obj.id_patient = next_id_patient
            pp_form_obj.save()
            # messages.success(request, ("Registration Successful!"))
            return redirect('patient/profile')
    else:
        form = RegisterUserForm()
        pp_form = PatientRegisterForm()

    return render(request, 'vita/register.html', {
        'form': form, 'pp_form': pp_form
    })


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        today = date.today()
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if username == 'admin':
                    return redirect("/admin")
                elif username == 'lekarz':
                    return redirect(f'/panel/{today}')
                else:
                    return redirect("/")
            else:
                messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
        else:
            messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
    form = AuthenticationForm()

    return render(request, "vita/login.html", {"login_form": form})


def logout_request(request):
    logout(request)
    # messages.info(request, "You have successfully logged out.")
    return redirect("/")


def profile(request):
    if request.method == 'POST':
        patient = Patient.objects.all().values()
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = PatientUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.patient)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Twoje dane zostały zapisane!')
            return redirect('profile')

    else:
        patient = Patient.objects.all().values()

        u_form = UserUpdateForm(instance=request.user)
        p_form = PatientUpdateForm(instance=request.user.patient)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'vita/patient/profile.html', context)

def contact(request):
    if request.method == 'POST':

        contact = User(request.POST)
        context = {
            'contact': contact
        }

    return redirect('/news', request,  context)