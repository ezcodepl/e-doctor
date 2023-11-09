import calendar
import locale
import random
import os
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from itertools import groupby, zip_longest
from django import template
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from .forms import UserCreationForm, RegisterUserForm, UserUpdateForm,  PatientRegisterForm, \
    DoctorsScheduleForm, FizScheduleForm, NewsForm, NoteTemplatesForm, uploadFilesForm, PatientUpdateExtendForm, VisitForm
from .models import News, Patient, DoctorSchedule, FizSchedule, NoteTemplates, FilesModel, Visits, PruposeVisit
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
import time
from django.contrib.auth.decorators import login_required
from calendar import HTMLCalendar
from calendar import monthrange
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.edit import FormView
from django.db import connection
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
    #get all records from Patient with data form User where user_id
    all_patients = Patient.objects.order_by('user__last_name')

    query = request.GET.get('q')
    if query:
        #show all record from query
        all_patients = Patient.objects.filter(
            Q(street__icontains=query) | Q(city__icontains=query) |
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        ).distinct()

        #query count
        query_count  = Patient.objects.filter(
            Q(street__icontains=query) | Q(city__icontains=query) |
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        ).distinct().count()

        #pagination
        paginator = Paginator(all_patients, 10)
        page_num = request.GET.get('page', 1)

        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
    else:
        paginator = Paginator(all_patients, 10)
        page_num = request.GET.get('page', 1)
        query_count = ''

        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)

    return render(request, "vita/panel/patients_list.html", {'all_patients': all_patients, 'page_obj': page_obj, 'query_count': query_count})


def delete_patient_files(request, pk):
    patient = Patient.objects.order_by('user__id').get(id_patient=pk)
    path = os.path.join(f'vita/media/patient_files/{pk}/{request.POST.get("file")}')
    file_name= os.path.join(f'patient_files/{pk}/{request.POST.get("file")}')

    if os.path.isfile(path):
         file = FilesModel.objects.filter(files=request.POST.get("file"))
         file.delete()
         os.remove(path)
         messages.success(request, f'Plik o nazwie {request.POST.get("file")} usunięto')
    return redirect(f"/panel/patients/{pk}")

def patients_files(request, pk):
    patient = Patient.objects.order_by('user__id').get(id_patient=pk)
    patients_folder = f'vita/media/patient_files/{pk}'

    # templates notes of doctor
    templates = NoteTemplates.objects.all()
    ########### end templates notes of doctor ################

    if 'submit' in request.POST:
        ################  upload patient files ###################
        if request.method == 'POST':
            form = uploadFilesForm(request.POST, request.FILES)
            files = request.FILES.getlist('files')


            if form.is_valid():
                dirname = str(request.POST.get('id'))

                # checks and create a patient folder name as id_patient
                try:
                    os.mkdir(os.path.join('vita/media/patient_files/', dirname))
                    for f in files:
                        fs = FileSystemStorage(location=patients_folder)  # defaults to   MEDIA_ROOT
                        # d = date.today()
                        get_ext = str(f).split('.')
                        storage_save = fs.save(f, f)
                        fi = FilesModel(patient_id=dirname, files=str(f), ext=get_ext[1])
                        fi.save()
                    messages.success(request, 'Pliki dodano do akt pacjenta')
                except OSError as e:
                    if e.errno == 17:
                        for f in files:
                            fs = FileSystemStorage(location=patients_folder)  # defaults to   MEDIA_ROOT
                            # d = date.today()
                            get_ext = str(f).split('.')
                            storage_save = fs.save(f, f)
                            fi = FilesModel(patient_id=dirname, files=str(f), ext=get_ext[1])
                            fi.save()

                        messages.success(request, 'Pliki dodano do akt pacjenta')
            else:
                messages.error(request, 'Nie udało się dodać plików do akt pacjenta')
        else:
            form = uploadFilesForm()
    else:
        form = uploadFilesForm()


    if os.path.exists(f'vita/media/patient_files/{pk}') :
        all_files = FilesModel.objects.filter(patient_id=pk) #os.listdir(f'vita/media/patient_files/{pk}')  #
    else:
        all_files = ''
        messages.info(request, 'W aktach pacjenta nie jeszcze plików')

    #################### end upload patient files ###################################################

    return render(request, 'vita/panel/patient_details.html',{'patient': patient,'form': form, 'all_files':all_files, 'templates': templates })


def create_patient(request):
    if request.method == "POST":
        cform = RegisterUserForm(request.POST)
        cp_form = PatientRegisterForm(request.POST)
        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')[:1]  # check id_patient
        last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
        select_form = request.POST.get('select_form')

        if cform.is_valid() and cp_form.is_valid():
            if int(select_form) == 1:
                last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
                c_form = cform.save(commit=False)
                first_name = str(request.POST.get('first_name')).capitalize()
                last_name = str(request.POST.get('last_name')).capitalize()
                c_form.first_name = first_name
                c_form.last_name = last_name
                c_form.username = f'stacjonarny{random.sample(range(999), 1)[0]}'
                c_form.password = make_password(BaseUserManager().make_random_password())
                c_form.emial = 'stacjonarny@megavita.pl'
                c_form.save()

                #set next id_patient number
                if len(last_id_patient) < 1:
                    next_id_patient = 1
                else:
                    next_id_patient = last_id_patient[0]['id_patient'] + 1

                p_form_obj = cp_form.save(commit=False)
                p_form_obj.user_id = last_user_id
                p_form_obj.id_patient = next_id_patient
                p_form_obj.save()
                messages.success(request, (f"Dodano nowego pacjenta: {request.POST.get('first_name')} {request.POST.get('last_name')}"))
                return redirect('/panel/patients')
            else:
                form = RegisterUserForm(request.POST)
                pp_form = PatientRegisterForm(request.POST)

                if form.is_valid() and pp_form.is_valid():
                    form.save()
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password1']
                    user = authenticate(username=username, password=password)

                    # set next id_patient number
                if last_id_patient[0]['id_patient'] is None:
                    next_id_patient = 1
                else:
                    next_id_patient = last_id_patient[0]['id_patient']+1

                pp_form_obj = pp_form.save(commit=False)
                pp_form_obj.user_id = last_user_id
                pp_form_obj.id_patient = next_id_patient

                pp_form_obj.save()
                messages.success(request, (f"Dodano nowego pacjenta: {request.POST.get('first_name')} {request.POST.get('last_name')}"))
                return redirect('/panel/patients')

        else:
            #print(cform.errors)
            cform = RegisterUserForm()
            cp_form = PatientRegisterForm()
            form = RegisterUserForm()
            pp_form = PatientRegisterForm()
    else:
        cform = RegisterUserForm()
        cp_form = PatientRegisterForm()
        form = RegisterUserForm()
        pp_form = PatientRegisterForm()
    x = f'stacjonarny{random.sample(range(999), 1)[0]}'
    user_x = x
    return render(request, 'vita/panel/create_patient.html', {'cform': cform, 'cp_form': cp_form, 'form': form, 'pp_form': pp_form, 'user_x': user_x })

def update_patient(request, pk):
    patient = Patient.objects.order_by('user__id').get(id_patient=pk)
    user = User.objects.get(id=patient.user_id)
    print(patient.user_id)
    #print(connection.queries) #print sql
    if 'update' in request.POST:
       if request.method == 'POST':
          form_u = UserUpdateForm(request.POST, instance=user)
          form_p = PatientUpdateExtendForm(request.POST, instance=patient)
          print(request.POST)
          print(request.POST['first_name'])
          if form_u.is_valid() and form_p.is_valid():
              form_uu = form_u.save(commit=False)
              form_uu.first_name = request.POST['first_name']
              form_uu.last_name = request.POST['last_name']
              form_uu.email = request.POST['email']
              #print(connection.queries)
              form_uu.save()

              form_pp = form_p.save(commit=False)
              form_pp.pesel = request.POST['pesel']
              form_pp.nip = request.POST['nip']
              form_pp.date_of_birth = request.POST['date_of_birth']
              form_pp.street = request.POST['street']
              form_pp.birthplace = request.POST['birthplace']
              form_pp.gender = request.POST['gender']
              form_pp.education = request.POST['education']
              form_pp.marital_status = request.POST['marital_status']
              form_pp.number_of_children = request.POST['number_of_children']
              form_pp.blood_group = request.POST['blood_group']
              form_pp.notes = request.POST['notes']
              form_pp.doctor_notes = request.POST['doctor_notes']
              form_pp.save()
              #print(connection.queries)
              messages.success(request, 'Dane zostały zapisane')
              return redirect(f'/panel/patients/{pk}')
          else:
              print(form_u.errors)
       else:
           print('not request')
    else:
        print('xxxxxx')

    return render(request, 'vita/panel/patient_details.html', {'patient':patient, 'user': user})


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

    day_type = DoctorSchedule.objects.filter(date=date).values()

    if (day_type[0]['day_type'] == 'Pracujący'):

        for work_hours in day_type:  # work_hours result 08:00-21:00

            work_hours = work_hours['work_hours'].split('-')
            sh = work_hours[0].split(':')
            eh = work_hours[1].split(':')

        start_hour = int(sh[0])  # 8
        end_hour = int(eh[0])  # 21
        scheme = int(day_type[0]['scheme']) #30m
        #date_sch = (day_type[0]['date']).strftime('%Y-%m-%d')


        start_time = datetime(1,1,1, start_hour)
        end_time = datetime(1, 1, 1, end_hour)


        h =[]

        check_visit = Visits.objects.filter(date=get_date, time__gte=sh[0], time__lte=eh[0]).select_related(
        'patient__user__pruposevisit').values('patient__user__first_name', 'patient__user__last_name', 'time','patient_id', 'prupose_visit__purpose_name', 'prupose_visit_id','visit')


        while start_time <= end_time:
            h.append(start_time.strftime("%H:%M"))
            start_time = start_time + timedelta(minutes=scheme)
           # h.extend(check_visit)

        # Tworzymy pusty słownik, który będzie przechowywał pary godzina: wizyta
        visits_dict = {}

        # Iterujemy po liście h, która zawiera godziny pracy lekarza
        for hour in h:
            # Sprawdzamy, czy godzina jest typu string, a nie słownik z danymi wizyty
            if isinstance(hour, str):
                # Iterujemy po liście check_visit, która zawiera dane wizyt
                for visit in check_visit:
                    # Sprawdzamy, czy godzina wizyty jest równa godzinie pracy
                    if visit['time'] == hour:
                        # Dodajemy parę godzina: wizyta do słownika
                        visits_dict[hour] = visit
                        # Przerywamy wewnętrzną pętlę, ponieważ znaleźliśmy pasującą wizytę
                        break
                # Jeśli nie znaleźliśmy pasującej wizyty, dodajemy parę godzina: None do słownika
                else:
                    visits_dict[hour] = None

        # Wyświetlamy słownik z godzinami i wizytami
        get_patient = User.objects.filter(id=check_visit[0]['patient_id']).values()
       # get_pruposevisit = PruposeVisit.objects.filter(id=check_visit[0]['prupose_visit_id']).values()

        print(visits_dict)


    else:
        print('Wolny')

    context = {
        'today': today,
        'get_date': get_date,
        'h': h,
        'visits': visits_dict,
        'patient_name': get_patient
        # 'pv':get_pruposevisit
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
        pe_form = PatientUpdateExtendForm(request.POST,
                                   request.FILES,
                                   instance=request.user.patient)
        if u_form.is_valid() and pe_form.is_valid():
            u_form.save()
            pe_form.save()
            messages.success(request, f'Twoje dane zostały zapisane!')
            return redirect('profile')

    else:
        patient = Patient.objects.all().values()

        u_form = UserUpdateForm(instance=request.user)
        pe_form = PatientUpdateExtendForm(instance=request.user.patient)

    context = {
        'u_form': u_form,
        'pe_form': pe_form
    }

    return render(request, 'vita/patient/profile.html', context)

def contact(request):
    if request.method == 'POST':

        contact = User(request.POST)
        context = {
            'contact': contact
        }

    return redirect('/news', request,  context)

def create_visit(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    vdate = request.POST['date']
    vtime = request.POST['time']
    vo = request.POST['office']

    if request.method == "POST":
        cform = RegisterUserForm(request.POST)
        cp_form = PatientRegisterForm(request.POST)
        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')[:1]  # check id_patient
        last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
        select_form = request.POST.get('select_form')

        if cform.is_valid() and cp_form.is_valid():
            if int(select_form) == 1:
                last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
                c_form = cform.save(commit=False)
                first_name = str(request.POST.get('first_name')).capitalize()
                last_name = str(request.POST.get('last_name')).capitalize()
                c_form.first_name = first_name
                c_form.last_name = last_name
                c_form.username = f'stacjonarny{random.sample(range(999), 1)[0]}'
                c_form.password = make_password(BaseUserManager().make_random_password())
                c_form.emial = 'stacjonarny@megavita.pl'
                c_form.save()

                # set next id_patient number
                if len(last_id_patient) < 1:
                    next_id_patient = 1
                else:
                    next_id_patient = last_id_patient[0]['id_patient'] + 1

                p_form_obj = cp_form.save(commit=False)
                p_form_obj.user_id = last_user_id
                p_form_obj.id_patient = next_id_patient
                p_form_obj.save()
                messages.success(request, (
                    f"Dodano nowego pacjenta: {request.POST.get('first_name')} {request.POST.get('last_name')}"))
                return redirect('/panel/patients')
            else:
                form = RegisterUserForm(request.POST)
                pp_form = PatientRegisterForm(request.POST)

                if form.is_valid() and pp_form.is_valid():
                    form.save()
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password1']
                    user = authenticate(username=username, password=password)

                    # set next id_patient number
                if last_id_patient[0]['id_patient'] is None:
                    next_id_patient = 1
                else:
                    next_id_patient = last_id_patient[0]['id_patient'] + 1

                pp_form_obj = pp_form.save(commit=False)
                pp_form_obj.user_id = last_user_id
                pp_form_obj.id_patient = next_id_patient

                pp_form_obj.save()
                messages.success(request, (
                    f"Dodano nowego pacjenta: {request.POST.get('first_name')} {request.POST.get('last_name')}"))
                return redirect('/panel/patients')

        else:
            # print(cform.errors)
            cform = RegisterUserForm()
            cp_form = PatientRegisterForm()
            form = RegisterUserForm()
            pp_form = PatientRegisterForm()
    else:
        cform = RegisterUserForm()
        cp_form = PatientRegisterForm()
        form = RegisterUserForm()
        pp_form = PatientRegisterForm()
    x = f'stacjonarny{random.sample(range(999), 1)[0]}'
    user_x = x

    return render(request, 'vita/panel/create_visit.html', {'cform': cform, 'cp_form': cp_form, 'form': form,
            'pp_form': pp_form, 'user_x': user_x, 'vd': vdate, 'vt': vtime, 'vo': vo })