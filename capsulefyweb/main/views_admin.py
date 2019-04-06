from .models import User
from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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