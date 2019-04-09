import paypalrestsdk
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.db.models import Q
from main import paypal
from .forms import ContactForm, NewFreeCapsuleForm, EditFreeCapsuleForm, ModularCapsuleForm, ModuleForm,\
    ModulesFormSet, NotifEmailForm
from .models import Capsule, Module, File, Social_network, User, Admin
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
from random import randint
import os
from datetime import datetime, timezone
from django.http import HttpResponseNotFound
import smtplib
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
import mimetypes
import main
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
import tweepy
from _functools import reduce
import operator
from main.logic import check_modules_release,remove_expired_capsules,check_deadman_switch


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
    capsule = get_object_or_404(Capsule, id=id)
    if capsule.capsule_type == 'M' and capsule.payment_id is None:
        return HttpResponseNotFound()
    creator = False
    editable = True
    if request.user.is_authenticated:
        user = request.user
        if user.id == capsule.creator.id:
            creator = True
    modules = []
    for module in capsule.modules.all():
        if module.release_date < datetime.now(timezone.utc):
            editable = False
        if not (creator == False and module.release_date > datetime.now(timezone.utc)):
            modules.append(module)
    modules.sort(key=lambda x: x.pk)
    if len(modules) == 0:
        return HttpResponseNotFound()
    else:
        return render(request, 'capsule/displaycapsule.html', {'capsule': capsule, 'modules': modules, 'editable': editable})


conversion_to_seconds = [60, 86400, 2592000, 31536000]

testMode = False
def createModularCapsule(request):
    user = request.user
    errors = []
    if request.method == 'POST':
        capsuleForm = ModularCapsuleForm(request.POST, user=request.user)
        moduleFormSet = ModulesFormSet(request.POST,  request.FILES)
        size = checkSize(request, moduleFormSet)
        if size > 524288000:
            errors.append("The total size of files can not be more than 500mb ")
        if capsuleForm.is_valid() and moduleFormSet.is_valid() and len(errors) == 0:
            title = capsuleForm.cleaned_data['title']
            emails = capsuleForm.cleaned_data['emails']
            capsule_type = 'M'
            private = capsuleForm.cleaned_data['private']
            try:
                time_unit = int(capsuleForm.cleaned_data['deadman_time_unit'])
                dead_man_switch = capsuleForm.cleaned_data['deadman_switch']
                dead_man_counter = capsuleForm.cleaned_data['deadman_counter'] * conversion_to_seconds[time_unit]
            except:
                dead_man_switch = False
                dead_man_counter = 0
                time_unit = 0
            price = 11.99
            twitter = capsuleForm.cleaned_data['twitter']
            facebook = capsuleForm.cleaned_data['facebook']
            print(time_unit)
            capsule = Capsule.objects.create(title=title, emails=emails, capsule_type=capsule_type, private=private,
                                             dead_man_switch=dead_man_switch, dead_man_counter=dead_man_counter,
                                             dead_man_initial_counter=dead_man_counter, time_unit=time_unit,
                                             twitter=twitter, facebook=facebook,
                                             creator_id=user.id, price=price)
            modulesCount = 0;
            for moduleForm in moduleFormSet:
                description = moduleForm.cleaned_data['description']
                release_date = moduleForm.cleaned_data['release_date']
                files = request.FILES.getlist('form-' + str(modulesCount) + '-file')
                module = Module.objects.create(description=description, release_date=release_date,
                                               capsule_id=capsule.id)
                modulesCount += 1
                if files is not None:
                    for file in files:
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
                        client = storage.Client(credentials=credentials, project='capsulefy')
                        bucket = client.get_bucket('capsulefy.appspot.com')
                        idrand = randint(0, 999)
                        filename, fileext = os.path.splitext(file.name)
                        blob = bucket.blob(capsule.title + str(idrand) + fileext)
                        filetype = mimetypes.guess_type(file.name)[0]
                        if filetype is None:
                            filetype = 'application/octet-stream'
                        filetypedb = 'F'
                        if filetype.split('/')[0] == 'image':
                            filetypedb = 'I'
                        elif filetype.split('/')[0] == 'video':
                            filetypedb = 'V'
                        blob.upload_from_file(file, size=file.size, content_type=filetype)
                        url = 'https://firebasestorage.googleapis.com/v0/b/capsulefy.appspot.com/o/' + capsule.title + str(
                            idrand) + \
                              fileext + '?alt=media&token=fbe33a62-037f-4d29-8868-3e5c6d689ca5'
                        filesize = file.size / 1048576
                        File.objects.create(url=url, size=filesize, type=filetypedb,
                                            remote_name=capsule.title + str(idrand) + fileext,
                                            local_name=file.name, module_id=module.id)

            if not testMode:
                request.session['capsuleId'] = capsule.id
                request.session.modified = True
                approval_url = paypal.payment(capsule.id)
                return HttpResponseRedirect(approval_url)
            else:
                return HttpResponseRedirect('/displaycapsule/' + str(capsule.id))
    else:
        capsuleForm = ModularCapsuleForm()
        moduleFormSet = ModulesFormSet()
    return render(request, 'capsule/createmodularcapsule.html', {"capsuleForm": capsuleForm, "moduleFormSet": moduleFormSet, "errors": errors})


def checkSize(request, moduleFormSet):
    totalSize = 0
    modulesCount = 0
    for moduleForm in moduleFormSet:
        files = request.FILES.getlist('form-' + str(modulesCount) + '-file')
        if files is not None:
            for file in files:
                print(file.size)
                totalSize += file.size
    return totalSize


def paymentExecute(request):
    paymentId = request.GET["paymentId"]
    PayerID = request.GET["PayerID"]
    payment = paypalrestsdk.Payment.find(paymentId)
    paypal.execute(payment, PayerID)
    capsuleId = request.session['capsuleId']
    capsule = Capsule.objects.filter(id = capsuleId).first()
    capsule.payment_id = paymentId
    capsule.save()
    return HttpResponseRedirect('/displaycapsule/' + str(capsuleId))


def editModularCapsule(request, pk):
    oldcapsule = get_object_or_404(Capsule, id=pk)
    if (oldcapsule.capsule_type != "M"):
        return HttpResponseNotFound()
    user = request.user
    if user.id != oldcapsule.creator.id:
        return HttpResponseNotFound()
    for module in oldcapsule.modules.all():
        if module.release_date < datetime.now(timezone.utc):
            return HttpResponseNotFound()
    olddata = {
        'title': oldcapsule.title,
        'emails': oldcapsule.emails,
        'twitter': oldcapsule.twitter,
        'facebook': oldcapsule.facebook,
        'private': oldcapsule.private,
        'deadman_switch': oldcapsule.dead_man_switch,
        'deadman_counter': oldcapsule.seconds_to_unit(),
        'deadman_time_unit': oldcapsule.time_unit
    }
    print(oldcapsule.time_unit)
    if request.method == 'POST':
        form = ModularCapsuleForm(request.POST, user=request.user)
        if form.is_valid():
            formulario = form.cleaned_data
            oldcapsule.title = formulario['title']
            oldcapsule.emails = formulario['emails']
            oldcapsule.twitter = formulario['twitter']
            oldcapsule.facebook = formulario['facebook']
            oldcapsule.private = formulario['private']
            try:
                time_unit = int(formulario['deadman_time_unit'])
                oldcapsule.time_unit=time_unit
                oldcapsule.dead_man_switch = formulario['deadman_switch']
                oldcapsule.dead_man_counter = formulario['deadman_counter']*conversion_to_seconds[time_unit]
                oldcapsule.dead_man_initial_counter = formulario['deadman_counter'] * conversion_to_seconds[time_unit]
            except:
                dead_man_switch = False
                dead_man_counter = 0
                time_unit = 0
            oldcapsule.save()
            return HttpResponseRedirect('/displaycapsule/' + str(pk))
    else:
        form = ModularCapsuleForm(initial=olddata)
        return render(request, 'capsule/editmodularcapsule.html', {'form': form, 'oldcapsule': oldcapsule})


def createModule(request, pk):
    user = request.user
    capsule = get_object_or_404(Capsule, id=pk)
    if user.id != capsule.creator.id:
        return HttpResponseNotFound()
    errors = []
    if request.method == 'POST':
        moduleForm = ModuleForm(request.POST, request.FILES)
        errors = checkModuleFiles(request, capsule)
        if moduleForm.is_valid() and len(errors) == 0:
            moduleFormulario = moduleForm.cleaned_data
            description = moduleFormulario['description']
            release_date = moduleFormulario['release_date']
            module = Module.objects.create(description=description, release_date=release_date, capsule_id=pk)
            files = request.FILES.getlist('file')
            if files is not None:
                for file in files:
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
                    client = storage.Client(credentials=credentials, project='capsulefy')
                    bucket = client.get_bucket('capsulefy.appspot.com')
                    idrand = randint(0, 999)
                    filename, fileext = os.path.splitext(file.name)
                    blob = bucket.blob(capsule.title + str(idrand) + fileext)
                    filetype = mimetypes.guess_type(file.name)[0]
                    if filetype is None:
                        filetype = 'application/octet-stream'
                    filetypedb = 'F'
                    if filetype.split('/')[0] == 'image':
                        filetypedb = 'I'
                    elif filetype.split('/')[0] == 'video':
                        filetypedb = 'V'
                    blob.upload_from_file(file, size=file.size, content_type=filetype)
                    url = 'https://firebasestorage.googleapis.com/v0/b/capsulefy.appspot.com/o/' + capsule.title + str(
                        idrand) + \
                          fileext + '?alt=media&token=fbe33a62-037f-4d29-8868-3e5c6d689ca5'
                    filesize = file.size / 1048576

                    File.objects.create(url=url, size=filesize, type=filetypedb,
                                        remote_name=capsule.title + str(idrand) + fileext,
                                        local_name=file.name, module_id=module.id)
            return HttpResponseRedirect('/editmodularcapsule/' + str(pk))
    else:
        moduleForm = ModuleForm()
    return render(request, 'capsule/editmodule.html', {'form': moduleForm, 'capsuleID': capsule.id, 'type': 'create', 'errors': errors})


def editModule(request, pk):
    oldmodule = get_object_or_404(Module, id=pk)
    errors = []
    if (oldmodule.capsule.capsule_type != "M"):
        return HttpResponseNotFound()
    if oldmodule.release_date < datetime.now(timezone.utc):
        return HttpResponseNotFound()
    user = request.user
    if user.id != oldmodule.capsule.creator.id:
        return HttpResponseNotFound()
    olddata = {
        'description': oldmodule.description,
        'release_date': str(oldmodule.release_date.date()),
    }
    print(str(oldmodule.release_date.date()))
    if request.method == 'POST':
        form = ModuleForm(request.POST, request.FILES)
        errors = checkModuleFiles(request, oldmodule.capsule)
        if form.is_valid() and len(errors) == 0:
            formulario = form.cleaned_data
            oldmodule.description = formulario['description']
            oldmodule.release_date = formulario['release_date']
            files = request.FILES.getlist('file')
            if files is not None:
                for file in files:
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
                    client = storage.Client(credentials=credentials, project='capsulefy')
                    bucket = client.get_bucket('capsulefy.appspot.com')
                    idrand = randint(0, 999)
                    filename, fileext = os.path.splitext(file.name)
                    blob = bucket.blob(oldmodule.capsule.title + str(idrand) + fileext)
                    filetype = mimetypes.guess_type(file.name)[0]
                    if filetype is None:
                        filetype = 'application/octet-stream'
                    filetypedb = 'F'
                    if filetype.split('/')[0] == 'image':
                        filetypedb = 'I'
                    elif filetype.split('/')[0] == 'video':
                        filetypedb = 'V'
                    blob.upload_from_file(file, size=file.size, content_type=filetype)
                    url = 'https://firebasestorage.googleapis.com/v0/b/capsulefy.appspot.com/o/' + oldmodule.capsule.title + str(
                        idrand) + \
                          fileext + '?alt=media&token=fbe33a62-037f-4d29-8868-3e5c6d689ca5'
                    filesize = file.size / 1048576

                    File.objects.create(url=url, size=filesize, type=filetypedb,
                                        remote_name=oldmodule.capsule.title + str(idrand) + fileext,
                                        local_name=file.name, module_id=oldmodule.id)
            oldmodule.save()
            return HttpResponseRedirect('/editmodularcapsule/' + str(oldmodule.capsule.id))
    else:
        form = ModuleForm(initial=olddata)
    return render(request, 'capsule/editmodule.html',
                  {'form': form, 'oldmodule': oldmodule, 'capsuleID': oldmodule.capsule.id, 'type': 'edit', 'errors': errors})


def checkModuleFiles(request, capsule):
    errors = []
    files = request.FILES.getlist('file')
    totalSize = 0
    if files is not None:
        for file in files:
            totalSize += file.size
    for module in capsule.modules.all():
        for file in module.files.all():
            totalSize += (file.size * 1048576)
    if totalSize > 524288000:
        errors.append("The total size of files can not be more than 500mb ")
    return errors



def deleteModule(request, pk):
    module = get_object_or_404(Module, id=pk)
    user = request.user
    if user.id != module.capsule.creator.id or len(module.capsule.modules.all()) == 1:
        return HttpResponseNotFound()
    files = File.objects.filter(module__capsule_id=pk)
    if len(files) != 0:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
        client = storage.Client(credentials=credentials, project='capsulefy')
        bucket = client.get_bucket('capsulefy.appspot.com')
        for file in files:
            bucket.delete_blob(file.remote_name)
    module.delete()
    return HttpResponseRedirect('/editmodularcapsule/' + str(module.capsule.id))


@login_required
def deleteFile(request, pk):
    file = get_object_or_404(File, id=pk)
    moduleid = file.module.id
    user = request.user
    if user.id != file.module.capsule.creator.id:
        return HttpResponseNotFound()
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
    client = storage.Client(credentials=credentials, project='capsulefy')
    bucket = client.get_bucket('capsulefy.appspot.com')
    bucket.delete_blob(file.remote_name)
    file.delete()
    return HttpResponseRedirect('/editmodule/' + str(moduleid))


@login_required
def deleteFreeFile(request, pk):
    file = get_object_or_404(File, id=pk)
    capsuleid = file.module.capsule.id
    user = request.user
    if user.id != file.module.capsule.creator.id:
        return HttpResponseNotFound()
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
    client = storage.Client(credentials=credentials, project='capsulefy')
    bucket = client.get_bucket('capsulefy.appspot.com')
    bucket.delete_blob(file.remote_name)
    file.delete()
    return HttpResponseRedirect('/editfreecapsule/' + str(capsuleid))


class login(LoginView):
    def __init__(self, *args, **kwargs):
        super(LoginView, self).__init__(*args, **kwargs)





@login_required
def createFreeCapsule(request):
    if request.method == 'POST':
        form = NewFreeCapsuleForm(request.POST, request.FILES, user=request.user,
                                  upfiles=request.FILES.getlist('files'))
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
                                             dead_man_initial_counter=dead_man_counter,
                                             twitter=twitter, facebook=facebook, creator_id=request.user.id)
            module = Module.objects.create(description=description, release_date=release_date, capsule_id=capsule.id)
            files = request.FILES.getlist('files')
            if files is not None:
                for file in files:
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
                    client = storage.Client(credentials=credentials, project='capsulefy')
                    bucket = client.get_bucket('capsulefy.appspot.com')
                    idrand = randint(0, 999)
                    filename, fileext = os.path.splitext(file.name)
                    blob = bucket.blob(title + str(idrand) + fileext)
                    filetype = mimetypes.guess_type(file.name)[0]
                    if filetype is None:
                        filetype = 'application/octet-stream'
                    filetypedb = 'F'
                    if filetype.split('/')[0] == 'image':
                        filetypedb = 'I'
                    elif filetype.split('/')[0] == 'video':
                        filetypedb = 'V'
                    blob.upload_from_file(file, size=file.size, content_type=filetype)
                    url = 'https://firebasestorage.googleapis.com/v0/b/capsulefy.appspot.com/o/' + title + \
                          str(idrand) + fileext + '?alt=media&token=fbe33a62-037f-4d29-8868-3e5c6d689ca5'
                    filesize = file.size / 1000000
                    File.objects.create(url=url, size=filesize, type=filetypedb,
                                        remote_name=title + str(idrand) + fileext, local_name=file.name,
                                        module_id=module.id)
            return HttpResponseRedirect('/displaycapsule/' + str(capsule.id))
    else:
        form = NewFreeCapsuleForm()
    return render(request, 'capsule/freecapsule.html', {'form': form})


@login_required
def editFreeCapsule(request, pk):
    oldcapsule = get_object_or_404(Capsule, id=pk)
    if oldcapsule.capsule_type != 'F' or oldcapsule.creator_id != request.user.id:
        return HttpResponseNotFound()
    oldmodule = oldcapsule.modules.first()
    if oldmodule.release_date < datetime.now(timezone.utc):
        return HttpResponseNotFound()
    olddata = {
        'title': oldcapsule.title,
        'description': oldmodule.description,
        'release_date': str(oldmodule.release_date.date()),
        'emails': oldcapsule.emails,
        'twitter': oldcapsule.twitter,
        'facebook': oldcapsule.facebook
    }
    if request.method == 'POST':
        form = EditFreeCapsuleForm(request.POST, request.FILES, user=request.user,
                                   upfiles=request.FILES.getlist('files'))
        if form.is_valid():
            formulario = form.cleaned_data
            oldcapsule.title = formulario['title']
            oldcapsule.emails = formulario['emails']
            oldcapsule.twitter = formulario['twitter']
            oldcapsule.facebook = formulario['facebook']
            oldmodule.description = formulario['description']
            oldmodule.release_date = formulario['release_date']
            oldcapsule.save()
            oldmodule.save()
            files = request.FILES.getlist('files')
            if files is not None:
                for file in files:
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
                    client = storage.Client(credentials=credentials, project='capsulefy')
                    bucket = client.get_bucket('capsulefy.appspot.com')
                    idrand = randint(0, 999)
                    filename, fileext = os.path.splitext(file.name)
                    blob = bucket.blob(oldcapsule.title + str(idrand) + fileext)
                    filetype = mimetypes.guess_type(file.name)[0]
                    if filetype is None:
                        filetype = 'application/octet-stream'
                    filetypedb = 'F'
                    if filetype.split('/')[0] == 'image':
                        filetypedb = 'I'
                    elif filetype.split('/')[0] == 'video':
                        filetypedb = 'V'
                    blob.upload_from_file(file, size=file.size, content_type=filetype)
                    url = 'https://firebasestorage.googleapis.com/v0/b/capsulefy.appspot.com/o/' + oldcapsule.title + \
                          str(idrand) + fileext + '?alt=media&token=fbe33a62-037f-4d29-8868-3e5c6d689ca5'
                    filesize = file.size / 1000000
                    File.objects.create(url=url, size=filesize, type=filetypedb,
                                        remote_name=oldcapsule.title + str(idrand) + fileext, local_name=file.name,
                                        module_id=oldmodule.id)
            return HttpResponseRedirect('/displaycapsule/' + str(oldcapsule.id))
    else:
        form = EditFreeCapsuleForm(initial=olddata)
    return render(request, 'capsule/freecapsule.html', {'form': form, 'oldcapsule': oldcapsule, 'oldmodule': oldmodule})


@login_required
def deleteCapsule(request, pk):
    capsule = get_object_or_404(Capsule, id=pk)
    if capsule.creator_id != request.user.id:
        return HttpResponseNotFound()
    files = File.objects.filter(module__capsule_id=pk)
    if len(files) != 0:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
        client = storage.Client(credentials=credentials, project='capsulefy')
        bucket = client.get_bucket('capsulefy.appspot.com')
        for file in files:
            bucket.delete_blob(file.remote_name)
    capsule.delete()
    return HttpResponseRedirect('/list/private')


@login_required
def select_capsule(request):
    return render(request, 'capsule/select_capsule.html')


@login_required
def refresh_deadman(request, id):
    capsule = get_object_or_404(Capsule, id=id)
    if capsule.creator_id != request.user.id:
        return HttpResponseNotFound()
    if capsule.dead_man_switch==True:
        capsule.dead_man_counter=capsule.dead_man_initial_counter
        capsule.expiration_notify=False
        capsule.save()
    return HttpResponseRedirect('/displaycapsule/' + str(capsule.id))

def list(request,type):
    
    return render(request, 'capsule/list.html',{'type':type})


def ajaxlist(request,type):
    searched = request.GET.get("query", '')
    
    if(type=='private'):
        capsulesT = Capsule.objects.filter(creator_id=request.user.id).filter(title__icontains=searched)
        capsulesDate = Capsule.objects.filter(creator_id=request.user.id).filter(modules__release_date__icontains=searched)
        capsulesDesc = Capsule.objects.filter(creator_id=request.user.id).filter(modules__description__icontains=searched)
        capsules_list=capsulesT|capsulesDate|capsulesDesc
    else:
        capsules_list = Capsule.objects.filter(private=False,creator__is_active=True).order_by('id')
        if(searched!=""):
            wds = searched.split()
            tag_qs = reduce(operator.and_,
                             (Q(title__icontains=x) | \
                             Q(modules__release_date__icontains=x) | \
                             Q(modules__description__icontains=x)  for x in wds))
            capsules_list =capsules_list.filter(tag_qs)

    
    page = request.GET.get('page', 1)
    paginator = Paginator(capsules_list, 4)
    
    try:
        capsules = paginator.page(page)
    except PageNotAnInteger:
        capsules = paginator.page(1)
    except EmptyPage:
        capsules = paginator.page(paginator.num_pages)
    
    response=render_to_string('capsule/list_content.html', {'capsules': capsules,'type':type})

    return HttpResponse(response)


@login_required
def my_account(request):
    hastwitter = False
    emailNot = ""
    try:
        user_logged = User.objects.get(id=request.user.id)
        if user_logged.email_notification != None and user_logged.email_notification != "":
            emailNot = user_logged.email_notification.split(",")
    except:
        user_logged = Admin.objects.get(id=request.user.id)
    username = ''
    twitteracc = Social_network.objects.filter(social_type='T', user_id=request.user.id).first()
    if twitteracc is not None:
        try:
            consumer_secret = settings.TWITTER_CREDENTIALS['consumer_secret']
            consumer_key = settings.TWITTER_CREDENTIALS['consumer_key']
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(twitteracc.token, twitteracc.secret)
            api = tweepy.API(auth)
            username = api.me()._json['screen_name']
            hastwitter = True
        except:
            print('Twitter error, revoking credentials')
            twitteracc.delete()
    return render(request, 'user/myaccount.html', {'emailNot':emailNot, 'userlogged': user_logged, 'hastwitter': hastwitter, 'username': username})


@login_required
def login_twitter(request):
    twitteracc = Social_network.objects.filter(social_type='T', user_id=request.user.id).first()
    if twitteracc is not None:
        return HttpResponseRedirect('/user/myaccount')
    consumer_secret = settings.TWITTER_CREDENTIALS['consumer_secret']
    consumer_key = settings.TWITTER_CREDENTIALS['consumer_key']
    callback_url = request.build_absolute_uri('/user/successtwitter')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)
    try:
        redirect_url = auth.get_authorization_url()
        request.session['request_token'] = auth.request_token
        return HttpResponseRedirect(redirect_url)
    except tweepy.TweepError as e:
        print('Error! Failed to get request token.')
        print(e.response)
        return HttpResponseRedirect('/user/myaccount')


@login_required
def success_twitter(request):
    twitteracc = Social_network.objects.filter(social_type='T', user_id=request.user.id).first()
    if twitteracc is not None:
        return HttpResponseRedirect('/user/myaccount')
    consumer_secret = settings.TWITTER_CREDENTIALS['consumer_secret']
    consumer_key = settings.TWITTER_CREDENTIALS['consumer_key']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    token = request.session['request_token']
    del request.session['request_token']
    verifier = request.GET.get('oauth_verifier')
    auth.request_token = token
    try:
        auth.get_access_token(verifier)
        Social_network.objects.create(social_type='T', token=auth.access_token, secret=auth.access_token_secret,
                                      user_id=request.user.id)
        return HttpResponseRedirect('/user/myaccount')
    except tweepy.TweepError as e:
        print(e.response)
        print('Error! Failed to get access token.')
        return HttpResponseRedirect('/user/myaccount')


def update(request):
    check_deadman_switch()
    check_modules_release()
    remove_expired_capsules()
    return HttpResponse("")


@login_required
def update_notifemail(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = NotifEmailForm(request.POST, instance=user)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            return HttpResponseRedirect('/user/myaccount')
    else:
        form = NotifEmailForm(instance=user)
    return render(request, 'user/notifemail.html', {'form': form})
