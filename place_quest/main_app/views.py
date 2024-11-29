from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from .models import CustomUser
from django.template import RequestContext
from .models import AttrList, TaskList, AttrFile, TaskFile
from decimal import Decimal, InvalidOperation
import json

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
    if request.method == "GET" and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return render(request, 'main.html')
    elif request.method == "POST":
        pass
    elif request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        start = int(request.GET.get('start', 0))
        limit = 100
        attractions = AttrList.objects.all()[start:start + limit]

        # Serialize the data into JSON format
        attractions_data = [{
            'id': attr.id,
            'name': attr.name,
            'description': attr.description,
        } for attr in attractions]

        return JsonResponse({'attractions': attractions_data})

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
def attr(request,id):
    attr = get_object_or_404(AttrList, id=id)
    files = attr.files.all()
    return render(request, 'attr.html', {'attr': attr, 'files': files})


@login_required
def task(request, id):
    task = get_object_or_404(TaskList, id=id)
    files = task.files.all()

    # Собираем информацию о файлах в список
    file_data = []
    for file in files:
        file_data.append({
            'file_name': file.file.name,
            'file_url': file.file.url,
        })

    # Возвращаем JSON с данными о задании
    return JsonResponse({
        'task_id': task.id,
        'task_name': task.name,
        'task_description': task.description,
        'files': file_data
    })

@login_required
def game(request):
    if request.method == "GET" and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return render(request, 'game.html')
    elif request.method == "POST":
        pass
    elif request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        start = int(request.GET.get('start', 0))
        limit = 100
        tasks = TaskList.objects.all()[start:start + limit]

        # Serialize the data into JSON format
        tasks_data = [{
            'id': task.id,
            'name': task.name,
            'description': task.description,
        } for task in tasks]

        return JsonResponse({'tasks': tasks_data})



# Функция проверки, является ли пользователь администратором
def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_page(request):
    # Получаем все записи из моделей
    attractions = AttrList.objects.all().values('id', 'name')
    tasks = TaskList.objects.all().values('id', 'name')

    # Передаем данные в шаблон в формате JSON
    return render(request, 'admin_page.html', {
        'attractions': json.dumps(list(attractions)),
        'tasks': json.dumps(list(tasks)),
    })

@login_required
@user_passes_test(is_admin)
def edit_attr(request, id):
    # Получаем достопримечательность по id или возвращаем 404
    attr = get_object_or_404(AttrList, id=id)

    # Логика для обработки редактирования (например, форма редактирования)
    if request.method == 'POST':
        # Здесь можно обработать форму редактирования и сохранить изменения
        attr.name = request.POST.get('name')
        attr.description = request.POST.get('description')
        attr.save()
        return redirect('admin_page')  # Перенаправляем обратно на страницу администратора

    # Отображаем форму для редактирования достопримечательности
    return render(request, 'edit_attr.html', {'attr': attr})


@login_required
@user_passes_test(is_admin)
def edit_task(request, id):
    task = get_object_or_404(TaskList, id=id)

    if request.method == 'POST':

        try:
            longitude = Decimal(request.POST.get('longitude', '').replace(',', '.')) if task.longitude else None
            latitude = Decimal(request.POST.get('latitude', '').replace(',', '.')) if task.latitude else None
            task.name = request.POST.get('name')
            task.description = request.POST.get('description')
            task.longitude = longitude
            task.latitude = latitude
            task.save()

        except (InvalidOperation, ValueError):
            return JsonResponse({'error': 'Некорректные значения для долготы или широты'}, status=400)

        # Добавление новых файлов
        files = request.FILES.getlist('files')
        for file in files:
            TaskFile(task=task, file=file).save()

        return JsonResponse({'message': 'Задание изменено', 'id': task.id}, status=201)

    # Отображаем форму для редактирования задачи
    return render(request, 'edit_task.html', {'task': task})


@login_required
@user_passes_test(is_admin)
def edit_attr(request, id):
    attr = get_object_or_404(AttrList, id=id)

    if request.method == 'POST':

        try:
            attr.name = request.POST.get('name')
            attr.description = request.POST.get('description')
            attr.save()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Добавление новых файлов
        files = request.FILES.getlist('files')
        for file in files:
            AttrFile(attr_list=attr, file=file).save()

        return JsonResponse({'message': 'Задание изменено', 'id': attr.id}, status=201)

    # Отображаем форму для редактирования задачи
    return render(request, 'edit_attr.html', {'attr': attr})

@login_required
@user_passes_test(is_admin)
def delete_task_file(request, id):
    if request.method == 'POST':
        file = get_object_or_404(TaskFile, id=id)
        file.delete()
        return JsonResponse({'message': 'Файл удален'}, status=200)
    return JsonResponse({'error': 'Неверный запрос'}, status=400)


@login_required
@user_passes_test(is_admin)
def delete_attr_file(request, id):
    if request.method == 'POST':
        file = get_object_or_404(AttrFile, id=id)
        file.delete()
        return JsonResponse({'message': 'Файл удален'}, status=200)
    return JsonResponse({'error': 'Неверный запрос'}, status=400)



@login_required
@user_passes_test(is_admin)
def add_task(request):
    if request.method == 'GET':
        return render(request, 'add_task.html')
    elif request.method == 'POST':
        try:
            # Handle form fields (non-file data)
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            longitude = request.POST.get('longitude')
            latitude = request.POST.get('latitude')

            if not name:
                return JsonResponse({'error': 'Поле name обязательно'}, status=400)

            # Validate coordinates (longitude and latitude)
            try:
                if longitude is not None:
                    longitude = Decimal(longitude)
                if latitude is not None:
                    latitude = Decimal(latitude)
            except (InvalidOperation, ValueError):
                return JsonResponse({'error': 'Значение longitude и latitude должно быть десятичным числом.'},
                                    status=400)

            # Create and save Task object
            task = TaskList(
                name=name,
                description=description,
                longitude=longitude,
                latitude=latitude
            )
            task.save()

            # Handle file uploads (using request.FILES)
            files = request.FILES.getlist('files')  # Get all uploaded files

            for file in files:
                # Save file for the task
                TaskFile(task=task, file=file).save()

            return JsonResponse({'message': 'Задание добавлено', 'id': task.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def add_attr(request):
    if request.method == 'GET':
        return render(request, 'add_attr.html')

    elif request.method == 'POST':
        try:
            # Using request.POST for form fields and request.FILES for uploaded files
            name = request.POST.get('name')
            description = request.POST.get('description', '')

            if not name:
                return JsonResponse({'error': 'Поле name обязательно'}, status=400)

            # Create the attraction object
            attr = AttrList(name=name, description=description)
            attr.save()

            # Handling file uploads
            files = request.FILES.getlist('files')  # Get all uploaded files

            for file in files:
                # Create and save a file object for each uploaded file
                AttrFile(attr_list=attr, file=file).save()

            return JsonResponse({'message': 'Достопримечательность добавлена', 'id': attr.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def logout_view(request):
    logout(request)
    return redirect(register_and_login)
