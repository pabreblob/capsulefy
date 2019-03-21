from django.shortcuts import render
from main.forms import ContactForm
import smtplib

from main.models import Capsule


def index(request):
    enterpriseEmail = "capsulefy.communications@gmail.com"
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["Name"]
            email = form.cleaned_data["Email"]
            message = form.cleaned_data["Message"]
            form = ContactForm()
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(enterpriseEmail, "aG7nOp4FhG")
            msg = name + "\n" + email + "\n" + message
            msg = msg.encode('utf-8')
            server.sendmail(msg=msg, from_addr=email, to_addrs=[enterpriseEmail])
            return render(request, 'index.html', {'form': form})
    else:
        form = ContactForm()
    return render(request, 'index.html', {'form': form})


def displayCapsules(request, id):
    capsule = Capsule.objects.get(pk= id)
    modules = []
    for module in capsule.modules.all():
        #Cuando tengamos los usuarios implementados, se filtrarán los módulos no publicados si el usuario loggeado no es el creador
        modules.append(module)
        print("hola")

    return render(request, 'display-capsule.html', {'capsule': capsule , 'modules': modules})


