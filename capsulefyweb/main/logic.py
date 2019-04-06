
import datetime
from datetime import timezone
from django.core.mail import send_mail
from main.models import Module, Capsule, Social_network
from dateutil.relativedelta import relativedelta
import smtplib
import capsulefyweb.settings
import tweepy

def send_email(module):
    
    html_message="<p><b>Capsule title: </b>"\
    +module.capsule.title+"</p>"\
    +"<p><b>Module content: </b>"\
    +module.description+"</p>"\
    +"<br><br><p><b>Author: </b>"\
    +module.capsule.creator.first_name+" "\
    +module.capsule.creator.last_name+"</p>"
    '''
    enterpriseEmail = "capsulefy.communications@gmail.com"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(enterpriseEmail, "aG7nOp4FhG")
    msg = "Capsule title: "+module.capsule.title+"\n"\
     + "Module content: "+module.description+"\n"\
     + "Author: "+module.capsule.creator.first_name+" "\
     +module.capsule.creator.last_name+"\n"
     
    msg = msg.encode('utf-8')
    server.sendmail(msg=msg, from_addr=enterpriseEmail, 
                    to_addrs=module.capsule.emails.split(','))
           
    ''' 
    try:
        send_mail(subject="Module of capsule is release",
                    message="",
                    html_message=html_message,
                    from_email="capsulefy.communications@gmail.com",
                    recipient_list=module.capsule.emails.split(','),
                    fail_silently=False)
        
        module.release_notify=True
        module.save()
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
    modules=Module.objects.filter(release_date__lte=datetime.datetime.now(timezone.utc), release_notify=False)
    twittercapsules = Capsule.objects.filter(twitter=True)
    twittermodules = []
    for twcapsule in twittercapsules:
        twmodules = twcapsule.modules.filter(release_date__lte=datetime.datetime.now(timezone.utc),
                                             twitter_notify=False)
        twittermodules.extend(twmodules)

    for mod in modules:
        send_email(mod)
    for mod in twittermodules:
        publish_twitter(mod)

def send_deadman_notification(capsule):
    days=round(capsule.dead_man_counter/86400)
    mail_list=[capsule.creator.email,capsule.creator.email_notification]
    html_message = "<p>Your capsule titled: " \
                   + capsule.title +" is about to expire in "+str(days)+" days!</p>" \
                   + "<p>If you don't want it to be released yet, go to your capsule and press the Refresh button " \
                   + capsulefyweb.settings.BASEURL + "</p>"
    try:
        send_mail(subject="Capsule timer is about to expire",
                  message="",
                  html_message=html_message,
                  from_email="capsulefy.communications@gmail.com",
                  recipient_list=mail_list,
                  fail_silently=False)
        capsule.expiration_notify=True
        capsule.save()
    except Exception as e:
        pass

def check_deadman_switch():
    capsules = Capsule.objects.filter(dead_man_switch=True)

    for capsule in capsules:
        capsule.dead_man_counter-=86400
        if capsule.dead_man_counter<=0:
            capsule.dead_man_counter=0
            modules=capsule.modules.all()
            for module in modules:
                if module.release_date>datetime.datetime.now(timezone.utc):
                    module.release_date=datetime.datetime.now(timezone.utc)
                    module.save()
            capsule.dead_man_switch=False
        elif capsule.dead_man_counter<=604800 and capsule.expiration_notify==False:
            try:
                send_deadman_notification(capsule)
            except Exception as e:
                pass
        capsule.save()

def remove_expired_capsules():
    capsules=Capsule.objects.filter(capsule_type='F').filter(modules__release_date__lt=datetime.datetime.now(timezone.utc)-relativedelta(months=6))
    for capsule in capsules:
        capsule.delete()
