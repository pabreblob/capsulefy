from main.models import User,Capsule
from main.forms_user import UserForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as UserA
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.http import HttpResponseNotFound
from main.views import deleteCapsule
def register(request):

    if(request.method=='POST'):
        form = UserForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(raw_password=user.password)
            user.save()
            messages.success(request, "Usuario registrado con exito."+
            " Ya puede iniciar sesión ")
            return redirect('login')
    else:
        form=UserForm()
            
    return render(request, 'capsule/register.html',
                          {'form': form})


@login_required
def deleteUser(request):
    user = request.user
    user_del = get_object_or_404(User, id=user.id)
    if user.id != user_del.id:
        return HttpResponseNotFound()
    capsules=Capsule.objects.filter(creator_id=user.id)
    for capsule in capsules:
        deleteCapsule(request,capsule.id)
    user_auth=UserA.objects.filter(id=user_del.id)
    user_auth.delete()
    return redirect('login')