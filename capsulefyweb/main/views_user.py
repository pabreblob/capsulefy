from main.models import User
from main.forms_user import UserForm
from django.shortcuts import render, redirect
from django.contrib import messages

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

    
    