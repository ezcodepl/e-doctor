from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserCreationForm, RegisterUserForm, PatientUpdateForm
from .models import News, Patient
from django.contrib.auth.models import User
import datetime

# Create your views here.


def home(request):
    return render(request, "vita/home.html")


def news(request):
    all_news = News.objects.all().order_by('-data_wpisu').values()

    return render(request, "vita/news.html", {'all_news': all_news})


def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('home')
    else:
        form = RegisterUserForm()

    return render(request, 'vita/register.html', {
        'form': form,
    })


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if username == 'admin':
                    return redirect("/admin")
                else:
                    return redirect("/")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "vita/login.html", {"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("/")


def profile(request):
    patients = Patient.objects.all().values()

    if request.method == "POST":
        form = PatientUpdateForm(request.POST)
        user = request.user
        #form = PatientUpdateForm(request.POST, instance=user)
        first = request.POST['first_name']
        username = request.POST['username']
        first_name = request.POST['first_name']

        patient_user_id = Patient.objects.values_list('user')

        for p in patient_user_id:
            if user.id == p[0]:
                pu_id = p[0]

            if form.is_valid():

                form.save()

    return render(request, "vita/patient/profile.html", {'patients': patients})

def update_profile(request):
    print('kurwa nie dziala')

    context = {}
    #
    # # fetch the object related to passed id
    user_id = request.user.id
    print(user_id)
    #obj = get_object_or_404(Patient, id=user_id)
    #
    # # pass the object as instance in form
    form = PatientUpdateForm(request.POST or None)
    #
    # # save the data from the form and
    # # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect("/patient/profile")
    #
    # # add form dictionary to context
    context["form"] = form
    #
    # return render(request, "vita/patient/update.html", context)
    return render(request, "vita/patient/update.html", context)