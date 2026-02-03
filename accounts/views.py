from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as auth_logout

def signup(request):
    form = UserCreationForm(request.POST or None)

    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    if form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'accounts/signup.html', {'form': form})



def logout_view(request):
    auth_logout(request)
    return redirect('home')   
