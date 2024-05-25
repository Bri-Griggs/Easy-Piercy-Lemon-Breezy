from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.http.request import HttpRequest
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm
from django.contrib import messages
# from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.decorators import login_required, user_passes_test

# from .filters import OrderFilter

def home(request):
    return render(request, 'home.html')
# @unauthenticated_user

def registerPage(request):
    form =CreateUserForm()

    if request.method == 'POST':
        form =CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for' + user)
            return redirect('login')

    context ={'form':form}
    return render(request, 'register.html', context)

def loginPage(request):
    if request.user.is_staff:
        return redirect('adminOnly')
    
    if request.user.is_authenticated:
        return redirect('booking')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if request.user.is_staff:
            return redirect('adminOnly')
        
        if user is not None:
            login(request, user)
            return redirect('booking')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')

def BookApp(request):
    weekdays = validWeekday(22)

    
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        if service is None:
            return redirect('booking')

        
        request.session['day'] = day
        request.session['service'] = service

        return redirect('time')

    return render(request, 'booking.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
    })

def timeApp(request):
    user = request.user
    times = [
        "3 PM", "3:30 PM", "4 PM", "4:30 PM", "5 PM", "5:30 PM", "6 PM", "6:30 PM", "7 PM", "7:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    maxDate = deltatime.strftime('%Y-%m-%d')

    
    day = request.session.get('day')
    service = request.session.get('service')

    
    hour = checkTime(times, day)
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service is not None:
            if minDate <= day <= maxDate:
                if date != 'Sunday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            Appointment.objects.get_or_create(
                                user=user,
                                service=service,
                                day=day,
                                time=time,
                            )
                            return redirect('appointments')
        

    return render(request, 'time.html', {
        'times': hour,
    })

def userApp(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'appointments.html', {
        'user':user,
        'appointments':appointments,
    })
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def adminAppointments(request):
    if request.user!= None and not request.user.is_staff:
        return redirect('home')
    appointments = Appointment.objects.all().order_by('day', 'time')
    return render(request, 'adminOnly.html', {'appointments': appointments})
    

def deleteAppointment(request, id):
    appointment = get_object_or_404(Appointment, pk=id)
    
    if request.method == 'POST':
        appointment.delete()
        return redirect('delete')

    return render(request, 'delete.html', {'appointment': appointment})

def userUpdateSubmit(request, id):
    user = request.user
    times = [
        "3 PM", "3:30 PM", "4 PM", "4:30 PM", "5 PM", "5:30 PM", "6 PM", "6:30 PM", "7 PM", "7:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    maxDate = deltatime.strftime('%Y-%m-%d')

    day = request.session.get('day')
    service = request.session.get('service')

    
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service is not None:
            if minDate <= day <= maxDate:
                if date != 'Sunday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            Appointment.objects.filter(pk=id).update(
                                user=user,
                                service=service,
                                day=day,
                                time=time,
                            )

        return redirect('appointments')

    return render(request, 'userUpdate.html', {
        'times': hour,
        'id': id,
    })

def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

def validWeekday(days):
    # Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range(days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y != 'Sunday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays
    
def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays

def checkTime(times, day):
    x = []
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1:
            x.append(k)
    return x

def checkEditTime(times, day, id):
    x = []
    appointment = Appointment.objects.get(pk=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x