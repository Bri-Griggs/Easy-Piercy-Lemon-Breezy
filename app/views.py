from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Order, Appointment
from .forms import CreateUserForm
from datetime import datetime, timedelta

def home(request):
    return render(request, 'home.html')

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {user}')
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('adminOnly')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('adminOnly')
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('login')

def BookApp(request):
    weekdays = validWeekday(22)
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        if not service:
            messages.success(request, "Please Select A Service!")
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

        if service:
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
                        (request, "Please Select A Service!")

    return render(request, 'time.html', {
        'times': hour,
    })

def userApp(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'appointments.html', {
        'user': user,
        'appointments': appointments,
    })

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def adminOnly(request):
    appointments = Appointment.objects.all().order_by('day', 'time')
    return render(request, 'adminOnly.html', {'appointments': appointments})

@login_required
@user_passes_test(is_admin)
def deleteAppointment(request, id):
    appointment = get_object_or_404(Appointment, pk=id)
    
    if request.method == 'POST':
        appointment.delete()
        return redirect('adminOnly')

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
    appointment = get_object_or_404(Appointment, pk=id)
    userSelectedTime = appointment.time

    error_message = None
    if request.method == 'POST':
        new_time = request.POST.get("time")
        date = dayToWeekday(day)

        if service:
            if minDate <= day <= maxDate:
                if date != 'Sunday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=new_time).exists():
                            error_message = "This time is already selected. Please choose a different time."
                        elif userSelectedTime != new_time:
                            appointment.time = new_time
                            appointment.save()
                            return redirect('appointments')
                        else:
                            error_message = "This time is already your current appointment time."

    return render(request, 'userUpdate.html', {
        'times': hour,
        'id': id,
        'error_message': error_message,
    })

def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

def validWeekday(days):
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


def fileNotFound(request):
    return render(request, 'filenotfound.html')
