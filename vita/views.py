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
import time
from django.contrib.auth.decorators import login_required
from calendar import HTMLCalendar
from calendar import monthrange




# Create your views here.

# Home links
################################################################################################
def home(request):
    return render(request, "vita/home.html")

def terminarz(request):

    # if request.method == "POST":
    #     form = DoctorsSchedule(request.POST)
    #
    #     if form.is_valid():
    #
    #         form.save()
    #     else:
    #         print(form.is_valid()) # form contains data and errors
    #         print(form.errors)
    #         form = DoctorsSchedule()


    months = {'1':'Styczeń', '2':'Luty','3':'Marzec','4':'Kwiecień','5':'Maj','6':'Czerwiec','7':'Lipiec',
              '8':'Sierpień', '9':'Wrzesień','10':'Październik','11':'Listopad','12':'Grudzień'}

    today = datetime.now()
    now = date.today()

    locale.setlocale(locale.LC_TIME, 'pl_PL')


    ##################### days of month list ######################################
    today_year_1 = today.year + 1
    today_year_2 = today.year + 2

    get_year = today.year
    get_month = today.month

    if request.GET.get('year') and request.GET.get('month'):

        y = int(request.GET.get('year'))
        m = int(request.GET.get('month'))
        btn_y = int(request.GET.get('year'))

    else:

        y = today.year
        m = today.month
        btn_y = today.year

    date_list = {}
    for d in range(1, monthrange(y, m)[1] + 1):
        x = '{:04d}-{:02d}-{:02d}'.format(y, m, d)
        dayName = datetime.strptime(x, '%Y-%m-%d').weekday()
        date_list[x] = calendar.day_name[dayName].capitalize()

    ################### end days of month list #################################
    btn_today = today.year
    btn_today_1 = today.year + 1
    btn_today_2 = today.year + 2


    context = {
        'today': today,
        'now': now,
        'months': months,
        'date_list': date_list,
        'btn_today': btn_today,
        'btn_today_1': btn_today_1,
        'btn_today_2': btn_today_2,
        'btn_y': btn_y
    }
    return render(request, "vita/panel/terminarz.html", context)

def panel(request, date):

    today = date.today()
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    # if today:
    #     get_date = current_path.replace('/', '')
    # else:
    #     get_date = full_path

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