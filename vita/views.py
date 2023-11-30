import calendar
import locale
import random
import os


from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from itertools import groupby, zip_longest
from django import template
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from django.views.decorators.http import require_GET

from .forms import UserCreationForm, RegisterUserForm, UserUpdateForm, PatientRegisterForm, \
    DoctorsScheduleForm, FizScheduleForm, NewsForm, NoteTemplatesForm, uploadFilesForm, PatientUpdateExtendForm, \
    VisitForm, VisitForm_f, DoctorVisitsForm
from .models import News, Patient, DoctorSchedule, FizSchedule, NoteTemplates, FilesModel, Visits, PruposeVisit, \
    Visits_f
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta, timezone
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

def docschedule(request):

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

    #check_schedule = DoctorSchedule.objects.all().values('date')
    dsdm = request.GET.get('month')
    dsdy = request.GET.get('year')
    dsdd = '10'
    dsd = f'{dsdy}-{dsdm}-{dsdd}'

    check_schedule = DoctorSchedule.objects.filter(date=dsd).exists() #today.strftime('%Y-%m-%d')

    if check_schedule:
        messages.warning(request, "Na ten miesiąc już utworzono kalendarz")
        x = DoctorSchedule.objects.filter(date=today.strftime('%Y-%m-%d'))
        print(x.query)
        form = DoctorsScheduleForm(request.POST)

        if request.method == 'POST':

            if not check_schedule:
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
                #check doctor shedule - visit today
                # ch_v = DoctorSchedule.objects.filter(date=today.strftime('%Y-%m-%d')).exists()
                #
                # if ch_v:
                #     messages.error(request, "Terminarz Lekarza został już na ten miesiąc ustalony")
                # else:
                 print('')

    else:
        messages.warning(request, "Nie utworzono jeszcze terminarza")
        # if schedule not save in datebase - create it

        form = DoctorsScheduleForm(request.POST)
        print(form.errors)
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

    return render(request, "vita/panel/docschedule.html", {'form': form, 'date_list': date_list,'months': months,
                                                         'today': today, 'get_days_list':get_days_list,
                                                         'btn_today':btn_today, 'btn_today_1': btn_today_1,
                                                         'btn_today_2': btn_today_2, 'btn_y': btn_y} )

def fizschedule(request):
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

    get_days_list = get_days_of_month_list()  # get days list from function get_days_of_month_list()

    months = months()
    date_list = days_of_month_list()

    btn_today = today.year
    btn_today_1 = today.year + 1
    btn_today_2 = today.year + 2

    if request.GET.get('year') and request.GET.get('month'):
        btn_y = int(request.GET.get('year'))
    else:
        btn_y = today.year

    # check_schedule = DoctorSchedule.objects.all().values('date')

    check_schedule = FizSchedule.objects.filter(date=today.strftime('%Y-%m-%d')).exists()
    if check_schedule:
        form = FizScheduleForm(request.POST)

        if request.method == 'POST':

            if not check_schedule:
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
                messages.success(request, "Terminarz Lekarza został zaktualizowany")
            else:
                # check doctor shedule - visit today
                # ch_v = DoctorSchedule.objects.filter(date=today.strftime('%Y-%m-%d')).exists()
                #
                # if ch_v:
                #     messages.error(request, "Terminarz Lekarza został już na ten miesiąc ustalony")
                # else:
                print('')

    else:
        messages.warning(request, "Nie utworzono jeszcze terminarza")
        # if schedule not save in datebase - create it
        form = FizScheduleForm(request.POST)
        if request.method == "POST":

            if form.is_valid():
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

            else:
                form = FizScheduleForm()

    return render(request, "vita/panel/fizschedule.html", {'form': form, 'date_list': date_list, 'months': months,
                                                         'today': today, 'get_days_list': get_days_list,
                                                         'btn_today': btn_today, 'btn_today_1': btn_today_1,
                                                         'btn_today_2': btn_today_2, 'btn_y': btn_y})


def patients_list(request):
    today = datetime.now()
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

    return render(request, "vita/panel/patients_list.html", {'all_patients': all_patients, 'page_obj': page_obj, 'query_count': query_count, 'today': today})


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
    today = datetime.now()
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
                directory_path = os.path.join('vita', 'media', 'patient_files')

                # create dir if not exists
                os.makedirs(directory_path, exist_ok=True)
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
                print(form.errors)
                messages.error(request, 'Nie udało się dodać plików do akt pacjenta')
        else:

            messages.error(request, 'Nie udało się dodać plików do akt pacjenta')

            form = uploadFilesForm()
    else:

        form = uploadFilesForm()


    if os.path.exists(f'vita/media/patient_files/{pk}') :
        all_files = FilesModel.objects.filter(patient_id=pk) #os.listdir(f'vita/media/patient_files/{pk}')  #
    else:
        all_files = ''
        messages.info(request, 'W aktach pacjenta nie jeszcze plików')

    #################### end upload patient files ###################################################

    #get patient visites active and cancel
    visits_akt = Visits.objects.select_related('pruposevisit').filter(patient=pk).order_by('-id').values('patient','prupose_visit__purpose_name',
                                                                                                         'prupose_visit_id',
                                                                                                         'visit',
                                                                                                         'status',
                                                                                                         'office',
                                                                                                         'time',
                                                                                                         'date')
    visits_can = Visits.objects.select_related('pruposevisit').filter(Q(patient=pk) & ~Q(status__in=[1, 2, 5])).order_by('-id').values('patient',
                                                                                                                                       'prupose_visit__purpose_name',
                                                                                                                                       'prupose_visit_id',
                                                                                                                                       'visit',
                                                                                                                                       'status',
                                                                                                                                       'office',
                                                                                                                                       'time',
                                                                                                                                       'date')

    # get patient visites fiz active and cancel
    visits_akt_f = Visits.objects.select_related('pruposevisit').filter(patient=pk).order_by('-id').values('patient',
                                                                                                         'prupose_visit__purpose_name',
                                                                                                         'prupose_visit_id',
                                                                                                         'visit',
                                                                                                         'status',
                                                                                                         'office',
                                                                                                         'time', 'date')
    visits_can_f = Visits.objects.select_related('pruposevisit').filter(
        Q(patient=pk) & ~Q(status__in=[1, 2, 5])).order_by('-id').values('patient', 'prupose_visit__purpose_name',
                                                                         'prupose_visit_id', 'visit', 'status','office', 'time',
                                                                         'date')
    # visits_count = Visits.objects.filter(patient_id=pk).count()
    # visit_f_count = Visits_f.objects.filter(patient_id=pk).count()
    # total_count = visits_count + visit_f_count

    return render(request, 'vita/panel/patient_details.html',{'patient': patient,'form': form, 'all_files':all_files,'templates': templates, 'visits_akt':visits_akt,'visits_can':visits_can, 'visits_akt_f':visits_akt_f,'visits_can_f':visits_can_f, 'today': today })

def create_patient(request):
    today = datetime.now()
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
    return render(request, 'vita/panel/create_patient.html', {'cform': cform, 'cp_form': cp_form, 'form': form, 'pp_form': pp_form, 'user_x': user_x, 'today': today })

def update_patient(request, pk):
    today = datetime.now()
    patient = Patient.objects.order_by('user__id').get(id_patient=pk)
    user = User.objects.get(id=patient.user_id)

    if 'update' in request.POST:
       if request.method == 'POST':
          form_u = UserUpdateForm(request.POST, instance=user)
          form_p = PatientUpdateExtendForm(request.POST, instance=patient)

          if form_u.is_valid() and form_p.is_valid():
              form_uu = form_u.save(commit=False)
              form_uu.first_name = request.POST['first_name']
              form_uu.last_name = request.POST['last_name']
              form_uu.email = request.POST['email']
              form_uu.username = request.POST['uname']
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
        messages.error(request, 'Dane nie zostały zapisane !')
        return redirect(f'/panel/patients/{pk}')

    return render(request, 'vita/panel/patient_details.html', {'patient':patient, 'user': user,'today': today})




def news_list(request):
    today = datetime.now()
    get_news = News.objects.order_by('-data_wpisu').values()

    if not get_news:
        messages.warning(request, 'Nie ma jeszcze żadnych dodanych aktualności')
    else:
        get_news = News.objects.order_by('-data_wpisu').values()

    return render(request, "vita/panel/news_list.html", {'get_news': get_news, 'today':today})

def create_news(request):
    today = datetime.now()
    if request.method == 'POST':
        n_form = NewsForm(request.POST)
        if n_form.is_valid():
            n_form.save()
            messages.success(request, 'Dodano nową aktualność')
            return redirect("/panel/news_list")
    else:
        n_form = NewsForm()

    context = {
        'n_form' : n_form,
        'today': today
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
    today = datetime.now()
    get_templates = NoteTemplates.objects.order_by('-created_at').values()

    if not get_templates:
        messages.warning(request, 'Nie ma jeszcze żadnych dodanych szablonów notatek')
    else:
        get_news = NoteTemplates.objects.order_by('-created_at').values()

    return render(request, "vita/panel/templates_list.html", {'get_templates': get_templates, 'today': today})
def create_templates(request):
    today = datetime.now()
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
        'form' : form,
        'today': today
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
    day_type_f = FizSchedule.objects.filter(date=date).values()

    if ( day_type.count() > 0 and day_type[0]['day_type'] == 'Pracujący'):

        for work_hours in day_type:  # work_hours result 08:00-21:00

            work_hours = work_hours['work_hours'].split('-')
            sh = work_hours[0].split(':')
            eh = work_hours[1].split(':')

        start_hour = int(sh[0])  # 8
        end_hour = int(eh[0])  # 21
        scheme = int(day_type[0]['scheme']) #30m
        start_time = datetime(1,1,1, start_hour)
        end_time = datetime(1, 1, 1, end_hour)
        h =[] #empty hour list
        # time__gte=sh[0], time__lte=eh[0],
        check_visit = Visits.objects.filter(date=get_date,office=1).select_related(
        'patient__user__pruposevisit__statusvisist').values('patient__user__first_name', 'patient__user__last_name','date', 'time','patient_id','patient__id_patient', 'prupose_visit__purpose_name', 'prupose_visit_id','visit','status')


        while start_time <= end_time:
            h.append(start_time.strftime("%H:%M"))
            start_time = start_time + timedelta(minutes=scheme)

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
        if len(check_visit) > 0:
          get_patient = User.objects.filter(id=check_visit[0]['patient_id']).values()
        else:
          get_patient = ''

        freeday = ''
    else:
        if day_type.count() == 0:
             freeday = ''
             messages.error(request, f'Na ten dzień nie został jeszcze utworzony terminarz lekarza')
        else:
            if ( day_type.count() > 0 and day_type[0]['day_type'] == 'Wolny'):
                freeday = 'Dzień wolny od pracy'
            else:
                freeday = ''

        h = ''
        visits_dict = ''
        get_patient = ''

    date_check = datetime.today()
    td = date_check.strftime('%Y-%m-%d')


    #########################################################################################################
    #########################################################################################################
    #####################################   Fizschedule  ####################################################

    if ( day_type_f.count() > 0 and day_type_f[0]['day_type'] == 'Pracujący'):

        for work_hours_f in day_type_f:  # work_hours result 08:00-21:00

            work_hours_f = work_hours_f['work_hours'].split('-')
            sh = work_hours_f[0].split(':')
            eh = work_hours_f[1].split(':')

        start_hour_f = int(sh[0])  # 8
        end_hour_f = int(eh[0])  # 21
        scheme_f = int(day_type[0]['scheme']) #30m
        start_time_f = datetime(1,1,1, start_hour_f)
        end_time_f = datetime(1, 1, 1, end_hour_f)
        hf =[] #empty hour list
        #time__gte=sh[0], time__lte=eh[0],
        check_visit_f = Visits.objects.filter(date=get_date, office=2).select_related(
        'patient__user__pruposevisit').values('patient__user__first_name', 'patient__user__last_name','date', 'time','patient_id','patient__id_patient', 'prupose_visit__purpose_name', 'prupose_visit_id','visit','status')


        while start_time_f <= end_time_f:
            hf.append(start_time_f.strftime("%H:%M"))
            start_time_f = start_time_f + timedelta(minutes=scheme_f)

        # Tworzymy pusty słownik, który będzie przechowywał pary godzina: wizyta
        visits_dict_f = {}

        # Iterujemy po liście h, która zawiera godziny pracy lekarza
        for hour_f in hf:
            # Sprawdzamy, czy godzina jest typu string, a nie słownik z danymi wizyty
            if isinstance(hour_f, str):
                # Iterujemy po liście check_visit, która zawiera dane wizyt
                for visit_f in check_visit_f:
                    # Sprawdzamy, czy godzina wizyty jest równa godzinie pracy
                    if visit_f['time'] == hour_f:
                        # Dodajemy parę godzina: wizyta do słownika
                        visits_dict_f[hour_f] = visit_f
                        # Przerywamy wewnętrzną pętlę, ponieważ znaleźliśmy pasującą wizytę
                        break
                # Jeśli nie znaleźliśmy pasującej wizyty, dodajemy parę godzina: None do słownika
                else:
                    visits_dict_f[hour_f] = None

        # Wyświetlamy słownik z godzinami i wizytami
        if len(check_visit_f) > 0:
          get_patient_f = User.objects.filter(id=check_visit_f[0]['patient_id']).values()
        else:
          get_patient_f = ''

        freeday_f = ''
    else:
        if day_type_f.count() == 0:
             freeday_f = ''
             messages.error(request, f'Na ten dzień nie został jeszcze utworzony terminarz fizkoterapii')
        else:
            if ( day_type_f.count() > 0 and day_type_f[0]['day_type'] == 'Wolny'):
                freeday_f = 'Dzień wolny od pracy'
            else:
                freeday_f = ''

        hf = ''
        visits_dict_f = ''
        get_patient_f = ''

    date_check_f = datetime.today()
    td_f = date_check_f.strftime('%Y-%m-%d')

    # information about visits www and cancel
    count_v_www = Visits.objects.filter(status=5).count()
    count_cancel = Visits.objects.filter(status=2).count()

    context = {
        'td': td,
        'td_f': td_f,
        'get_date': get_date,
        'h': h,
        'hf': hf,
        'visits': visits_dict,
        'visits_f': visits_dict_f,
        'patient_name': get_patient,
        'freeday': freeday,
        'freeday_f': freeday_f,
        'today': today,
        'count_www': count_v_www,
        'count_cancel': count_cancel
    }

    return render(request, "vita/panel/panel.html", context)

def test(request):

    return render(request, "vita/test.html")


def new_visit(request):
    today = date.today()
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]
    today.isoformat()


    return render(request, "vita/patient/new_visit.html", context={'today':today})


def appointments(request):
    if request.user.is_authenticated:
        user_id = request.user.id

        # get patient visites active and cancel
        visits_akt = Visits.objects.select_related('pruposevisit').filter(patient=user_id).order_by('-id').values(
            'patient', 'prupose_visit__purpose_name',
            'prupose_visit_id', 'visit',
            'status',
            'office',
            'time', 'date')
    else:
        return HttpResponseForbidden('Dostęp tylko dla zalogowanych użytkowników')
    return render(request, "vita/patient/appointments.html", context={'visits_akt': visits_akt})


def history(request):
    if request.user.is_authenticated:
        user_id = request.user.id

        # get patient visites active and cancel
        visits_akt = Visits.objects.select_related('pruposevisit').filter(patient=user_id).order_by('-id').values(
            'patient', 'prupose_visit__purpose_name',
            'prupose_visit_id', 'visit',
            'status',
            'office',
            'time', 'date')
        #print(visits_akt.query)
        visits_can = Visits.objects.select_related('pruposevisit').filter(
            Q(patient=user_id) & ~Q(status__in=[1, 2, 5])).order_by('-id').values('patient',
                                                                                           'prupose_visit__purpose_name',
                                                                                           'prupose_visit_id',
                                                                                           'visit',
                                                                                           'status',
                                                                                           'office',
                                                                                           'time',
                                                                                           'date')

        # get patient visites fiz active and cancel
        visits_akt_f = Visits.objects.select_related('pruposevisit').filter(patient=user_id).order_by(
            '-id').values('patient',
                          'prupose_visit__purpose_name',
                          'prupose_visit_id',
                          'visit',
                          'status',
                          'office',
                          'time', 'date')
        visits_can_f = Visits.objects.select_related('pruposevisit').filter(
            Q(patient=user_id) & ~Q(status__in=[1, 2, 5])).order_by('-id').values('patient',
                                                                                           'prupose_visit__purpose_name',
                                                                                           'prupose_visit_id', 'visit',
                                                                                           'status', 'office', 'time',
                                                                                           'date')
    else:
        return HttpResponseForbidden('Treść widowczna tylo dla zalogowanych użytkowników')

    return render(request, "vita/patient/history.html", context={'visits_akt': visits_akt})


def news(request):
    today = datetime.now()
    all_news = News.objects.order_by('-data_wpisu').filter(status=1).values()

    if not all_news:
        messages.info(request, 'W tej chwili nie opublikowano żadnych aktualności')

    return render(request, "vita/news.html", {'all_news': all_news, 'today': today})

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

    vdate = request.POST.get('date')
    vtime = request.POST.get('time')
    vo = request.POST.get('office')

    persons = User.objects.select_related('patient__user').values('patient__id','patient__user__first_name','patient__user__last_name','patient__city','patient__street',) #filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)


        # data = {"options": [str(p) for p in persons]}
        # return JsonResponse(data)

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
                c_form.email = 'stacjonarny@megavita.pl'
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


    return render(request, 'vita/panel/create_visit.html', {'cform': cform, 'cp_form': cp_form, 'form': form,'pp_form': pp_form, 'user_x': user_x,'vd': vdate, 'vt': vtime, 'vo': vo, 'persons': persons })


def create_visit_f(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    vdate_f = request.POST.get('date')
    vtime_f = request.POST.get('time')
    vo_f = request.POST.get('office')

    persons = User.objects.select_related('patient__user').values('patient__id','patient__user__first_name','patient__user__last_name','patient__city','patient__street',) #filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)


        # data = {"options": [str(p) for p in persons]}
        # return JsonResponse(data)

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
                c_form.email = 'stacjonarny@megavita.pl'
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


    return render(request, 'vita/panel/create_visit_f.html', {'cform': cform, 'cp_form': cp_form, 'form': form,'pp_form': pp_form, 'user_x': user_x,'vd_f': vdate_f, 'vt_f': vtime_f, 'vo_f': vo_f, 'persons': persons })





def create_new_visit(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    if request.method == 'POST':

        # for key, value in request.POST.items():
        #    print(f"{key}: {value}")
        cform = RegisterUserForm(request.POST)
        cp_form = PatientRegisterForm(request.POST)
        v_form = VisitForm(request.POST)

        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')[:1]  # check id_patient
        last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
        select_form = request.POST.get('select_form')

        if request.POST['sf'] == '0': # add visit with patient from autocomplete

              person = request.POST['person'].split(' ') #split data from autocomplete field
              pid = person[0] #patient_id
              print(pid)
              pln = person[1]  # patient last_name
              print(pln)
              pfn = person[2] #patient first_name
              pst = person[3] #patient street
              pc = person[4] #patient city
              check_patient = Patient.objects.filter(id_patient=pid).values() #get patient id

              if v_form.is_valid():
                  vv_form = v_form.save(commit=False)
                  vv_form.date = request.POST['date']
                  vv_form.time = request.POST['time']
                  vv_form.status = '1'
                  check_visit_nr = Visits.objects.filter(patient_id = pid).values().last()#check visist number
                  if check_visit_nr:
                      #visit_nr = int(check_visit_nr['visit']) + 1
                      visits_count = Visits.objects.filter(patient_id=pid).count()
                      visit_f_count = Visits_f.objects.filter(patient_id=pid).count()
                      total_count = visits_count + visit_f_count
                      print(total_count)
                      visit_nr = total_count + 1
                      print(visit_nr)
                  else:
                      visit_nr = '1'
                  vv_form.visit = visit_nr
                  vv_form.office = request.POST['office']
                  vv_form.prupose_visit_id = request.POST['purpose_visit']
                  vv_form.pay = '0'
                  vv_form.cancel = '0'
                  vv_form.patient_id = pid
                  vv_form.save()
              else:
                  print(cform.errors)
                  print(cp_form.errors)
                  print(v_form.errors)
        else:
                # patient data entered manually to fields
                if request.POST['sf'] == '1':

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

                    #check_username = User.objects.filter(username=c_form.username).values()  # check username

                    # if c_form != check_username:
                    #     c_form.save()
                    # else:
                    #      messages.success(request, (
                    #      f"Pacjent o takim imieniu i nazwisku jest już w naszej bazie: {request.POST.get('first_name')} {request.POST.get('last_name')} {c_form.username}"))
                    #      print('Już taki jest ')

                    if len(last_id_patient) < 1:
                        next_id_patient = 1
                    else:
                        next_id_patient = last_id_patient[0]['id_patient'] + 1

                    p_form_obj = cp_form.save(commit=False)
                    p_form_obj.user_id = last_user_id
                    p_form_obj.id_patient = next_id_patient
                    p_form_obj.save()

                    if v_form.is_valid():
                         vv_form = v_form.save(commit=False)
                         vv_form.date = request.POST['date']
                         vv_form.time = request.POST['time']
                         vv_form.status = '1'
                         vv_form.visit = '1'
                         vv_form.office = request.POST['office']
                         vv_form.prupose_visit_id = request.POST['purpose_visit']
                         last_user_id = Patient.objects.order_by('-id').values('id')[:1]  # check user_id
                         if last_user_id == '':
                             vv_form.patient_id = '1'
                         else:
                             vv_form.patient_id = last_user_id
                         vv_form.save()
                    else:
                        print(v_form.errors)
    else:
        print('')
        # cform = RegisterUserForm()
        # cp_form = PatientRegisterForm()
        # form = RegisterUserForm()
        # pp_form = PatientRegisterForm()


    return redirect(f'/panel/{request.POST["date"]}')


def create_new_visit_f(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    if request.method == 'POST':
        print(request.POST)
        # for key, value in request.POST.items():
        #    print(f"{key}: {value}")
        cform = RegisterUserForm(request.POST)
        cp_form = PatientRegisterForm(request.POST)
        v_form_f = VisitForm_f(request.POST)

        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')[:1]  # check id_patient
        last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
        select_form = request.POST.get('select_form')

        if request.POST['sf'] == '0': # add visit with patient from autocomplete

              person = request.POST['person'].split(' ') #split data from autocomplete field
              pid = person[0] #patient_id
              print(pid)
              pln = person[1] #patient last_name
              print(pln)
              pfn = person[2] #patient first_name
              pst = person[3] #patient street
              pc = person[4] #patient city
              check_patient = Patient.objects.filter(id_patient=pid).values() #get patient id

              if v_form_f.is_valid():
                  vv_form = v_form_f.save(commit=False)
                  vv_form.date = request.POST['date']
                  vv_form.time = request.POST['time']
                  vv_form.status = '1'
                  check_visit_nr_f = Visits_f.objects.filter(patient_id = pid).values().last()#check visist number

                  if check_visit_nr_f:
                      visits_count_f = Visits.objects.filter(patient_id=int(check_visit_nr_f['visit'])).count()
                      visit_f_count_f = Visits_f.objects.filter(patient_id=int(check_visit_nr_f['visit'])).count()
                      total_count_f = visits_count_f + visit_f_count_f
                      print(total_count_f)
                      visit_nr_f = total_count_f + 1
                      print(visit_nr_f)
                  else:
                      visit_nr_f = '1'

                  vv_form.visit = visit_nr_f
                  vv_form.office = request.POST['office']
                  vv_form.prupose_visit_id = request.POST['purpose_visit']
                  vv_form.pay = '0'
                  vv_form.cancel = '0'
                  vv_form.patient_id = pid
                  vv_form.save()
              else:
                  print(cform.errors)
                  print(cp_form.errors)
                  print(v_form_f.errors)
        else:
                # patient data entered manually to fields
                if request.POST['sf'] == '1':

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

                    #check_username = User.objects.filter(username=c_form.username).values()  # check username

                    # if c_form != check_username:
                    #     c_form.save()
                    # else:
                    #      messages.success(request, (
                    #      f"Pacjent o takim imieniu i nazwisku jest już w naszej bazie: {request.POST.get('first_name')} {request.POST.get('last_name')} {c_form.username}"))
                    #      print('Już taki jest ')

                    if len(last_id_patient) < 1:
                        next_id_patient = 1
                    else:
                        next_id_patient = last_id_patient[0]['id_patient'] + 1

                    p_form_obj = cp_form.save(commit=False)
                    p_form_obj.user_id = last_user_id
                    p_form_obj.id_patient = next_id_patient
                    p_form_obj.save()

                    if v_form_f.is_valid():
                         vv_form = v_form_f.save(commit=False)
                         vv_form.date = request.POST['date']
                         vv_form.time = request.POST['time']
                         vv_form.status = '1'
                         vv_form.visit = '1'
                         vv_form.office = request.POST['office']
                         vv_form.prupose_visit_id = request.POST['purpose_visit']
                         last_user_id = Patient.objects.order_by('-id').values('id')[:1]  # check user_id
                         if last_user_id == '':
                             vv_form.patient_id = '1'
                         else:
                             vv_form.patient_id = last_user_id
                         vv_form.save()
                    else:
                        print(v_form_f.errors)
    else:
        print('')
        # cform = RegisterUserForm()
        # cp_form = PatientRegisterForm()
        # form = RegisterUserForm()
        # pp_form = PatientRegisterForm()


    return redirect(f'/panel/{request.POST["date"]}')


def pause_visit(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')
    vform = VisitForm(request.POST)
    if request.method == 'POST':

        form = vform.save(commit=False)
        form.date = request.POST['date']
        form.time = request.POST['time']
        form.status = '0'
        form.visit = '0'
        form.office = request.POST['office']
        form.prupose_visit_id = '5'
        if request.user.username == 'lekarz':
            form.patient_id = request.user.id
        form.save()
    else:
        print(vform.errors)
        print('')

    return redirect(f'/panel/{request.POST["date"]}')





def calendar_view(request, year=None, month=None):
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month
    # get the calendar for the given year and month
    cal = calendar.monthcalendar(year, month)
    # create a list of links for each day
    links = []
    for week in cal:
        week_links = []
        for day in week:
            if day == 0:
                # if the day is 0, it means it is outside the current month
                week_links.append('')
            else:
                print('')
                # otherwise, create a link to the day view with the date as parameter
                #link = reverse(day, args=[year, month, day])
                #week_links.append(link)
        links.append(week_links)
    # render the calendar template with the links
    return render(request, 'calendar.html', {'cal': cal, 'links': links})

def day_view(request, year, month, day):
    # get the date from the parameters
    date = datetime(year, month, day)
    # do something with the date, e.g. display events or details
    # ...
    # render the day template with the date
    return render(request, 'day.html', {'date': date})

def doctor_visits(request, offset=0, num_days=14):

    today = datetime.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset * 2)
    days_of_week = [week_start + timedelta(days=i) for i in range(num_days)]

    schedule_table = []
    time_slots = []

    start_time = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=8)
    end_time = datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=21)

    while start_time <= end_time:
        time_str = start_time.strftime("%H:%M")
        time_slots.append({
            'time': time_str,
            'header': start_time.strftime("%H:%M")
        })
        start_time += timedelta(minutes=30)

    for i in range(0, num_days, 7):
        week_schedule = []
        for j in range(7):
            day = days_of_week[i + j]
            day_schedule = {
                'date': day,
                'schedule': []
            }

            for time_slot in time_slots:
                has_visit = Visits.objects.filter(date=day, time=time_slot['time']).exists()
                day_schedule['schedule'].append({
                    'time': time_slot['time'],
                    'header': time_slot['header'],
                    'has_visit': has_visit
                })

            week_schedule.append(day_schedule)

        schedule_table.append(week_schedule)

    available_slots = [
        (f"{day_schedule['date']} {time_slot['time']}", f"{day_schedule['date']} {time_slot['time']}")
        for week_schedule in schedule_table
        for day_schedule in week_schedule
        for time_slot in day_schedule['schedule']
        if not time_slot['has_visit']
    ]
    if request.method == 'POST':
        form = DoctorVisitsForm(request.POST)
        print('post')
        print(request.POST)

        if form.is_valid():
            for sel in request.POST.getlist('sel_visit'):
                sel_visit = sel.split(' ')

                # Sprawdzenie, czy wizyta już istnieje w bazie danych
                existing_visit = Visits.objects.filter(date=sel_visit[0], time=sel_visit[1], patient_id='5').first()

                if existing_visit is None:
                    # Wizyta nie istnieje, więc możemy ją dodać
                    s_form = Visits(date=sel_visit[0], time=sel_visit[1], status='1', visit='1', office='1',pay='0',
                                    cancel='0', prupose_visit_id='1', patient_id=request.user.id)
                    s_form.save()
                    messages.success(request, (
                        f"Dodano nową wizytę w dniu: {sel_visit[0]} o godzinie {sel_visit[1]} "))
                else:
                    messages.warning(request, (
                        f"Wizyta o dacie: {sel_visit[0]} i godzinie {sel_visit[1]} jest już dodana: "))

            return redirect('/patient/appointments')
        else:
            print("Formularz nie jest poprawny:", form.errors)
    else:
        form = DoctorVisitsForm()

    context = {
        'schedule_table': schedule_table,
        'time_slots': time_slots,
        'visits': Visits.objects.all(),
        'current_week_offset': offset,
        'form': form,
        'today': today
    }

    return render(request, 'vita/patient/doctor_visits.html', context)
