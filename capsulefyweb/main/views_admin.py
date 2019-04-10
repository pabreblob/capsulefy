from .models import User
from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from main.models import Capsule, Module
from datetime import timezone, datetime
from django.db.models import Q
@login_required
def list(request):
    if not request.user.is_superuser:
        raise Http404("")
    if request.GET.get("search") == None or request.GET.get("search") == "":
        users_all = User.objects.all().order_by("username")
    else:
        users_all = User.objects.filter(username__icontains=request.GET.get("search")).order_by("username")

    page = request.GET.get('page', 1)

    paginator = Paginator(users_all, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'admin/user_list.html', {"users": users})

@login_required
def ajax_ban(request):
    try:
        if not request.user.is_superuser:
            raise Http404("")
        user = User.objects.get(id=request.GET.get("id"))
        user.is_active = not user.is_active
        user.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")
    
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        raise Http404("")
    '''Number of registered user, number of banned users, 
    number of premium capsules, number of free capsules, 
    ratio of premium capsules/free capsules, 
    number of published capsules, number of unpublished capsules, 
    ratio published/unpublished
    '''
    data={}
    data['registeredUser']=User.objects.all().count()
    data['bannedUser']=User.objects.filter(is_active=False).count()
    data['premiumCapsules']=Capsule.objects.filter(capsule_type='M').count()
    data['freeCapsules']=Capsule.objects.filter(capsule_type='F').count()
    data['totalCapsules']=Capsule.objects.all().count()
    data['unPaidCapsules']=Capsule.objects.filter(Q(capsule_type='M') & Q(payment_id=None)).count()
    data['bannedCapsules']=Capsule.objects.filter(creator__is_active=False).count()
    
    data['totalModules']=Module.objects.all().count()
    data['publishedModules']=Module.objects.filter(release_date__lte=datetime.now(timezone.utc)).count()
    data['unpublishedModules']=Module.objects.filter(release_date__gt=datetime.now(timezone.utc)).count()
    data['ratioPremiumFree']=data['premiumCapsules']/data['freeCapsules']
    data['ratioPubliUnpubli']=data['publishedModules']/data['unpublishedModules']
    data['porModPubli']=round(data['publishedModules']/data['totalModules']*100,1)
    data['porModunPubli']=round(data['unpublishedModules']/data['totalModules']*100,1)
    data['porCapFree']=round(data['freeCapsules']/data['totalCapsules']*100,1)
    data['porCapPre']=round(data['premiumCapsules']/data['totalCapsules']*100,1)
    
    return render(request, 'admin/dashboard.html', {"data": data})
    
    