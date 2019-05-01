import datetime
import mimetypes
import os
from datetime import timezone
from random import randint

import paypalrestsdk
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from capsulefyweb import settings
from main import paypal
from main.models import Module, Capsule, Social_network, File
from dateutil.relativedelta import relativedelta
import smtplib
import capsulefyweb.settings
import tweepy
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from django.conf import settings


def send_email(module):
    try:
        
        html_message='A time capsule module created by '+module.capsule.creator.first_name\
        +' '+module.capsule.creator.last_name+ \
        'has just been released! <br>Check it out at https://capsul' +\
        'efy.herokuapp.com/displaycapsule/' + str(module.capsule_id)
        
        mail_list = module.capsule.emails.split(',')
        i = 0
        while i < len(mail_list):
            print(mail_list[i])
            message = Mail(
                from_email='capsulefy.communications@gmail.com',
                to_emails=mail_list[i],
                subject='Module of capsule is released',
                html_content=html_message)
            try:
                sg = SendGridAPIClient(capsulefyweb.settings.SENDGRID_KEY)
                response = sg.send(message)
                module.release_notify = True
                module.save()

            except Exception as e:
                print(e)
            i = i + 1
    except:
        pass


def publish_twitter(module):
    twitteracc = Social_network.objects.filter(social_type='T', user_id=module.capsule.creator_id).first()
    if twitteracc is not None:
        try:
            consumer_secret = capsulefyweb.settings.TWITTER_CREDENTIALS['consumer_secret']
            consumer_key = capsulefyweb.settings.TWITTER_CREDENTIALS['consumer_key']
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(twitteracc.token, twitteracc.secret)
            api = tweepy.API(auth)
            api.update_status('A time capsule module I created has just been released! Check it out at https://capsul' +
                              'efy.herokuapp.com/displaycapsule/' + str(module.capsule_id))
            module.twitter_notify = True
            module.save()
        except:
            print('Twitter error, revoking credentials')
            twitteracc.delete()
    else:
        pass


def check_modules_release():
    modules = Module.objects.filter(release_date__lte=datetime.datetime.now(timezone.utc), release_notify=False)
    twittercapsules = Capsule.objects.filter(twitter=True)
    twittermodules = []
    for twcapsule in twittercapsules:
        twmodules = twcapsule.modules.filter(release_date__lte=datetime.datetime.now(timezone.utc),
                                             twitter_notify=False)
        twittermodules.extend(twmodules)

    for mod in modules:
        if mod.capsule.emails != None:
            send_email(mod)

    for mod in twittermodules:
        publish_twitter(mod)


def send_deadman_notification(capsule):
    days = round(capsule.dead_man_counter / 86400)
    try:
        if capsule.creator.email_notification != None:
            mail_list = [capsule.creator.email, capsule.creator.email_notification]
        else:
            mail_list = [capsule.creator.email]
    except:
        pass
    html_message = "<p>Your capsule titled: " \
                   + capsule.title + " is about to expire in " + str(days) + " days!</p>" \
                   + "<p>If you don't want it to be released yet, go to your capsule and press the Refresh button " \
                   + capsulefyweb.settings.BASEURL + "</p>"
    i = 0
    while i < len(mail_list):
        print(mail_list[i])
        message = Mail(
            from_email='capsulefy.communications@gmail.com',
            to_emails=mail_list[i],
            subject='Capsule timer is about to expire',
            html_content=html_message)
        try:
            sg = SendGridAPIClient(capsulefyweb.settings.SENDGRID_KEY)
            response = sg.send(message)
            capsule.expiration_notify = True
            capsule.save()

        except:
            pass
        i = i + 1


def check_deadman_switch():
    capsules = Capsule.objects.filter(dead_man_switch=True)

    for capsule in capsules:
        capsule.dead_man_counter -= 86400
        if capsule.dead_man_counter <= 0:
            capsule.dead_man_counter = 0
            modules = capsule.modules.all()
            for module in modules:
                if module.release_date > datetime.datetime.now(timezone.utc):
                    module.release_date = datetime.datetime.now(timezone.utc)
                    module.save()
            capsule.dead_man_switch = False
        elif capsule.dead_man_counter <= 604800 and capsule.expiration_notify == False:
            try:
                send_deadman_notification(capsule)
            except Exception as e:
                pass
        capsule.save()


def remove_expired_capsules():
    capsules = Capsule.objects.filter(capsule_type='F').filter(
        modules__release_date__lt=datetime.datetime.now(timezone.utc) - relativedelta(months=6))
    for capsule in capsules:
        capsule.delete()



def upload_file(capsule, module, file):
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


def delete_files(files):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
    client = storage.Client(credentials=credentials, project='capsulefy')
    bucket = client.get_bucket('capsulefy.appspot.com')
    for file in files:
        bucket.delete_blob(file.remote_name)


def delete_file(file):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.FIREBASE_CREDENTIALS)
    client = storage.Client(credentials=credentials, project='capsulefy')
    bucket = client.get_bucket('capsulefy.appspot.com')
    bucket.delete_blob(file.remote_name)


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


def checkSize(request, moduleFormSet):
    totalSize = 0
    modulesCount = 0
    for moduleForm in moduleFormSet:
        files = request.FILES.getlist('form-' + str(modulesCount) + '-file')
        if files is not None:
            for file in files:
                totalSize += file.size
    return totalSize
