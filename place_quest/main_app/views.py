from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import CustomUser
from django.template import RequestContext

def disallowed_host_view(request, exception):
    return render(request,  '404.html', status=400)  

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
    
    
def custom_403_view(request, exception):
    return render(request, '404.html', status=403)
    
def custom_500_view(request):
    return render(request, '404.html', status=500)
    
    
def csrf_failure(request, reason=""):
    context = RequestContext(request)
    response = render(request, '404.html', context)
    response.status_code = 403
    return response

@login_required
def main(request):
    return render(request, 'main.html')


def register_and_login(request):
    if request.method == 'POST':
        # Регистрация
        if 'signupEmail' in request.POST and 'signupPassword' in request.POST:
            email = request.POST['signupEmail']
            password = request.POST['signupPassword']
            try:
                user = CustomUser.objects.create_user(email=email, password=password)
                user.save()
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)

                    return JsonResponse({'redirect_url': '/'})
            except IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    print(e)
                    return JsonResponse({'error2': 'Данная почта уже используется.'})
                else:
                    print(e)
                    return JsonResponse({'error2': 'Произошла ошибка при регистрации пользователя.'})
        # Вход
        elif 'loginEmail' in request.POST and 'loginPassword' in request.POST:
            email = request.POST['loginEmail']
            password = request.POST['loginPassword']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'redirect_url': '/'})
            else:
                # Обработка ошибки входа
                return JsonResponse({'error1': 'Неверный логин или пароль.'})
    return render(request, 'login.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect(register_and_login)
