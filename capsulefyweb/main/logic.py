
import datetime
from datetime import timezone
from django.core.mail import send_mail
from main.models import Module,Capsule
from dateutil.relativedelta import relativedelta
import smtplib

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


def check_modules_release():
    
    modules=Module.objects.filter(release_date__lte=datetime.datetime.now(timezone.utc), 
                          release_notify=False)
    
    for mod in modules:
        send_email(mod)

def check_deadman_switch():
    capsules = Capsule.objects.filter(dead_man_switch=True)

    for capsule in capsules:
        capsule.dead_man_counter-=86400
        if capsule.dead_man_counter<=0:
            capsule.dead_man_counter=0
            modules=capsule.modules.all()
            for module in modules:
                if module.release_date>datetime.now(timezone.utc):
                    module.release_date=datetime.now(timezone.utc)
                    module.save()
            capsule.dead_man_switch=False
        capsule.save()

def remove_expired_capsules():
    capsules=Capsule.objects.filter(capsule_type='F').filter(modules__release_date__lt=datetime.datetime.now(timezone.utc)-relativedelta(months=6))
    for capsule in capsules:
        capsule.delete()