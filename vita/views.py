import calendar
import datetime
import logging
import os
import random
from calendar import monthrange
from datetime import date, datetime, timedelta

from django import template
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from pyvit import settings
from .forms import RegisterUserForm, UserUpdateForm, PatientRegisterForm, \
    DoctorsScheduleForm, FizScheduleForm, NewsForm, NoteTemplatesForm, uploadFilesForm, PatientUpdateExtendForm, \
    VisitForm, DoctorVisitsForm, ReserveForm, FizVisitsForm
from .models import News, Patient, DoctorSchedule, FizSchedule, NoteTemplates, FilesModel, Visits, ReversList, \
    StatusVisit, Visits_No

register = template.Library()


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'vita/patient/password_reset.html'
    email_template_name = 'vita/patient/password_reset_email.html'
    subject_template_name = 'vita/patient/password_reset_subject'
    success_message = "Wysłaliśmy Ci instrukcje dotyczące ustawienia hasła, " \
                      "jeśli istnieje konto z podanym przez Ciebie adresem e-mail, powinieneś je otrzymać wkrótce. " \
                      " Jeśli nie otrzymasz e-maila, " \
                      "upewnij się, że wpisałeś adres, którym został podany przyt rejestracji konta, i sprawdź folder spam."
    success_url = '/login/'


def home(request):
    today_date = datetime.now().date()
    context = {
        'today': today_date,
    }
    return render(request, "vita/home.html", context)


def docschedule(request):
    today = datetime.now()

    def months():
        return {
            '1': 'Styczeń', '2': 'Luty', '3': 'Marzec', '4': 'Kwiecień', '5': 'Maj', '6': 'Czerwiec',
            '7': 'Lipiec', '8': 'Sierpień', '9': 'Wrzesień', '10': 'Październik', '11': 'Listopad', '12': 'Grudzień'
        }

    def days_of_month_list():
        if request.GET.get('year') and request.GET.get('month'):
            y = int(request.GET.get('year'))  # Rzutujemy na int
            m = int(request.GET.get('month'))  # Rzutujemy na int
        else:
            y = today.year
            m = today.month

        day_names_polish = [
            "poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"
        ]
        date_list = {}
        for d in range(1, monthrange(y, m)[1] + 1):
            x = '{:04d}-{:02d}-{:02d}'.format(y, m, d)
            dayName = datetime.strptime(x, '%Y-%m-%d').weekday()
            day_name_polish = day_names_polish[dayName].capitalize()
            date_list[x] = day_name_polish

        return date_list

    def get_days_of_month_list(year, month):
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, monthrange(year, month)[1])
        return list(DoctorSchedule.objects.filter(date__range=[start_date, end_date]).values())

    btn_today = today.year
    btn_today_1 = today.year + 1
    btn_today_2 = today.year + 2

    if request.GET.get('year') and request.GET.get('month'):
        btn_y = int(request.GET.get('year'))  # Rzutujemy na int
    else:
        btn_y = today.year

    date_list = days_of_month_list()

    get_days_list = get_days_of_month_list(btn_y, int(request.GET.get('month', today.month)))  # Rzutujemy na int

    if request.method == 'POST':
        form = DoctorsScheduleForm(request.POST)
        if form.is_valid():
            data_l = request.POST.getlist('data')
            day_type_l = request.POST.getlist('day_type')
            work_hours_l = request.POST.getlist('work_hours_start')
            scheme_l = request.POST.getlist('scheme')
            official_hours_l = request.POST.getlist('official_hours_start')

            for date, day_type, work_hours, official_hours, scheme in zip(data_l, day_type_l, work_hours_l,
                                                                          official_hours_l, scheme_l):
                schedule, created = DoctorSchedule.objects.update_or_create(
                    date=date,
                    defaults={'day_type': day_type, 'work_hours': work_hours, 'official_hours': official_hours,
                              'scheme': scheme}
                )
            messages.success(request, "Terminarz Lekarza został zaktualizowany")
    else:
        form = DoctorsScheduleForm()

    return render(request, "vita/panel/docschedule.html", {
        'form': form, 'date_list': date_list, 'months': months, 'today': today, 'get_days_list': get_days_list,
        'btn_today': btn_today, 'btn_today_1': btn_today_1, 'btn_today_2': btn_today_2, 'btn_y': btn_y
    })


def fizschedule(request):
    today = datetime.now()

    def months():
        return {
            '1': 'Styczeń', '2': 'Luty', '3': 'Marzec', '4': 'Kwiecień', '5': 'Maj', '6': 'Czerwiec',
            '7': 'Lipiec', '8': 'Sierpień', '9': 'Wrzesień', '10': 'Październik', '11': 'Listopad', '12': 'Grudzień'
        }

    def days_of_month_list():
        if request.GET.get('year') and request.GET.get('month'):
            y = int(request.GET.get('year'))  # Rzutujemy na int
            m = int(request.GET.get('month'))  # Rzutujemy na int
        else:
            y = today.year
            m = today.month

        day_names_polish = [
            "poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"
        ]
        date_list = {}
        for d in range(1, monthrange(y, m)[1] + 1):
            x = '{:04d}-{:02d}-{:02d}'.format(y, m, d)
            dayName = datetime.strptime(x, '%Y-%m-%d').weekday()
            day_name_polish = day_names_polish[dayName].capitalize()
            date_list[x] = day_name_polish

        return date_list

    def get_days_of_month_list(year, month):
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, monthrange(year, month)[1])
        return list(FizSchedule.objects.filter(date__range=[start_date, end_date]).values())

    btn_today = today.year
    btn_today_1 = today.year + 1
    btn_today_2 = today.year + 2

    if request.GET.get('year') and request.GET.get('month'):
        btn_y = int(request.GET.get('year'))
    else:
        btn_y = today.year

    date_list = days_of_month_list()

    get_days_list = get_days_of_month_list(btn_y, int(request.GET.get('month', today.month)))

    if request.method == 'POST':
        form = FizScheduleForm(request.POST)
        if form.is_valid():
            print(request)
            data_l = request.POST.getlist('data')
            day_type_l = request.POST.getlist('day_type')
            work_hours_l = request.POST.getlist('work_hours_start')
            scheme_l = request.POST.getlist('scheme')
            official_hours_l = request.POST.getlist('official_hours_start')

            for date, day_type, work_hours, official_hours, scheme in zip(data_l, day_type_l, work_hours_l,
                                                                          official_hours_l, scheme_l):
                schedule, created = FizSchedule.objects.update_or_create(
                    date=date,
                    defaults={'day_type': day_type, 'work_hours': work_hours, 'official_hours': official_hours,
                              'scheme': scheme}
                )
            messages.success(request, "Terminarz Fizykoterapii został zaktualizowany")
    else:
        form = FizScheduleForm()

    return render(request, "vita/panel/fizschedule.html", {
        'form': form, 'date_list': date_list, 'months': months, 'today': today, 'get_days_list': get_days_list,
        'btn_today': btn_today, 'btn_today_1': btn_today_1, 'btn_today_2': btn_today_2, 'btn_y': btn_y
    })


def patients_list(request):
    today = datetime.now()
    # get all records from Patient with data form User where user_id
    all_patients = Patient.objects.order_by('user__last_name')

    query = request.GET.get('q')
    if query:
        # show all record from query
        all_patients = Patient.objects.filter(
            Q(street__icontains=query) | Q(city__icontains=query) |
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        ).distinct()

        # query count
        query_count = Patient.objects.filter(
            Q(street__icontains=query) | Q(city__icontains=query) |
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        ).distinct().count()

        # pagination
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

    return render(request, "vita/panel/patients_list.html",
                  {'all_patients': all_patients, 'page_obj': page_obj, 'query_count': query_count, 'today': today})


def delete_patient_files(request, pk):
    patient = Patient.objects.order_by('user__id').get(id_patient=pk)
    path = os.path.join(f'vita/media/patient_files/{pk}/{request.POST.get("file")}')
    file_name = os.path.join(f'patient_files/{pk}/{request.POST.get("file")}')

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

    if os.path.exists(f'vita/media/patient_files/{pk}'):
        all_files = FilesModel.objects.filter(patient_id=pk)  # os.listdir(f'vita/media/patient_files/{pk}')  #
    else:
        all_files = ''
        messages.info(request, 'W aktach pacjenta nie jeszcze plików')

    #################### end upload patient files ###################################################
    user_id = patient
    # get patient visites active and cancel

    visits_akt = Visits.objects.select_related('purposevisit', 'status').filter(
        patient=user_id,
        status__id__in=[1,3,5]  # Dostosuj te nazwy statusów do swojej bazy danych
    ).order_by(
        '-id'
    ).values(
        'patient',
        'purpose_visit__purpose_name',
        'purpose_visit_id',
        'visit',
        'status__status_name',
        'office',
        'time',
        'date'
    )

    visits_can = Visits_No.objects.select_related('purposevisit', 'status').filter(
        Q(patient=user_id) & ~Q(status__in=[1, 3, 5])).order_by('-id').values('patient',
                                                                              'purpose_visit__purpose_name',
                                                                              'purpose_visit_id',
                                                                              'visit',
                                                                              'status__status_name',
                                                                              'office',
                                                                              'time',
                                                                              'date')

    return render(request, 'vita/panel/patient_details.html',
                  {'patient': patient, 'form': form, 'all_files': all_files, 'templates': templates,
                   'visits_akt': visits_akt, 'visits_can': visits_can, 'today': today})


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
    return render(request, 'vita/panel/create_patient.html',
                  {'cform': cform, 'cp_form': cp_form, 'form': form, 'pp_form': pp_form, 'user_x': user_x,
                   'today': today})


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
                form_uu.username = request.POST['username']
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
                # print(connection.queries)
                messages.success(request, 'Dane zostały zapisane')
                return redirect(f'/panel/patients/{pk}')
            else:
                print(form_u.errors)
        else:
            print('not request')
    else:
        messages.error(request, 'Dane nie zostały zapisane !')
        return redirect(f'/panel/patients/{pk}')

    return render(request, 'vita/panel/patient_details.html', {'patient': patient, 'user': user, 'today': today})


def news_list(request):
    today = datetime.now()
    get_news = News.objects.order_by('-data_wpisu').values()

    if not get_news:
        messages.warning(request, 'Nie ma jeszcze żadnych dodanych aktualności')
    else:
        get_news = News.objects.order_by('-data_wpisu').values()

    return render(request, "vita/panel/news_list.html", {'get_news': get_news, 'today': today})


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
        'n_form': n_form,
        'today': today
    }
    return render(request, "vita/panel/create_news.html", context)


def edit_news(request, pk):
    news = get_object_or_404(News, id_news=pk)
    return render(request, "vita/panel/edit_news.html", {'news': news})


def update_news(request, pk):
    obj = get_object_or_404(News, id_news=pk)
    if request.method == 'POST':
        n_form = NewsForm(request.POST, instance=obj)
        if n_form.is_valid():
            n_form.save()
            messages.success(request, 'Dane zapisano')
            return redirect("/panel/news_list")
    else:
        n_form = NewsForm(instance=obj)

    context = {
        'n_form': n_form
    }

    return render(request, "vita/panel/create_news.html", context)


def delete_news(request, pk):
    news = News.objects.get(id_news=pk)

    if request.method == "GET":
        news.delete()
        messages.info(request, f'News o temacie: "{news.temat}" z dnia {news.data_wpisu} usunięto!')
        return redirect('/panel/news_list')
    else:
        messages.error(request, 'Nie udało się usunąć aktualności')
    context = {
        'news': news
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
        'form': form,
        'today': today
    }

    return render(request, "vita/panel/create_templates.html", context)


def edit_templates(request, pk):
    templates = get_object_or_404(NoteTemplates, id=pk)
    return render(request, "vita/panel/edit_templates.html", {'templates': templates})


def update_templates(request, pk):
    obj = get_object_or_404(NoteTemplates, id=pk)
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
        'form': form
    }

    return render(request, "vita/panel/create_templates.html", context)


def delete_templates(request, pk):
    templates = NoteTemplates.objects.get(id=pk)

    if request.method == "GET":
        templates.delete()
        messages.info(request, f'Szablon notatki o nazwie: "{templates.name}" usunięto!')
        return redirect('/panel/templates_list')
    else:
        messages.error(request, 'Nie udało się usunąć szablonu notatki')
    context = {
        'templates': templates
    }

    return render(request, "vita/panel/templates_list.html", context)


def update_visit_status(request, visit_id):
    visit = get_object_or_404(Visits, id=visit_id)

    if request.method == 'POST':
        if 'status' in request.POST and 'visit_id' in request.POST:
            new_status_id = int(request.POST.get('status'))
            visit_id = request.POST.get('visit_id')

            if new_status_id in [2, 4]:
                visit_no = Visits_No.objects.create(
                    id=visit.id,
                    patient=visit.patient,
                    date=visit.date,
                    time=visit.time,
                    cancel=1,
                    office=visit.office,
                    purpose_visit_id=visit.purpose_visit_id,
                    status_id=new_status_id
                )
                visit.delete()  # Usunięcie wizyty z tabeli Visits
                if new_status_id == 2:
                    status_name = 'Odwołana'
                elif new_status_id == 4:
                    status_name = 'Nie odbyła się'
                messages.success(request, f'Wizyta została przeniesiona do tabeli wizyty odwołane jako {status_name}.')
            else:
                # Aktualizacja statusu wizyty
                visit.status_id = new_status_id
                visit.save()
                messages.success(request, 'Status wizyty został zaktualizowany.')

            return redirect('panel', date=visit.date)

        elif 'status_f' in request.POST and 'visit_id_f' in request.POST:
            new_status_id_f = int(request.POST.get('status_f'))
            visit_id_f = request.POST.get('visit_id_f')

            if new_status_id_f in [2, 4]:
                visit_f = get_object_or_404(Visits, id=visit_id_f)
                visit_no = Visits_No.objects.create(
                    id=visit_f.id,
                    patient=visit_f.patient,
                    date=visit_f.date,
                    time=visit_f.time,
                    cancel=1,
                    office=visit_f.office,
                    purpose_visit_id=visit_f.purpose_visit_id,
                    status_id=new_status_id_f
                )
                visit_f.delete()  # Usunięcie wizyty z tabeli Visits
                if new_status_id_f == 2:
                    status_name = 'Odwołana'
                elif new_status_id_f == 4:
                    status_name = 'Nie odbyła się'
                messages.success(request, f'Wizyta została przeniesiona do tabeli wizyty odwołane jako {status_name}.')
            else:
                # Aktualizacja statusu wizyty
                visit_f = get_object_or_404(Visits, id=visit_id_f)
                visit_f.status_id = new_status_id_f
                visit_f.save()
                messages.success(request, 'Status wizyty został zaktualizowany.')

            return redirect('panel', date=visit_f.date)

    return render(request, 'vita/panel/panel.html', {'visit': visit})

def delete_visit(request, visit_id):
    visit = get_object_or_404(Visits, id=visit_id)

    if request.method == 'POST':
        visit.delete()
        messages.success(request, 'Wizyta została usunięta.')
        return redirect('panel', date=visit.date)

    context = {
        'visit': visit,
    }
    return render(request, 'vita/panel/panel.html', context)


def panel(request, date):
    today = datetime.today()
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]
    get_date = current_path.replace('/', '')

    day_type = DoctorSchedule.objects.filter(date=date).values()
    day_type_f = FizSchedule.objects.filter(date=date).values()

    if day_type.exists() and day_type[0]['day_type'] == 'Pracujący':
        work_hours = day_type[0]['work_hours'].split('-')
        sh = work_hours[0].split(':')
        eh = work_hours[1].split(':')
        start_hour = int(sh[0])
        end_hour = int(eh[0])
        scheme = int(day_type[0]['scheme'])

        start_time = datetime(1, 1, 1, start_hour)
        end_time = datetime(1, 1, 1, end_hour)
        h = []  # empty hour list

        check_visit = Visits.objects.filter(date=get_date, office=1).select_related(
            'patient__user__purposevisit__statusvisist'
        ).values(
            'patient__user__first_name', 'patient__user__last_name', 'date', 'time', 'patient_id',
            'patient__id_patient',
            'purpose_visit__purpose_name', 'purpose_visit_id', 'visit', 'status', 'id'
        )

        while start_time <= end_time:
            h.append(start_time.strftime("%H:%M"))
            start_time += timedelta(minutes=scheme)  # Poprawne wykorzystanie wartości scheme

        # Tworzenie słownika wizyt
        visits_dict = {hour: next((visit for visit in check_visit if visit['time'] == hour), None) for hour in h}

        if check_visit.exists():
            get_patient = User.objects.filter(id=check_visit[0]['patient_id']).values()
        else:
            get_patient = ''

        freeday = ''
    else:
        freeday = '' if day_type.exists() else 'Na ten dzień nie został jeszcze utworzony terminarz lekarza'
        if day_type.exists() and day_type[0]['day_type'] == 'Wolny':
            freeday = 'Dzień wolny od pracy'
        h, visits_dict, get_patient = '', '', ''

    date_check = datetime.today()
    td = date_check.strftime('%Y-%m-%d')

    #########################################################################################################
    #########################################################################################################
    #####################################   Fizschedule  ####################################################

    if day_type_f.exists() and day_type_f[0]['day_type'] == 'Pracujący':
        work_hours_f = day_type_f[0]['work_hours'].split('-')
        sh = work_hours_f[0].split(':')
        eh = work_hours_f[1].split(':')
        start_hour_f = int(sh[0])
        end_hour_f = int(eh[0])
        scheme_f = int(day_type_f[0]['scheme'])

        start_time_f = datetime(1, 1, 1, start_hour_f)
        end_time_f = datetime(1, 1, 1, end_hour_f)
        hf = []  # empty hour list

        check_visit_f = Visits.objects.filter(date=get_date, office=2).select_related(
            'patient__user__purposevisit'
        ).values(
            'patient__user__first_name', 'patient__user__last_name', 'date', 'time', 'patient_id',
            'patient__id_patient',
            'purpose_visit__purpose_name', 'purpose_visit_id', 'visit', 'status', 'id'
        )

        while start_time_f <= end_time_f:
            hf.append(start_time_f.strftime("%H:%M"))
            start_time_f += timedelta(minutes=scheme_f)  # Poprawne wykorzystanie wartości scheme_f

        # Tworzenie słownika wizyt dla fizykoterapii
        visits_dict_f = {hour_f: next((visit_f for visit_f in check_visit_f if visit_f['time'] == hour_f), None) for
                         hour_f in hf}

        if check_visit_f.exists():
            get_patient_f = User.objects.filter(id=check_visit_f[0]['patient_id']).values()
        else:
            get_patient_f = ''
        freeday_f = ''
    else:
        freeday_f = '' if day_type_f.exists() else 'Na ten dzień nie został jeszcze utworzony terminarz fizykoterapii'
        if day_type_f.exists() and day_type_f[0]['day_type'] == 'Wolny':
            freeday_f = 'Dzień wolny od pracy'
        hf, visits_dict_f, get_patient_f = '', '', ''

    date_check_f = datetime.today()
    td_f = date_check_f.strftime('%Y-%m-%d')

    def get_visits_with_patient_data():
        all_visits_www = Visits.objects.filter(status=5).select_related('patient__user').order_by('-date')[:5]
        visits_data = [{
            'visit_id': visit.id,
            'status': visit.status,
            'date': visit.date,
            'time': visit.time,
            'patient_id': visit.patient_id,
            'patient_first_name': visit.patient.user.first_name,
            'patient_last_name': visit.patient.user.last_name,
        } for visit in all_visits_www]
        return visits_data

    all_visits_www = get_visits_with_patient_data()
    status_visits = StatusVisit.objects.filter(~Q(id=0))

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
        'all_visits_www': all_visits_www,
        'status_visit': status_visits
    }

    return render(request, "vita/panel/panel.html", context)


def test(request):
    return render(request, "vita/test.html")


def new_visit(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        today = date.today()
        full_path = request.get_full_path()
        current_path = full_path[full_path.index('/', 1):]
        today.isoformat()
    else:
        return HttpResponseForbidden('Treść widowczna tylo dla zalogowanych użytkowników')

    return render(request, "vita/patient/new_visit.html", context={'today': today})


@login_required()
def appointments(request):
    user_id = request.user.id
    visits_akt = Visits.objects.filter(patient=user_id,status__in=[1, 5]).order_by('date', 'time')  # Przykładowy queryset

    counter = 0
    for visit in visits_akt:
        if visit.status in [1, 5]:
            counter += 1
            visit.lp_number = counter

    context = {
        'visits_akt': visits_akt,
    }

    return render(request, 'vita/patient/appointments.html', context)


@login_required
def cancel_appointment(request, visit_id):
    if request.method == 'POST' and 'visit_id' in request.POST:
        post_visit_id = request.POST['visit_id']

        if post_visit_id == str(visit_id):
            visit = get_object_or_404(Visits, id=visit_id)
            Visits_No.objects.create(
                id=visit.id,
                patient=visit.patient,
                date=visit.date,
                time=visit.time,
                cancel=1,
                office=visit.office,
                purpose_visit_id=visit.purpose_visit_id,
                status_id=6  # Zmiana statusu na 6
            )
            visit.delete()  # Usunięcie wizyty z tabeli Visits
            messages.success(request, 'Wizyta została odwołana.')
        else:
            messages.error(request, 'Nieprawidłowy ID wizyty.')
    else:
        messages.error(request, 'Brak ID wizyty w żądaniu.')

    return redirect('appointments')


@login_required
def history(request):
    if request.user.is_authenticated:
        user_id = request.user.id

        visits_akt_list = Visits.objects.select_related('purposevisit', 'status').filter(
            patient=user_id,
            status__id__in=[3]
        ).order_by('-id').values(
            'patient',
            'purpose_visit__purpose_name',
            'purpose_visit_id',
            'visit',
            'status__status_name',
            'office',
            'time',
            'date'
        )

        visits_can_list = Visits_No.objects.select_related('purposevisit', 'status').filter(
            Q(patient=user_id) & ~Q(status__in=[1, 3, 5])
        ).order_by('-id').values(
            'patient',
            'purpose_visit__purpose_name',
            'purpose_visit_id',
            'visit',
            'status__status_name',
            'office',
            'time',
            'date'
        )

        items_per_page_akt = request.GET.get('items_per_page_akt', 10)
        items_per_page_can = request.GET.get('items_per_page_can', 10)

        try:
            items_per_page_akt = int(items_per_page_akt)
        except ValueError:
            items_per_page_akt = 10

        try:
            items_per_page_can = int(items_per_page_can)
        except ValueError:
            items_per_page_can = 10

        akt_page = request.GET.get('akt_page', 1)
        can_page = request.GET.get('can_page', 1)

        try:
            akt_page = int(akt_page)
        except ValueError:
            akt_page = 1

        try:
            can_page = int(can_page)
        except ValueError:
            can_page = 1

        paginator_akt = Paginator(visits_akt_list, items_per_page_akt)
        paginator_can = Paginator(visits_can_list, items_per_page_can)

        try:
            visits_akt = paginator_akt.page(akt_page)
        except PageNotAnInteger:
            visits_akt = paginator_akt.page(1)
        except EmptyPage:
            visits_akt = paginator_akt.page(paginator_akt.num_pages)

        try:
            visits_can = paginator_can.page(can_page)
        except PageNotAnInteger:
            visits_can = paginator_can.page(1)
        except EmptyPage:
            visits_can = paginator_can.page(paginator_can.num_pages)

    else:
        return HttpResponseForbidden('Treść widoczna tylko dla zalogowanych użytkowników')

    context = {
        'visits_akt': visits_akt,
        'visits_can': visits_can,
        'items_per_page_akt': items_per_page_akt,
        'items_per_page_can': items_per_page_can,
    }

    return render(request, "vita/patient/history.html", context)


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
                if 'remember_me' in request.POST and request.POST['remember_me']:
                    request.session.set_expiry(settings.REMEMBER_ME_DURATION)

                    if username == 'admin':
                        return redirect("/admin")
                    elif username == 'lekarz':
                        return redirect(f'/panel/{today}')
                    else:
                        return redirect("/")
                else:
                    request.session.set_expiry(0)
                return redirect('/')

            else:
                messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
        else:
            messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
    form = AuthenticationForm()

    return render(request, "vita/login.html", {"login_form": form})

logger = logging.getLogger(__name__)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'vita/patient/password_change_form.html'

    def get_success_url(self):
        # Możesz tu określić dowolny URL, na który użytkownik zostanie przekierowany po zmianie hasła
        return reverse('password_change_done')

class PasswordChangeDoneView(TemplateView):
    template_name = 'vita/patient/password_change_done.html'

def logout_request(request):
    logout(request)
    messages.info(request, "Zostałeś poprawnie wylogowany.")
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
    today_date = datetime.now().date()

    context = {
        'u_form': u_form,
        'pe_form': pe_form,
        'today' : today_date
    }

    return render(request, 'vita/patient/profile.html', context)


def contact(request):
    if request.method == 'POST':
        contact = User(request.POST)
        context = {
            'contact': contact
        }

    return redirect('/news', request, context)


def create_visit(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]

    get_date = current_path.replace('/', '')

    vdate = request.POST.get('date')
    vtime = request.POST.get('time')
    vo = request.POST.get('office')

    persons = User.objects.select_related('patient__user').values('patient__id', 'patient__user__first_name',
                                                                  'patient__user__last_name', 'patient__city',
                                                                  'patient__street', )  # filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)

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

    return render(request, 'vita/panel/create_visit.html',
                  {'cform': cform, 'cp_form': cp_form, 'form': form, 'pp_form': pp_form, 'user_x': user_x, 'vd': vdate,
                   'vt': vtime, 'vo': vo, 'persons': persons})

def create_new_visit(request):
    full_path = request.get_full_path()
    current_path = full_path[full_path.index('/', 1):]
    get_date = current_path.replace('/', '')

    if request.method == 'POST':
        cform = RegisterUserForm(request.POST)
        cp_form = PatientRegisterForm(request.POST)
        v_form = VisitForm(request.POST)

        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')[:1]  # check id_patient
        last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
        select_form = request.POST.get('select_form')

        if request.POST['sf'] == '0':  # add visit with patient from autocomplete
            person = request.POST['person'].split(' ')  # split data from autocomplete field
            pid = person[0] if person else None  # patient_id

            if not pid:
                # Return an error message if patient ID is empty
                return render(request, 'vita/panel/create_visit.html', {
                    'cform': cform, 'cp_form': cp_form, 'v_form': v_form,
                    'error_message': 'Proszę wybrać pacjenta z bazy danych.'
                })

            check_patient = Patient.objects.filter(id_patient=pid).values()  # get patient id

            if v_form.is_valid():
                vv_form = v_form.save(commit=False)
                vv_form.date = request.POST['date']
                vv_form.time = request.POST['time']
                vv_form.status_id = 1
                check_visit_nr = Visits.objects.filter(patient_id=pid).values().last()  # check visist number
                if check_visit_nr:
                    visits_count = Visits.objects.filter(patient_id=pid).count()
                    visit_f_count = Visits.objects.filter(patient_id=pid).count()
                    total_count = visits_count + visit_f_count
                    visit_nr = total_count + 1
                else:
                    visit_nr = '1'
                vv_form.visit = visit_nr
                vv_form.office = request.POST['office']
                vv_form.purpose_visit_id = request.POST['purpose_visit']
                vv_form.pay = '0'
                vv_form.cancel = '0'
                vv_form.patient_id = pid

                # Check for existing visit collision
                existing_visit = Visits.objects.filter(
                    Q(date=request.POST['date']) & Q(time=request.POST['time']) & ~Q(office=request.POST['office']) & Q(
                        patient_id=pid)
                ).first()

                if existing_visit:
                    existing_visit_data = {
                        'date': existing_visit.date,
                        'time': existing_visit.time,
                        'office': existing_visit.office,
                        'patient_name': f"{existing_visit.patient.user.first_name} {existing_visit.patient.user.last_name}"
                    }
                    return render(request, 'vita/panel/create_visit.html', {
                        'cform': cform, 'cp_form': cp_form, 'v_form': v_form, 'existing_visit_data': existing_visit_data
                    })

                vv_form.save()
            else:
                print(cform.errors)
                print(cp_form.errors)
                print(v_form.errors)
        else:
            # patient data entered manually to fields
            if request.POST['sf'] == '1':
                c_form = cform.save(commit=False)
                first_name = str(request.POST.get('first_name')).capitalize()
                last_name = str(request.POST.get('last_name')).capitalize()
                c_form.first_name = first_name
                c_form.last_name = last_name
                c_form.username = f'stacjonarny{random.sample(range(999), 1)[0]}'
                c_form.password = make_password(BaseUserManager().make_random_password())
                c_form.email = 'stacjonarny@megavita.pl'
                c_form.save()

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
                    vv_form.status_id = 1
                    vv_form.visit = '1'
                    vv_form.office = request.POST['office']
                    vv_form.purpose_visit_id = request.POST['purpose_visit']

                    # Check for existing visit collision
                    existing_visit = Visits.objects.filter(
                        Q(date=request.POST['date']) & Q(time=request.POST['time']) & ~Q(
                            office=request.POST['office']) & Q(patient_id=next_id_patient)
                    ).first()

                    if existing_visit:
                        existing_visit_data = {
                            'date': existing_visit.date,
                            'time': existing_visit.time,
                            'office': existing_visit.office,
                            'patient_name': f"{existing_visit.patient.user.first_name} {existing_visit.patient.user.last_name}"
                        }
                        return render(request, 'vita/panel/create_visit.html', {
                            'cform': cform, 'cp_form': cp_form, 'v_form': v_form,
                            'existing_visit_data': existing_visit_data
                        })

                    vv_form.patient_id = next_id_patient
                    vv_form.save()
                else:
                    print(v_form.errors)
    else:
        print("Wystąpił problem z przetwarzaniem danych formularza, bład w linii 1268 views.py")

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
        form.status_id = 0
        form.visit = '0'
        form.office = request.POST['office']
        form.purpose_visit_id = '5'
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


@login_required()
def doctor_visits(request, offset=0, num_days=14):
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset * 2)
    days_of_week = []

    for i in range(num_days):
        current_day = week_start + timedelta(days=i)
        if current_day.weekday() < 5 and current_day >= today and DoctorSchedule.objects.filter(
                date=current_day).exists():
            days_of_week.append(current_day)

    schedule_table = []

    for i in range(0, num_days, 7):
        week_schedule = []
        for j in range(7):
            if i + j < len(days_of_week):
                day = days_of_week[i + j]
                day_schedule = {
                    'date': day,
                    'schedule': []
                }

                # Pobierz godziny pracy z FizSchedule dla danego dnia
                fiz_schedule = DoctorSchedule.objects.get(date=day)

                try:
                    # Przetwórz godziny pracy w polu work_hours
                    work_hours_str = fiz_schedule.work_hours
                    start_time_str, end_time_str = work_hours_str.split('-')
                    start_time = datetime.strptime(start_time_str, '%H:%M')
                    end_time = datetime.strptime(end_time_str, '%H:%M')

                    current_time = start_time
                    while current_time <= end_time:
                        time_str = current_time.strftime("%H:%M")
                        has_visit = Visits.objects.filter(date=day, time=time_str, office='1').exists()
                        day_schedule['schedule'].append({
                            'time': time_str,
                            'header': current_time.strftime("%H:%M"),
                            'has_visit': has_visit
                        })
                        current_time += timedelta(minutes=30)

                except ValueError as e:
                    messages.error(request, f"Błąd podczas przetwarzania godzin pracy dla dnia {day}: {e}")

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
        form = FizVisitsForm(request.POST)

        if form.is_valid():
            for sel in request.POST.getlist('sel_visit'):
                sel_visit = sel.split(' ')

                existing_visit = Visits.objects.filter(date=sel_visit[0], time=sel_visit[1], patient_id=request.user.id,
                                                       office='2').first()
                existing_schedule = DoctorSchedule.objects.filter(date=sel_visit[0]).first()

                if existing_schedule is None:
                    messages.warning(request, f"Na dzień: {sel_visit[0]} nie został jeszcze ustalony terminarz ")
                else:
                    if existing_visit is None:
                        status_visit = StatusVisit.objects.get(status_name='www')
                        s_form = Visits(date=sel_visit[0], time=sel_visit[1], status=status_visit, visit='1',
                                        office='1',
                                        pay='0', cancel='0', purpose_visit_id='2', patient_id=request.user.id)
                        s_form.save()
                        messages.success(request,
                                         f"Dodano nową wizytę w dniu: {sel_visit[0]} o godzinie {sel_visit[1]} ")
                    else:
                        messages.warning(request,
                                         f"Wizyta o dacie: {sel_visit[0]} i godzinie {sel_visit[1]} jest już dodana ")

            return redirect('/patient/appointments')
        else:
            print("Formularz nie jest poprawny:", form.errors)
    else:
        form = DoctorVisitsForm()

    day_type = DoctorSchedule.objects.all().values()

    context = {
        'schedule_table': schedule_table,
        'visits': Visits.objects.filter(office='1'),  # Filtruj wizyty dla fizykoterapii
        'current_week_offset': offset,
        'form': form,
        'today': today,
        'day_type': day_type
    }

    return render(request, 'vita/patient/doctor_visits.html', context)


@login_required()
def fiz_visits(request, offset=0, num_days=14):
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset * 2)
    days_of_week = []

    for i in range(num_days):
        current_day = week_start + timedelta(days=i)
        if current_day.weekday() < 5 and current_day >= today and FizSchedule.objects.filter(date=current_day).exists():
            days_of_week.append(current_day)

    schedule_table = []

    for i in range(0, num_days, 7):
        week_schedule = []
        for j in range(7):
            if i + j < len(days_of_week):
                day = days_of_week[i + j]
                day_schedule = {
                    'date': day,
                    'schedule': []
                }

                # Pobierz godziny pracy z FizSchedule dla danego dnia
                fiz_schedule = FizSchedule.objects.get(date=day)

                try:
                    # Przetwórz godziny pracy w polu work_hours
                    work_hours_str = fiz_schedule.work_hours
                    start_time_str, end_time_str = work_hours_str.split('-')
                    start_time = datetime.strptime(start_time_str, '%H:%M')
                    end_time = datetime.strptime(end_time_str, '%H:%M')

                    current_time = start_time
                    while current_time <= end_time:
                        time_str = current_time.strftime("%H:%M")
                        has_visit = Visits.objects.filter(date=day, time=time_str, office='2').exists()
                        day_schedule['schedule'].append({
                            'time': time_str,
                            'header': current_time.strftime("%H:%M"),
                            'has_visit': has_visit
                        })
                        current_time += timedelta(minutes=30)

                except ValueError as e:
                    messages.error(request, f"Błąd podczas przetwarzania godzin pracy dla dnia {day}: {e}")

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
        form = FizVisitsForm(request.POST)

        if form.is_valid():
            for sel in request.POST.getlist('sel_visit'):
                sel_visit = sel.split(' ')

                existing_visit = Visits.objects.filter(date=sel_visit[0], time=sel_visit[1], patient_id=request.user.id,
                                                       office='2').first()
                existing_schedule = FizSchedule.objects.filter(date=sel_visit[0]).first()

                if existing_schedule is None:
                    messages.warning(request, f"Na dzień: {sel_visit[0]} nie został jeszcze ustalony terminarz ")
                else:
                    if existing_visit is None:

                        status_visit = StatusVisit.objects.get(status_name='www')
                        s_form = Visits(date=sel_visit[0], time=sel_visit[1], status=status_visit, visit='1',
                                        office='2',
                                        pay='0', cancel='0', purpose_visit_id='2', patient_id=request.user.id)
                        s_form.save()
                        messages.success(request,
                                         f"Dodano nową wizytę w dniu: {sel_visit[0]} o godzinie {sel_visit[1]} ")
                    else:
                        messages.warning(request,
                                         f"Wizyta o dacie: {sel_visit[0]} i godzinie {sel_visit[1]} jest już dodana ")

            return redirect('/patient/appointments')
        else:
            print("Formularz nie jest poprawny:", form.errors)
    else:
        form = FizVisitsForm()

    day_type = FizSchedule.objects.all().values()

    context = {
        'schedule_table': schedule_table,
        'visits': Visits.objects.filter(office='2'),  # Filtruj wizyty dla fizykoterapii
        'current_week_offset': offset,
        'form': form,
        'today': today,
        'day_type': day_type
    }

    return render(request, 'vita/patient/fiz_visits.html', context)


def reserve_list(request):
    is_empty = not ReversList.objects.exists()

    if is_empty:
        messages.warning(request, 'Nie dodano jeszcze żadnego pacjenta do listy rezerwowej')
        full_list = []
    else:
        full_list = ReversList.objects.select_related('patient__user').all()

    context = {
        'full_list': full_list
    }
    return render(request, 'vita/panel/reserve_list.html', context)


def create_reserve_list(request):
    get_all = ReversList.objects.all().exists()
    # patient_ids = get_all[0]['patient_id']
    # get_patient = Patient.objects.filter(id_patient=patient_ids).values()
    # get_user = User.objects.filter(id=patient_ids).values()
    # get_visit = Visits.objects.filter(patient_id=patient_ids).values().count()
    persons = User.objects.select_related('patient__user').values('patient__id', 'patient__user__first_name',
                                                                  'patient__user__last_name', 'patient__city',
                                                                  'patient__street', )  # filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)

    # check_visist_reserve = ReversList.objects.filter(date=request.POST['date']).values()

    if get_all:
        print('')
        # print(get_user[0]['first_name'], get_user[0]['last_name'], get_visit)
    else:
        messages.warning(request, 'Nie dodano jeszcze żadnego pacjenta do listy rezerwowej')

    if request.method == 'POST':
        cform = RegisterUserForm(request.POST)
        cp_form = PatientRegisterForm(request.POST)
        v_form = ReserveForm(request.POST)

        last_id_patient = Patient.objects.order_by('-id_patient').values('id_patient')[:1]  # check id_patient
        last_user_id = User.objects.order_by('-id').values('id')[:1]  # check user_id
        select_form = request.POST.get('select_form')

        if request.POST['sf'] == '0':  # add visit with patient from autocomplete

            print('sf')
            person = request.POST['person'].split(' ')  # split data from autocomplete field
            pid = person[0]  # patient_id
            print(pid)
            pln = person[1]  # patient last_name
            print(pln)
            pfn = person[2]  # patient first_name
            pst = person[3]  # patient street
            pc = person[4]  # patient city
            check_patient = Patient.objects.filter(id_patient=pid).values()  # get patient id

            if v_form.is_valid():
                vv_form = v_form.save(commit=False)
                vv_form.date = request.POST['date']
                vv_form.time = request.POST['time']
                vv_form.status_name = request.POST['priority']
                vv_form.call = '0'
                vv_form.phone = '0'
                vv_form.description = 'brak'
                check_visit_nr = ReversList.objects.filter(patient_id=pid).values().last()  # check visist number

                if check_visit_nr:
                    visits_count = Visits.objects.filter(patient_id=int(check_visit_nr['visit'])).count()
                    total_count = visits_count
                    print(total_count)
                    visit_nr = total_count + 1
                    print(visit_nr)
                else:
                    visit_nr = '1'

                vv_form.visit = visit_nr
                vv_form.office = request.POST['office']
                vv_form.patient_id = pid
                vv_form.save()
                messages.success(request, 'Dodano  pacjenta do listy rezerwowej')
                return redirect('/panel/reserve_list')
            else:
                print(v_form.errors)

        else:
            # patient data entered manually to fields
            if request.POST['sf'] == '1':
                print('sf1')
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

                if len(last_id_patient) < 1:
                    next_id_patient = 1
                else:
                    next_id_patient = last_id_patient[0]['id_patient'] + 1

                p_form_obj = cp_form.save(commit=False)
                p_form_obj.user_id = last_user_id
                p_form_obj.id_patient = next_id_patient
                p_form_obj.save()

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
                    vv_form.status_name = request.POST['priority']
                    vv_form.call = '0'
                    vv_form.phone = '0'
                    vv_form.description = 'brak'
                    vv_form.visit = '1'
                    vv_form.office = request.POST['office']
                    last_user_id = Patient.objects.order_by('-id').values('id')[:1]  # check user_id
                    if last_user_id == '':
                        vv_form.patient_id = '1'
                    else:
                        vv_form.patient_id = last_user_id
                    vv_form.save()
                    messages.success(request, 'Dodano  pacjenta do listy rezerwowej')
                    return redirect('/panel/reserve_list')
                else:
                    print(v_form.errors)

    else:
        cform = RegisterUserForm()
        cp_form = PatientRegisterForm()
        v_form = ReserveForm()

    today = date.today()
    today.strftime('%Y-%m-%d')
    x = f'stacjonarny{random.sample(range(999), 1)[0]}'
    user_x = x

    context = {
        'cform': cform,
        'cp_form': cp_form,
        'persons': persons,
        'today': today,
        'user_x': user_x
    }
    return render(request, 'vita/panel/create_reserve_list.html', context)


def show_all_temporary_visits(request):
    temporary_visits = Visits.objects.all()
    print(temporary_visits)

    context = {

    }
    return render(request, 'vita/panel/temporaray_visits.html', context)


def doctors_weekly_plan(request, offset=0, num_days=7):
    offset = int(offset)  # Ensure offset is an integer
    today = date.today()
    start_date = today + timedelta(days=offset * num_days)
    end_date = start_date + timedelta(days=num_days - 1)
    td = datetime.today().strftime('%Y-%m-%d')

    context = {
        'td': td,
        'start_date': start_date,
        'end_date': end_date,
        'week_days': [],
        'current_week_offset': offset,  # Add this to context
        'today': today,
    }

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime('%A')

        if day_name in ['Saturday', 'Sunday']:
            continue

        day_type = DoctorSchedule.objects.filter(date=current_date).first()

        if day_type is None:
            messages.error(request, f'Na {current_date} nie został jeszcze utworzony terminarz lekarza',
                           extra_tags='ds')
            continue

        if day_type.day_type == 'Wolny':
            continue

        try:
            work_hours = day_type.work_hours.split('-')
            start_time = datetime.strptime(work_hours[0], '%H:%M')
            end_time = datetime.strptime(work_hours[1], '%H:%M')
            end_time += timedelta(minutes=1)  # Add one minute to include 21:00
        except (ValueError, IndexError) as e:
            messages.error(request, f'Nieprawidłowy format godzin pracy dla {current_date}: {day_type.work_hours}',
                           extra_tags='ds')
            continue

        scheme = int(day_type.scheme)

        h = []
        current_time = start_time
        while current_time <= end_time:
            h.append(current_time.strftime('%H:%M'))
            current_time += timedelta(minutes=scheme)

        visits_dict = {}
        visits = Visits.objects.filter(date=current_date, office=1).select_related('patient__user').order_by('time')
        for hour in h:
            matching_visit = visits.filter(time=hour).first()
            if matching_visit:
                visits_dict[hour] = {
                    'patient_first_name': matching_visit.patient.user.first_name,
                    'patient_last_name': matching_visit.patient.user.last_name,
                    'purpose_visit': matching_visit.purpose_visit.purpose_name,
                    'status': matching_visit.status,
                    'id_patient': matching_visit.patient.id_patient,
                }
            else:
                visits_dict[hour] = None

        context['week_days'].append({
            'date': current_date,
            'day_name': day_name,
            'h': h,
            'visits': visits_dict,
        })

    return render(request, 'vita/panel/doctors_weekly_plan.html', context)


def fiz_weekly_plan(request, offset=0, num_days=7):
    offset = int(offset)  # Ensure offset is an integer
    today = date.today()
    start_date = today + timedelta(days=offset * num_days)
    end_date = start_date + timedelta(days=num_days - 1)
    td = datetime.today().strftime('%Y-%m-%d')

    context = {
        'td': td,
        'start_date': start_date,
        'end_date': end_date,
        'week_days': [],
        'current_week_offset': offset,  # Add this to context
        'today': today,
    }

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime('%A')

        if day_name in ['Saturday', 'Sunday']:
            continue

        day_type = FizSchedule.objects.filter(date=current_date).first()

        if day_type is None:
            messages.error(request, f'Na {current_date} nie został jeszcze utworzony terminarz lekarza',
                           extra_tags='ds')
            continue

        if day_type.day_type == 'Wolny':
            continue

        try:
            work_hours = day_type.work_hours.split('-')
            start_time = datetime.strptime(work_hours[0], '%H:%M')
            end_time = datetime.strptime(work_hours[1], '%H:%M')
            end_time += timedelta(minutes=1)  # Add one minute to include 21:00
        except (ValueError, IndexError) as e:
            messages.error(request, f'Nieprawidłowy format godzin pracy dla {current_date}: {day_type.work_hours}',
                           extra_tags='ds')
            continue

        scheme = int(day_type.scheme)

        h = []
        current_time = start_time
        while current_time <= end_time:
            h.append(current_time.strftime('%H:%M'))
            current_time += timedelta(minutes=scheme)

        visits_dict = {}
        visits = Visits.objects.filter(date=current_date, office=2).select_related('patient__user').order_by('time')
        for hour in h:
            matching_visit = visits.filter(time=hour).first()
            if matching_visit:
                visits_dict[hour] = {
                    'patient_first_name': matching_visit.patient.user.first_name,
                    'patient_last_name': matching_visit.patient.user.last_name,
                    'purpose_visit': matching_visit.purpose_visit.purpose_name,
                    'status': matching_visit.status,
                    'id_patient': matching_visit.patient_id,
                }
            else:
                visits_dict[hour] = None
        print(scheme)
        context['week_days'].append({
            'date': current_date,
            'day_name': day_name,
            'h': h,
            'visits': visits_dict,
        })
    return render(request, 'vita/panel/fiz_weekly_plan.html', context)


def get_available_doc(start_date, end_date):
    available_slots = []

    current_date = start_date
    while current_date <= end_date:
        day_name = current_date.strftime('%A')

        if day_name in ['Saturday', 'Sunday']:
            current_date += timedelta(days=1)
            continue

        day_type = DoctorSchedule.objects.filter(date=current_date).first()

        if day_type is None or day_type.day_type == 'Wolny':
            current_date += timedelta(days=1)
            continue

        try:
            work_hours = day_type.work_hours.split('-')
            start_time = datetime.strptime(work_hours[0], '%H:%M')
            end_time = datetime.strptime(work_hours[1], '%H:%M')
            end_time += timedelta(minutes=1)  # Include the end hour
        except (ValueError, IndexError):
            current_date += timedelta(days=1)
            continue

        scheme = int(day_type.scheme)

        current_time = start_time
        while current_time <= end_time:
            visit_time = current_time.strftime('%H:%M')
            if not Visits.objects.filter(date=current_date, time=visit_time, office=1).exists():
                available_slots.append({
                    'date': current_date,
                    'time': visit_time,
                })
                if len(available_slots) == 10:
                    return available_slots
            current_time += timedelta(minutes=scheme)

        current_date += timedelta(days=1)

    return available_slots


def get_available_fiz(start_date, end_date):
    available_slots_f = []

    current_date = start_date
    while current_date <= end_date:
        day_name = current_date.strftime('%A')

        if day_name in ['Saturday', 'Sunday']:
            current_date += timedelta(days=1)
            continue

        day_type = FizSchedule.objects.filter(date=current_date).first()

        if day_type is None or day_type.day_type == 'Wolny':
            current_date += timedelta(days=1)
            continue

        try:
            work_hours = day_type.work_hours.split('-')
            start_time = datetime.strptime(work_hours[0], '%H:%M')
            end_time = datetime.strptime(work_hours[1], '%H:%M')
            end_time += timedelta(minutes=1)  # Include the end hour
        except (ValueError, IndexError):
            current_date += timedelta(days=1)
            continue

        scheme = int(day_type.scheme)

        current_time = start_time
        while current_time <= end_time:
            visit_time = current_time.strftime('%H:%M')
            if not Visits.objects.filter(date=current_date, time=visit_time, office=2).exists():
                available_slots_f.append({
                    'date': current_date,
                    'time': visit_time,
                })
                if len(available_slots_f) == 10:
                    return available_slots_f
            current_time += timedelta(minutes=scheme)

        current_date += timedelta(days=1)

    return available_slots_f


def upcoming_appointments(request):
    today = datetime.today().date()
    end_date = today + timedelta(days=30)  # Arbitrary end date for searching available slots

    available_slots = get_available_doc(today, end_date)
    available_slots_f = get_available_fiz(today, end_date)

    # Debugging: Print available slots to console
    print("Available Slots:", available_slots)
    # Debugging: Print available slots to console
    print("Available Slots_F:", available_slots_f)

    context = {
        'available_slots': available_slots,
        'available_slots_f': available_slots_f,
    }

    return render(request, 'vita/upcoming_appointments.html', context)
