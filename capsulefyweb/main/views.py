from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from .forms import ContactForm, FreeCapsuleForm
from .models import Capsule, Module, File
import smtplib


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


def createFreeCapsule(request):
    if request.method == 'POST':
        form = FreeCapsuleForm(request.POST)
        if form.is_valid():
            formulario = form.cleaned_data
            title = formulario['title']
            emails = formulario['emails']
            capsule_type = 'F'
            private = False
            dead_man_switch = False
            dead_man_counter = 0
            twitter = formulario['twitter']
            facebook = formulario['facebook']
            description = formulario['description']
            release_date = formulario['release_date']
            capsule = Capsule.objects.create(title=title, emails=emails, capsule_type=capsule_type, private=private,
                                             dead_man_switch=dead_man_switch, dead_man_counter=dead_man_counter,
                                             twitter=twitter, facebook=facebook, creator_id=2)
            Module.objects.create(description=description, release_date=release_date, capsule_id=capsule.id)
            return HttpResponseRedirect('/')
    else:
        form = FreeCapsuleForm()
    return render(request, 'freecapsule.html', {'form': form})


def editFreeCapsule(request, pk):
    oldcapsule = get_object_or_404(Capsule, id=pk)
    oldmodule = oldcapsule.modules.first()
    olddata = {
        'title': oldcapsule.title,
        'description': oldmodule.description,
        'release_date': oldmodule.release_date,
        'emails': oldcapsule.emails,
        'twitter': oldcapsule.twitter,
        'facebook': oldcapsule.facebook
    }
    if request.method == 'POST':
        form = FreeCapsuleForm(request.POST)
        if form.is_valid():
            formulario = form.cleaned_data
            title = formulario['title']
            emails = formulario['emails']
            capsule_type = 'F'
            private = False
            dead_man_switch = False
            dead_man_counter = 0
            twitter = formulario['twitter']
            facebook = formulario['facebook']
            description = formulario['description']
            release_date = formulario['release_date']
            capsule = Capsule.objects.create(title=title, emails=emails, capsule_type=capsule_type, private=private,
                                             dead_man_switch=dead_man_switch, dead_man_counter=dead_man_counter,
                                             twitter=twitter, facebook=facebook, creator_id=2)
            Module.objects.create(description=description, release_date=release_date, capsule_id=capsule.id)
            return HttpResponseRedirect('/')
    else:
        form = FreeCapsuleForm(initial=olddata)
    return render(request, 'freecapsule.html', {'form': form})

