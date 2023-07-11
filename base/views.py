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
import requests
from bs4 import BeautifulSoup


today = date.today()
start_of_day = datetime.combine(today, datetime.min.time())
end_of_day = datetime.combine(today, datetime.max.time())

# Create your views here.


def home(request):
    return render(request, 'base/home.html')


@login_required(login_url='cooperative-login')
def cooperativeHome(request):
    # fetching prices from the web
    url = 'https://ugandacoffee.go.ug/'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all divs with class 'price-table'
        price_table = soup.find_all('div', {'class': 'price-table'})

        prices = {}

        if price_table:
            # Find all divs with class 'tab-row'
            for table in price_table:
                tab_rows = table.find_all('div', {'class': 'tab-row'})
                for tab_row in tab_rows:
                    label = tab_row.find(
                        'div', {'class': 'lable'}).text.strip()
                    price = tab_row.find(
                        'div', {'class': 'price-data'}).text.strip()
                    prices[label] = price
        # Print the prices
        # print("Type: US Cents/Lb")
        # for key, value in prices.items():
        #     if key == "Kiboko":
        #         print("Type: Shillings/Kg")
        #     print(f"{key}: {value}")
    cooperative_details = Cooperative.objects.get(cooperative=request.user)
    farmers = Farmer.objects.filter(cooperative=request.user)
    total_batches = Batch.objects.filter(cooperative=request.user)

    accepted_batches = Batch.objects.filter(
        cooperative=request.user, is_approved=True)

    rejected_batches = Batch.objects.filter(
        cooperative=request.user, is_approved=False)

    exporter_accepted_batches = Batch.objects.filter(
        cooperative=request.user, is_approved=True, sold_to_exporter=True)

    buyer_accepted_batches = Batch.objects.filter(
        cooperative=request.user, is_approved=True, sold_to_buyer=True)
    
    exporter_acceptance_percentage = ((exporter_accepted_batches.count()/accepted_batches.count()) * 100)
    exporter_acceptance_percentage = round(exporter_acceptance_percentage, 2)
    
    buyer_acceptance_percentage = ((buyer_accepted_batches.count()/total_batches.count()) * 100)
    buyer_acceptance_percentage = round(buyer_acceptance_percentage, 2)

    
    context = {
        'farmers': farmers,
        'total_batches': total_batches,
        'accepted_batches': accepted_batches,
        'rejected_batches': rejected_batches,
        'exporter_accepted_batches': exporter_accepted_batches,
        'buyer_accepted_batches': buyer_accepted_batches,
        'exporter_acceptance_percentage': exporter_acceptance_percentage,
        'buyer_acceptance_percentage': buyer_acceptance_percentage,
        'notification_batches':total_batches[0:4],
        'prices': prices,
        'cooperative_details': cooperative_details
    }

    return render(request, 'base/cooperative/cooperative-home.html', context)


def cooperativeLogin(request):
    if request.user.is_authenticated:
        return redirect('cooperative-home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # check if user belongs to cooperative group---> if not, redirect to login page
        try:
            user = User.objects.get(email=email)
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
def cooperativeBatchView(request):
    batches = Batch.objects.filter(cooperative=request.user)
    context = {'batches': batches}
    return render(request, 'base/cooperative/cooperative-view-batches.html', context)


@login_required(login_url='cooperative-login')
def farmerRegistration(request):
    if request.method == 'POST':
        name = request.POST.get('farmerName')
        phone = request.POST.get('phone')
        operation_scale = request.POST.get('scale')
        location = request.POST.get('location')
        Farmer.objects.create(
            name=name,
            phone=phone,
            operation_scale=operation_scale,
            cooperative=request.user,
            location=location,
        )
        messages.success(request, "Farmer registered successfully.")
        return redirect('cooperative-manage-farmers')
    return render(request, 'base/cooperative/cooperative-farmer-registration.html')


@login_required(login_url='cooperative-login')
def farmerUpdate(request, pk):
    farmer = Farmer.objects.get(id=pk)
    context = {
        'farmer': farmer
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
    return render(request, 'base/delete.html', {'obj': farmer})


@login_required(login_url='cooperative-login')
def cooperativeFarmersView(request):
    farmers = Farmer.objects.filter(cooperative=request.user)
    context = {'farmers': farmers}
    return render(request, 'base/cooperative/cooperative-manage-farmers.html', context)


@login_required(login_url='cooperative-login')
def cooperativeLogout(request):
    logout(request)
    return redirect('cooperative-login')


# admnin views
@login_required(login_url='admin-login')
def adminHome(request):
    farmers = Farmer.objects.all().count()
    cooperatives = User.objects.filter(group_id__name='Cooperative').count()
    exporters = User.objects.filter(group_id__name='Exporter').count()
    buyers = User.objects.filter(group_id__name='Buyer').count()
    accepted_batches = Batch.objects.filter(is_approved=True).count()
    rejected_batches = Batch.objects.filter(is_approved=False).count()

    districts = {
        "Central Region": [
            "Buikwe",
            "Bukomansimbi",
            "Butambala",
            "Buvuma",
            "Gomba",
            "Kalangala",
            "Kalungu",
            "Kampala",
            "Kasanda",
            "Kayunga",
            "Kiboga",
            "Kyankwanzi",
            "Kyotera",
            "Luweero",
            "Lwengo",
            "Lyantonde",
            "Masaka",
            "Mityana",
            "Mpigi",
            "Mubende",
            "Mukono",
            "Nakaseke",
            "Nakasongola",
            "Rakai",
            "Sembabule",
            "Wakiso"
        ],
        "Eastern Region": [
            "Amuria",
            "Kapelebyong",
            "Budaka",
            "Bududa",
            "Bugiri",
            "Bugweri",
            "Bukedea",
            "Bukwa",
            "Bulambuli",
            "Busia",
            "Butaleja",
            "Butebo",
            "Buyende",
            "Iganga",
            "Jinja",
            "Kaberamaido",
            "Kalaki",
            "Kaliro",
            "Kamuli",
            "Kapchorwa",
            "Katakwi",
            "Kibuku",
            "Kumi",
            "Manafwa",
            "Namisindwa",
            "Mayuge",
            "Mbale",
            "Namayingo",
            "Namutumba",
            "Ngora",
            "Pallisa",
            "Butebo",
            "Serere",
            "Sironko",
            "Soroti",
            "Tororo"
        ], "Northern Region": [
            "Abim",
            "Adjumani",
            "Agago",
            "Alebtong",
            "Amolatar",
            "Amudat",
            "Amuru",
            "Apac",
            "Kwania"
            "Arua",
            "Terego",
            "Madi-Okollo",
            "Dokolo",
            "Gulu",
            "Omoro",
            "Kaabong",
            "Karenga",
            "Kitgum",
            "Koboko",
            "Kole",
            "Kotido",
            "Lamwo",
            "Lira",
            "Maracha",
            "Moroto",
            "Moyo",
            "Obongi",
            "Nakapiripirit",
            "Nabilatuk",
            "Napak",
            "Nebbi",
            "Packwach",
            "Nwoya",
            "Otuke",
            "Oyam",
            "Pader",
            "Yumbe",
            "Zombo"
        ],
        "Western Region": [
            "Buhweju",
            "Buliisa",
            "Bundibugyo",
            "Bushenyi",
            "Hoima",
            "Kikuube",
            "Ibanda",
            "Isingiro",
            "Kabale",
            "Rubanda",
            "Kabarole",
            "Bunyangabu",
            "Kamwenge",
            "Kitagwenda"
            "Kanungu",
            "Kasese",
            "Kibaale",
            "Kakumiro",
            "Kagadi",
            "Kiruhura",
            "Kazo",
            "Kiryandongo",
            "Kisoro",
            "Kyegegwa",
            "Kyenjojo",
            "Masindi",
            "Mbarara",
            "Rwampara",
            "Mitooma",
            "Ntoroko",
            "Ntungamo",
            "Rubirizi",
            "Rukiga",
            "Rukungiri",
            "Sheema"
        ]
    }
    if request.method == 'POST':
        district = request.POST.get('district')
        if district:
            district_cooperatives = User.objects.filter(
                location__icontains=district, group__name='Cooperative').count()
            context = {
                'farmers': farmers,
                'cooperatives':  cooperatives,
                'exporters': exporters,
                'buyers': buyers,
                'accepted_batches': accepted_batches,
                'rejected_batches': rejected_batches,
                'districts': districts,
                'district_cooperatives': district_cooperatives,
            }
            return render(request, 'base/admin/admin-home.html', context)

    context = {
        'farmers': farmers,
        'cooperatives':  cooperatives,
        'exporters': exporters,
        'buyers': buyers,
        'accepted_batches': accepted_batches,
        'rejected_batches': rejected_batches,
        'districts': districts
    }
    return render(request, 'base/admin/admin-home.html', context)

# Login admin


def adminLogin(request):
    if request.user.is_authenticated:
        return redirect('admin-home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # check if user belongs to admin group---> if not, redirect to login page
        try:
            user = User.objects.get(email=email)
            group = user.group.name
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
                name=coperative_name,
                phone=phone,
                location=location,
                password=hashed_password,
                email=email,
            )
        except:
            messages.error(request, "Cooperative email already exists.")
            return redirect('admin-cooperative-registration')
        # add user to cooperative group
        group = Group.objects.get(name='Cooperative')
        group.group_user.add(cooperative)

        # add cooperative_head to cooperative table
        details = Cooperative.objects.create(
            cooperative_head=cooperative_head,
        )

        cooperative.cooperative_details.add(details)

        # send email to cooperative
        send_email('cooperative', coperative_name, email, password)
        messages.success(
            request, "Cooperative registered successfully and email sent.")
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
    return render(request, 'base/admin-delete.html', {'obj': cooperative})


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
                name=exporter_name,
                phone=phone,
                location=location,
                password=hashed_password,
                email=email,
            )
        except:
            messages.error(request, "Email already exists.")
            return redirect('admin-exporter-registration')
        # add user to cooperative group
        group = Group.objects.get(name='Exporter')
        group.group_user.add(exporter)

        # add cooperative_head to cooperative table
        details = Exporter.objects.create(
            license=license,
        )

        exporter.exporter_details.add(details)

        # send email to cooperative
        send_email('exporter', exporter_name, email, password)
        messages.success(
            request, "Cooperative registered successfully and email sent.")
        return redirect('admin-manage-exporters')
    return render(request, 'base/admin/admin-exporter-registration.html')


def adminBatchView(request):
    batches = Batch.objects.all()
    context = {'batches': batches}
    return render(request, 'base/admin/admin-view-batches.html', context)

# email sending


def send_email(account_type, name, email, password):
    subject = 'Welcome to the CQTS Platform'
    recipient_list = [email]  # Replace with the recipient's email address

    # Render the HTML template
    context = {
        'type': account_type,
        'name': name,
        'email': email,
        'password': password
    }
    html_message = render_to_string(
        'base/registration/account_registration_email_template.html', context)

    # Create the plain text version of the message
    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL,
              recipient_list, html_message=html_message)
    return None
