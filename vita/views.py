import calendar
import locale
from itertools import groupby, zip_longest
from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserCreationForm, RegisterUserForm, UserUpdateForm, PatientUpdateForm, PatientRegisterForm, DoctorsScheduleForm, FizScheduleForm, NewsForm, NoteTemplatesForm
from .models import News, Patient, DoctorSchedule, FizSchedule, NoteTemplates
from django.contrib.auth.models import User
from datetime import date, datetime
import time
from django.contrib.auth.decorators import login_required
from calendar import HTMLCalendar
from calendar import monthrange
from django.contrib.auth.base_user import BaseUserManager

register = template.Library()


# Create your views here.

# Home links
################################################################################################
def home(request):
    return render(request, "vita/home.html")

def terminarz(request):

    today = datetime.now()
    locale.setlocale(locale.LC_TIME, 'pl_PL')

    def months():

        months = {'1': 'Styczeń', '2': 'Luty', '3': 'Marzec', '4': 'Kwiecień', '5': 'Maj', '6': 'Czerwiec',
                  '7': 'Lipiec',
                  '8': 'Sierpień', '9': 'Wrzesień', '10': 'Październik', '11': 'Listopad', '12': 'Grudzień'}
        return months

    ##################### days of month list create ######################################
    def days_of_month_list():
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

        return date_list

    ################### end days of month list create #################################

    def get_days_of_month_list():
        get_days_list = DoctorSchedule.objects.all().values()

        return get_days_list

    get_days_list = get_days_of_month_list() # get days list from function get_days_of_month_list()

    months = months()
    date_list = days_of_month_list()

    btn_today = today.year
    btn_today_1 = today.year + 1
    btn_today_2 = today.year + 2

    if request.GET.get('year') and request.GET.get('month'):
        btn_y = int(request.GET.get('year'))
    else:
        btn_y = today.year

    check_schedule = DoctorSchedule.objects.all().values('date')

    if len(check_schedule) > 0:
        form = DoctorsScheduleForm(request.POST)

        if request.method == 'POST':
            x1 = request.POST  # get data from request and getlist from QueryDict
            data_l = x1.getlist('data')
            day_type_l = x1.getlist('day_type')
            work_hours_l = x1.getlist('work_hours_start')
            scheme_l = x1.getlist('scheme')
            official_hours_l = x1.getlist('official_hours_start')

            for date, day_type, work_hours, official_hours, scheme in zip(data_l, day_type_l, work_hours_l,
                                                                          official_hours_l, scheme_l):
                post_dict = {'date': date, 'day_type': day_type, 'work_hours': work_hours,
                             'official_hours': official_hours, 'scheme': scheme}
                # print(post_dict)
                form = DoctorsScheduleForm(post_dict)
                form.save()
            messages.success(request, "Terminarz Lekarza został zaktualizowany")
    else:
        messages.warning(request, "Nie utworzono jeszcze terminarza")
        # if schedule not save in datebase - create it
        form = DoctorsScheduleForm(request.POST)
        if request.method == "POST":

            if form.is_valid():
                  x1 = request.POST #get data from request and getlist from QueryDict
                  data_l = x1.getlist('data')
                  day_type_l = x1.getlist('day_type')
                  work_hours_l = x1.getlist('work_hours_start')
                  scheme_l = x1.getlist('scheme')
                  official_hours_l = x1.getlist('official_hours_start')

                  for date, day_type, work_hours, official_hours, scheme in zip(data_l,day_type_l,work_hours_l,official_hours_l,scheme_l):

                      post_dict = {'date': date, 'day_type': day_type, 'work_hours': work_hours, 'official_hours': official_hours, 'scheme': scheme}
                      #print(post_dict)
                      form = DoctorsScheduleForm(post_dict)
                      form.save()

            else:
                form = DoctorsScheduleForm()

    return render(request, "vita/panel/terminarz.html", {'form': form, 'date_list': date_list,'months': months,
                                                         'today': today, 'get_days_list':get_days_list,
                                                         'btn_today':btn_today, 'btn_today_1': btn_today_1,
                                                         'btn_today_2': btn_today_2, 'btn_y': btn_y} )

def terminarz_fizykoterapii(request):

    today = datetime.now()
    locale.setlocale(locale.LC_TIME, 'pl_PL')

    def months():

        months = {'1': 'Styczeń', '2': 'Luty', '3': 'Marzec', '4': 'Kwiecień', '5': 'Maj', '6': 'Czerwiec',
                  '7': 'Lipiec',
                  '8': 'Sierpień', '9': 'Wrzesień', '10': 'Październik', '11': 'Listopad', '12': 'Grudzień'}
        return months

    ##################### days of month list create ######################################
    def days_of_month_list():
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

        return date_list

    ################### end days of month list create #################################

    def get_days_of_month_list():
        get_days_list = FizSchedule.objects.all().values()

        return get_days_list

    get_days_list = get_days_of_month_list() # get days list from function get_days_of_month_list()

    months = months()
    date_list = days_of_month_list()

    btn_today = today.year
    btn_today_1 = today.year + 1
    btn_today_2 = today.year + 2

    if request.GET.get('year') and request.GET.get('month'):
        btn_y = int(request.GET.get('year'))
    else:
        btn_y = today.year

    check_schedule = FizSchedule.objects.all().values('date')

    if len(check_schedule) > 0:
        form =FizScheduleForm(request.POST)

        if request.method == 'POST':
            x1 = request.POST  # get data from request and getlist from QueryDict
            data_l = x1.getlist('data')
            day_type_l = x1.getlist('day_type')
            work_hours_l = x1.getlist('work_hours_start')
            scheme_l = x1.getlist('scheme')
            official_hours_l = x1.getlist('official_hours_start')

            for date, day_type, work_hours, official_hours, scheme in zip(data_l, day_type_l, work_hours_l,
                                                                          official_hours_l, scheme_l):
                post_dict = {'date': date, 'day_type': day_type, 'work_hours': work_hours,
                             'official_hours': official_hours, 'scheme': scheme}
                # print(post_dict)
                form = FizScheduleForm(post_dict)
                form.save()
            messages.success(request, "Terminarz fizykoterapii został zaktualizowany")
    else:
        messages.warning(request, "Nie utworzono jeszcze terminarza")
        # if schedule not save in datebase - create it
        form = FizScheduleForm(request.POST)
        if request.method == "POST":

            if form.is_valid():
                  x1 = request.POST #get data from request and getlist from QueryDict
                  data_l = x1.getlist('data')
                  day_type_l = x1.getlist('day_type')
                  work_hours_l = x1.getlist('work_hours_start')
                  scheme_l = x1.getlist('scheme')
                  official_hours_l = x1.getlist('official_hours_start')

                  for date, day_type, work_hours, official_hours, scheme in zip(data_l,day_type_l,work_hours_l,official_hours_l,scheme_l):

                      post_dict = {'date': date, 'day_type': day_type, 'work_hours': work_hours, 'official_hours': official_hours, 'scheme': scheme}
                      #print(post_dict)
                      form = FizScheduleForm(post_dict)
                      form.save()

            else:
                form = FizScheduleForm()

    return render(request, "vita/panel/terminarz_f.html", {'form': form, 'date_list': date_list,'months': months,
                                                         'today': today, 'get_days_list':get_days_list,
                                                         'btn_today':btn_today, 'btn_today_1': btn_today_1,
                                                         'btn_today_2': btn_today_2, 'btn_y': btn_y} )


def patients_list(request):
    return render(request, "vita/panel/patients_list.html")


# def new_patient(request):
#     form = RegisterUserForm()
#     pp_form = PatientRegisterForm()
#     return render(request, "vita/panel/create_patient.html", {'form': form, 'pp_form': pp_form})

def create_patient(request):
    if request.method == "POST":

        cpform = RegisterUserForm(request.POST)
        cppp_form = PatientRegisterForm(request.POST)
        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')  # check id_patient
        print(request.POST)

        if cpform.is_valid() and cppp_form.is_valid():
            #cpform.save()  # save user form
            cp_form = cpform.save(commit=False)
            cp_form.username = request.POST.get('first_name') + "." + request.POST.get('last_name')
            cp_form.password = BaseUserManager().make_random_password()
            cp_form.emial = 'stacjonarny@xxx.pl'
            cp_form.save()

            # set next id_patient number
            if last_id_patient is not None:
                next_id_patient = 1
            else:
                next_id_patient = last_id_patient[0]['id_patient'] + 1

            pp_form_obj = cppp_form.save(commit=False)
            pp_form_obj.user = request.user
            pp_form_obj.id_patient = next_id_patient
            pp_form_obj.save()
            messages.success(request, ("Registration Successful!"))
            return redirect('patient/patients_list')
    else:

        cpform = RegisterUserForm()
        cppp_form = PatientRegisterForm()

    return render(request, 'vita/panel/create_patient.html', {
        'cpform': cpform, 'cppp_form': cppp_form
    })

def news_list(request):
    get_news = News.objects.order_by('-data_wpisu').values()

    if not get_news:
        messages.warning(request, 'Nie ma jeszcze żadnych dodanych aktualności')
    else:
        get_news = News.objects.order_by('-data_wpisu').values()

    return render(request, "vita/panel/news_list.html", {'get_news': get_news})
def create_news(request):

    if request.method == 'POST':
        n_form = NewsForm(request.POST)
        if n_form.is_valid():
            n_form.save()
            messages.success(request, 'Dodano nową aktualność')
            return redirect("/panel/news_list")
    else:
        n_form = NewsForm()

    context = {
        'n_form' : n_form
    }

    return render(request, "vita/panel/create_news.html", context)

def edit_news(request, pk):
    news = get_object_or_404(News, id_news = pk)
    return render(request, "vita/panel/edit_news.html", {'news': news})
def update_news(request, pk):
    obj = get_object_or_404(News, id_news = pk)
    if request.method == 'POST':
        n_form = NewsForm(request.POST, instance=obj)
        if n_form.is_valid():
            n_form.save()
            messages.success(request, 'Dane zapisano')
            return redirect("/panel/news_list")
    else:
        n_form = NewsForm(instance=obj)

    context = {
        'n_form' : n_form
    }

    return render(request, "vita/panel/create_news.html", context)

def delete_news(request, pk):
    news = News.objects.get(id_news = pk)

    if request.method == "GET":
        news.delete()
        messages.info(request, f'News o temacie: "{news.temat}" z dnia {news.data_wpisu} usunięto!')
        return redirect('/panel/news_list')
    else:
        messages.error(request, 'Nie udało się usunąć aktualności')
    context = {
        'news' : news
    }

    return render(request, "vita/panel/news_list.html", context)

def templates_list(request):
    get_templates = NoteTemplates.objects.order_by('-created_at').values()

    if not get_templates:
        messages.warning(request, 'Nie ma jeszcze żadnych dodanych szablonów notatek')
    else:
        get_news = NoteTemplates.objects.order_by('-created_at').values()

    return render(request, "vita/panel/templates_list.html", {'get_templates': get_templates})
def create_templates(request):

    if request.method == 'POST':
        form = NoteTemplatesForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Szablon notatki zapisano')
            return redirect("/panel/templates_list")
        else:
            form = NoteTemplatesForm()
            print(form.errors)
    else:
        form = NoteTemplatesForm()

    context = {
        'form' : form
    }

    return render(request, "vita/panel/create_templates.html", context)

def edit_templates(request, pk):
    templates = get_object_or_404(NoteTemplates, id= pk)
    return render(request, "vita/panel/edit_templates.html", {'templates': templates})
def update_templates(request, pk):
    obj = get_object_or_404(NoteTemplates, id = pk)
    print(obj)
    if request.method == 'POST':
        form = NoteTemplatesForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dane zapisano')
            return redirect("/panel/templates_list")
    else:
        form = NoteTemplatesForm(instance=obj)

    context = {
        'form' : form
    }

    return render(request, "vita/panel/create_templates.html", context)
def delete_templates(request, pk):
    templates = NoteTemplates.objects.get(id = pk)

    if request.method == "GET":
        templates.delete()
        messages.info(request, f'Szablon notatki o nazwie: "{templates.name}" usunięto!')
        return redirect('/panel/templates_list')
    else:
        messages.error(request, 'Nie udało się usunąć szablonu notatki')
    context = {
        'templates' : templates
    }

    return render(request, "vita/panel/templates_list.html", context)

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
    return render(request, "vita/panel/panel.html", context)

def test(request):

    return render(request, "vita/test.html")


def new_visit(request):
    return render(request, "vita/patient/new_visit.html")


def appointments(request):
    return render(request, "vita/patient/appointments.html")


def history(request):
    return render(request, "vita/patient/history.html")


def news(request):
    all_news = News.objects.order_by('-data_wpisu').filter(status=1).values()

    if not all_news:
        messages.info(request, 'W tej chwili nie opublikowano żadnych aktualności')

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
        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')  # check id_patient

        if form.is_valid() and pp_form.is_valid():
            form.save()  # save user form

            # login user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)

            # set next id_patient number
            if len(last_id_patient) < 1:
                next_id_patient = 1
            else:
                next_id_patient = last_id_patient[0]['id_patient'] + 1
                print(next_id_patient)
                print(last_id_patient[0]['id_patient'] + 1)

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