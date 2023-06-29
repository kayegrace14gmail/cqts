from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, Farmer, Batch, Cooperative, Exporter
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from CQTS import settings
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse


today = date.today()
start_of_day = datetime.combine(today, datetime.min.time())
end_of_day = datetime.combine(today, datetime.max.time())

# Create your views here.
def home(request):
    return render(request, 'base/home.html')


@login_required(login_url='cooperative-login')
def cooperativeHome(request):
    # period = request.GET.get('period') if request.GET.get('period') != None else 'Today'
    # if period == 'Today':
    #     start_of_day = datetime.combine(today, datetime.min.time())
    #     end_of_day = datetime.combine(today, datetime.max.time())
    #     accepted_batches = Batch.objects.filter(cooperative = request.user, is_approved = True, created_at__range=(start_of_day, end_of_day)).count()
    #     rejected_batches = Batch.objects.filter(cooperative = request.user, is_approved = False, created_at__range=(start_of_day, end_of_day)).count()
    
    # elif period == 'Week':
    #     start_of_week = today - timedelta(days=today.weekday())
    #     end_of_week = start_of_week + timedelta(days=6)
    #     accepted_batches = Batch.objects.filter(cooperative = request.user, is_approved = True, created_at__range=(start_of_week, end_of_week)).count()
    #     rejected_batches = Batch.objects.filter(cooperative = request.user, is_approved = False, created_at__range=(start_of_week, end_of_week)).count()
          
    # elif period == 'Month':
    #     pass
    farmers = Farmer.objects.filter(cooperative = request.user).count()
    accepted_batches = Batch.objects.filter(cooperative = request.user, is_approved = True).count()
    rejected_batches = Batch.objects.filter(cooperative = request.user, is_approved = False).count()
    
    context = {'accepted_batches': accepted_batches,
                'rejected_batches': rejected_batches,
                'farmers': farmers, }
    return render(request, 'base/cooperative/cooperative-home.html', context)

def cooperativeLogin(request):
    if request.user.is_authenticated:
        return redirect('cooperative-home')

    if request.method == 'POST':
       email =  request.POST.get('email').lower()
       password = request.POST.get('password')

       
        #check if user belongs to cooperative group---> if not, redirect to login page
       try:
            user = User.objects.get(email = email)
            group = user.group.name
            
       except:
            messages.error(request, "Email or password is incorrect.")
            return redirect('cooperative-login')
       
       if group != 'Cooperative':
        messages.error(request, "Not a cooperative Account.")
        return redirect('cooperative-login')

       user = authenticate(request, email=email, password=password)
           
       if user is not None:
            login(request, user)
            return redirect('cooperative-home')
       else: 
            messages.error(request, "Email or password is incorrect.")

    context = {}
    return render(request, 'base/cooperative/cooperative-login.html', context)

@login_required(login_url='cooperative-login')
def farmerRegistration(request):
    if request.method == 'POST':
        name = request.POST.get('farmerName')
        phone = request.POST.get('phone')
        operation_scale = request.POST.get('scale')
        location = request.POST.get('location')
        Farmer.objects.create(
            name = name,
            phone = phone,
            operation_scale = operation_scale,
            cooperative = request.user,
            location = location,
        )
        messages.success(request, "Farmer registered successfully.")
        return redirect('cooperative-manage-farmers')
    return render(request, 'base/cooperative/cooperative-farmer-registration.html') 

@login_required(login_url='cooperative-login')
def farmerUpdate(request, pk):
    farmer = Farmer.objects.get(id=pk)
    context = {
        'farmer' : farmer
    }

    if request.method == 'POST':
        name = request.POST.get('farmerName')
        phone = request.POST.get('phone')
        operation_scale = request.POST.get('scale')
        location = request.POST.get('location')
        farmer.name = name
        farmer.phone = phone
        farmer.operation_scale = operation_scale
        farmer.location = location
        farmer.save()
        messages.success(request, "Farmer updated successfully.")
        return redirect('cooperative-manage-farmers')
    return render(request, 'base/cooperative/cooperative-farmer-registration.html', context)
    
@login_required(login_url='cooperative-login')
def farmerDeletion(request, pk):
    farmer = Farmer.objects.get(id=pk)
    if request.method == 'POST':
        farmer.delete()
        messages.success(request, "Farmer deleted successfully.")
        return redirect('cooperative-manage-farmers')
    return render(request, 'base/delete.html', {'obj' :farmer})

@login_required(login_url='cooperative-login') 
def cooperativeFarmersView(request):
    farmers = Farmer.objects.filter(cooperative = request.user)
    context = {'farmers':farmers}
    return render(request, 'base/cooperative/cooperative-manage-farmers.html', context)

@login_required(login_url='cooperative-login')
def cooperativeLogout(request):
    logout(request)
    return redirect('cooperative-login')


#admnin views
@login_required(login_url='admin-login')
def adminHome(request):
    farmers = Farmer.objects.all()
    cooperatives = User.objects.filter(group_id__name = 'Cooperative')
    exporters = User.objects.filter(group_id__name = 'Exporter')
    context = {
        'farmers' : farmers,
        'cooperatives' :  cooperatives,
        'exporters' : exporters,
    }
    return render(request, 'base/admin/admin-home.html', context)

#Login admin
def adminLogin(request):
    if request.user.is_authenticated:
        return redirect('admin-home')

    if request.method == 'POST':
       email =  request.POST.get('email').lower()
       password = request.POST.get('password')
       
        #check if user belongs to admin group---> if not, redirect to login page
       try:
            user = User.objects.get(email = email)
            group  = user.group.name
       except:
            messages.error(request, "Email or password is incorrect.")
            return redirect('admin-login')
       
       if group != 'CQTSadmin':
        messages.error(request, "Not admin Account.")
        return redirect('admin-login')

       user = authenticate(request, email=email, password=password)
           
       if user is not None:
            login(request, user)
            return redirect('admin-home')
       else: 
            messages.error(request, "Email or password is incorrect.")

    context = {}
    return render(request, 'base/admin/admin-login.html', context)


def adminCooperativesRegistration(request):
    if request.method == 'POST':
        coperative_name = request.POST.get('cooperative_name')
        location = request.POST.get('location')
        cooperative_head = request.POST.get('cooperative_head')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        password = User.objects.make_random_password()

        hashed_password = make_password(password)

        try:
            cooperative = User.objects.create(
            name = coperative_name,
            phone = phone,
            location = location,
            password = hashed_password,
            email = email,
        )
        except:
            messages.error(request, "Cooperative email already exists.")
            return redirect('admin-cooperative-registration')
        #add user to cooperative group
        group = Group.objects.get(name='Cooperative')
        group.group_user.add(cooperative)

        #add cooperative_head to cooperative table
        details = Cooperative.objects.create(
            cooperative_head = cooperative_head,
        )

        cooperative.cooperative_details.add(details)

        #send email to cooperative
        send_email('cooperative',coperative_name, email, password)
        messages.success(request, "Cooperative registered successfully and email sent.")
        return redirect('admin-manage-cooperatives')
    return render(request, 'base/admin/admin-cooperative-registration.html')

def adminCooperativesView(request):
    Cooperatives = User.objects.filter(group__name='Cooperative')
    context = {'Cooperatives': Cooperatives}
    return render(request, 'base/admin/admin-manage-cooperatives.html', context)

def adminExportersView(request):
    Exporters = Exporter.objects.all()
    context = {'Exporters': Exporters}
    return render(request, 'base/admin/admin-manage-exporters.html', context)
   

def adminLogout(request):
    logout(request)
    return redirect('admin-login')

@login_required(login_url='admin-login')
def cooperativeDeletion(request, pk):
    cooperative = User.objects.get(id=pk)
    if request.method == 'POST':
        cooperative.delete()
        messages.success(request, "Cooperative deleted successfully.")
        return redirect('admin-manage-cooperatives')
    return render(request, 'base/admin-delete.html', {'obj' :cooperative})

def adminExportersRegistration(request):
    if request.method == 'POST':
        exporter_name = request.POST.get('exporter_name')
        location = request.POST.get('district')
        license = request.POST.get('license_no')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        password = User.objects.make_random_password()

        hashed_password = make_password(password)

        try:
            exporter = User.objects.create(
            name = exporter_name,
            phone = phone,
            location = location,
            password = hashed_password,
            email = email,
        )
        except:
            messages.error(request, "Email already exists.")
            return redirect('admin-exporter-registration')
        #add user to cooperative group
        group = Group.objects.get(name='Exporter')
        group.group_user.add(exporter)

        #add cooperative_head to cooperative table
        details = Exporter.objects.create(
            license = license,
        )

        exporter.exporter_details.add(details)

        #send email to cooperative
        send_email('exporter', exporter_name, email, password)
        messages.success(request, "Cooperative registered successfully and email sent.")
        return redirect('admin-manage-exporters')
    return render(request, 'base/admin/admin-exporter-registration.html')





#email sending
def send_email(account_type, name, email, password):
    subject = 'Welcome to the CQTS Platform'
    recipient_list = [email]  # Replace with the recipient's email address
    
    # Render the HTML template
    context = {
        'type' : account_type,
        'name': name,  
        'email': email,
        'password': password
    }
    html_message = render_to_string('base/registration/account_registration_email_template.html', context)
    
    # Create the plain text version of the message
    plain_message = strip_tags(html_message)
    
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, recipient_list, html_message=html_message)
    return None