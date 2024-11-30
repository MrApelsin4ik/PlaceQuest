from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.template import RequestContext
from .models import CustomUser, AttrList, TaskList, AttrFile, TaskFile, UserTask, TaskList2, UserTask2, Filter, AttrFilter
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import json
import math

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
        filters = Filter.objects.all()
        grouped_filters = {}
        for filter in filters:
            if filter.key not in grouped_filters:
                grouped_filters[filter.key] = []
            grouped_filters[filter.key].append(filter)

        return render(request, 'main.html', {'grouped_filters': grouped_filters})
    elif request.method == "POST":
        pass
    elif request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        start = int(request.GET.get('start', 0))
        limit = 100

        filter_ids = request.GET.getlist('filters[]')

        # Фильтрация attr по выбранным фильтрам

        if filter_ids:
            filtered_attrs = AttrList.objects.filter(filters__id__in=filter_ids).distinct()
        else:
            filtered_attrs = AttrList.objects.all()

        attractions = filtered_attrs[start:start + limit]

        # Сериализация данных аттракционов
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
            try:
                # Проверка текста на русский язык (проверка email или пароля)
                email = request.POST.get('signupEmail') or request.POST.get('loginEmail', '')
                password = request.POST.get('signupPassword') or request.POST.get('loginPassword', '')

                # Проверка валидности email
                validate_email(email)

                user = CustomUser.objects.create_user(email=email, password=password)
                user.save()
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({'redirect_url': '/'})
            except ValidationError:
                return JsonResponse({'error2': 'Неверный формат email.'})
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




def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Вычисление расстояния между двумя точками в метрах, используя формулу Haversine.
    """
    # Радиус Земли в метрах
    R = 6371000
    # Преобразуем координаты в радианы
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Разница координат
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Формула Haversine
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def calculate_rating(distance, max_distance=10000, max_rating=100):
    """
    Расчёт рейтинга на основе расстояния.
    Если расстояние больше max_distance, возвращается 0.
    """
    if distance > max_distance:
        return 0
    return round((1 - (distance / max_distance)) * max_rating)

@login_required()
def pass_task(request):
        try:
            # Получаем данные из запроса
            data = json.loads(request.body)
            user_id = request.user.id
            task_id = data.get('task_id')
            longitude = float(data.get('longitude'))
            latitude = float(data.get('latitude'))
            print(task_id, longitude, latitude)

            # Проверяем, есть ли уже запись с таким user_id и task_id
            if UserTask.objects.filter(user_id=user_id, task_id=task_id).exists():
                return JsonResponse({'success': False, 'error': 'Задание уже выполнено'})


            task = get_object_or_404(TaskList, id=task_id)

            # Вычисляем расстояние
            distance = calculate_distance(latitude, longitude, task.latitude, task.longitude)
            print(distance)
            # Рассчитываем рейтинг
            rating = int(calculate_rating(distance))
            print(rating)

            if rating != 0:
                user = get_object_or_404(CustomUser, id=user_id)
                user.rating += rating
                user.save()

            user_task = UserTask.objects.create(
                user_id=user_id,
                task=task,
                longitude=longitude,
                latitude=latitude,
                task_number=task.id
            )

            # Сохраняем объект в БД
            user_task.save()

            return JsonResponse({'success': True, 'rating': rating, 'inf_aft_complete':task.inf_aft_complete, 'longitude':task.longitude, 'latitude':task.latitude})
        except Exception as e:
            # В случае ошибки возвращаем ошибку
            return JsonResponse({'success': False, 'error': str(e)})


@login_required
def rating_table(request):
    current_user = CustomUser.objects.get(id=request.user.id)
    users = CustomUser.objects.exclude(id=request.user.id).order_by('-rating').values('id', 'rating')

    return render(request, 'rating_table.html', {
        'user_id': current_user.id,
        'user_rating': current_user.rating,
        'users': users
    })

@login_required
def assistant(request):
    return render(request, 'assistant.html')


@login_required
def game(request):
    if request.method == "GET" and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return render(request, 'game.html')
    elif request.method == "POST":
        pass
    elif request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        start = int(request.GET.get('start', 0))
        limit = 100

        # Фильтруем задачи, исключая те, которые уже выполнены для текущего пользователя
        tasks = TaskList.objects.exclude(
            id__in=UserTask.objects.filter(user_id=request.user.id).values('task_id')
        )[start:start + limit]

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
    tasks1 = TaskList.objects.all().values('id', 'name')
    tasks2 = TaskList2.objects.all().values('id', 'name')

    # Передаем данные в шаблон в формате JSON
    return render(request, 'admin_page.html', {
        'attractions': json.dumps(list(attractions)),
        'tasks1': json.dumps(list(tasks1)),
        'tasks2': json.dumps(list(tasks2)),
    })



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
            task.inf_aft_complete = request.POST.get('inf_aft_complete')
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

            # Обновление фильтров
            filter_ids = request.POST.getlist('filters')
            # Удаление всех текущих фильтров
            attr.filters.clear()


            # Добавляем выбранные фильтры
            for filter_id in filter_ids:
                if filter_id:
                    filter_obj = Filter.objects.get(id=filter_id)
                    attr.filters.add(filter_obj)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Добавление новых файлов
        files = request.FILES.getlist('files')
        for file in files:
            AttrFile(attr_list=attr, file=file).save()

        return JsonResponse({'message': 'Задание изменено', 'id': attr.id}, status=201)

    # Получаем доступные фильтры
    available_filters = Filter.objects.all()

    # Отображаем форму для редактирования
    return render(request, 'edit_attr.html', {'attr': attr, 'available_filters': available_filters})

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
            inf_aft_complete = request.POST.get('inf_aft_complete', '')
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
                latitude=latitude,
                inf_aft_complete=inf_aft_complete
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
        filters = Filter.objects.all()
        return render(request, 'add_attr.html', {'filters': filters})

    elif request.method == 'POST':
        try:
            # Using request.POST for form fields and request.FILES for uploaded files
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            filter_ids = request.POST.getlist('filters')
            if not name:
                return JsonResponse({'error': 'Поле name обязательно'}, status=400)

            # Create the attraction object
            attr = AttrList(name=name, description=description)
            attr.save()

            # Привязка выбранных фильтров
            for filter_id in filter_ids:
                try:
                    filter_obj = Filter.objects.get(id=filter_id)
                    attr.filters.add(filter_obj)
                except Filter.DoesNotExist:
                    continue  # Если фильтр не найден, просто пропускаем

            # Handling file uploads
            files = request.FILES.getlist('files')  # Get all uploaded files

            for file in files:
                # Create and save a file object for each uploaded file
                AttrFile(attr_list=attr, file=file).save()

            return JsonResponse({'message': 'Достопримечательность добавлена', 'id': attr.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@login_required
def game2(request):
    if request.method == "GET" and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return render(request, 'game2.html')
    elif request.method == "POST":
        pass
    elif request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        start = int(request.GET.get('start', 0))
        limit = 100

        # Фильтруем задачи, исключая те, которые уже выполнены для текущего пользователя
        tasks = TaskList2.objects.exclude(
            id__in=UserTask2.objects.filter(user_id=request.user.id).values('task_id')
        )[start:start + limit]

        # Serialize the data into JSON format
        tasks_data = [{
            'id': task.id,
            'name': task.name,
            'required_time': task.required_time,
            'rating': task.rating,
            'parts':task.parts,
            'image_url': task.image.url if task.image else None,


        } for task in tasks]

        return JsonResponse({'tasks': tasks_data})


@login_required
@user_passes_test(is_admin)
def add_task2(request):
    if request.method == 'GET':
        return render(request, 'add_task.html')
    elif request.method == 'POST':
        try:
            # Handle form fields (non-file data)
            name = request.POST.get('name')
            inf_aft_complete = request.POST.get('inf_aft_complete', '')
            rating = request.POST.get('rating')
            required_time = request.POST.get('required_time')
            parts = request.POST.get('parts')

            rating = int(rating) if rating else None
            required_time = int(required_time) if required_time else None

            if 'image' in request.FILES:
                image = request.FILES['image']  # Заменяем существующее изображение

            if not name:
                return JsonResponse({'error': 'Поле name обязательно'}, status=400)


            # Create and save Task object
            task = TaskList2(
                name=name,
                inf_aft_complete=inf_aft_complete,
                image=image,
                rating=rating,
                required_time=required_time,
                parts=parts,
            )
            task.save()


            return JsonResponse({'message': 'Задание добавлено', 'id': task.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
def delete_task_file2(request, id):
    if request.method == 'POST':
        task = get_object_or_404(TaskList2, id=id)
        if task.image:
            task.image.delete()
            task.save()
        return JsonResponse({'message': 'Файл удален'}, status=200)
    return JsonResponse({'error': 'Неверный запрос'}, status=400)

@login_required
@user_passes_test(is_admin)
def delete_task2(request, id):
    if request.method == 'POST':
        task = get_object_or_404(TaskList2, id=id)
        task.delete()
        return JsonResponse({'message': 'Файл удален'}, status=200)

    return JsonResponse({'error': 'Неверный запрос'}, status=400)

@login_required
@user_passes_test(is_admin)
def delete_task(request, id):
    if request.method == 'POST':
        task = get_object_or_404(TaskList, id=id)
        task.delete()
        return JsonResponse({'message': 'Файл удален'}, status=200)

    return JsonResponse({'error': 'Неверный запрос'}, status=400)


@login_required
@user_passes_test(is_admin)
def delete_attr(request, id):
    if request.method == 'POST':
        task = get_object_or_404(AttrList, id=id)
        task.delete()
        return JsonResponse({'message': 'Файл удален'}, status=200)

    return JsonResponse({'error': 'Неверный запрос'}, status=400)



@login_required
@user_passes_test(is_admin)
def edit_task2(request, id):
    task = get_object_or_404(TaskList2, id=id)

    if request.method == 'POST':

        try:
            task.name = request.POST.get('name')
            task.inf_aft_complete = request.POST.get('inf_aft_complete')
            task.rating = int(request.POST.get('rating', task.rating))  # Обновление рейтинга
            task.required_time = int(request.POST.get('required_time', task.required_time))  # Обновление времени
            task.parts=int(request.POST.get('parts', task.parts))
            if 'image' in request.FILES:
                task.image = request.FILES['image']  # Заменяем существующее изображение

            task.save()

        except (InvalidOperation, ValueError):
            return JsonResponse({'error': 'Некорректные значения для долготы или широты'}, status=400)


        return JsonResponse({'message': 'Задание изменено', 'id': task.id}, status=201)

    # Отображаем форму для редактирования задачи
    return render(request, 'edit_task2.html', {'task': task})



@login_required
def pass_task2(request):

    try:
        # Получаем данные из запроса
        data = json.loads(request.body)
        user_id = request.user.id
        task_id = data.get('task_id')
        elapsed_time = data.get('elapsed_time')

        # Проверяем, есть ли уже запись с таким user_id и task_id
        if UserTask2.objects.filter(user_id=user_id, task_id=task_id).exists():
            return JsonResponse({'success': False, 'error': 'Задание уже выполнено'})

        task = get_object_or_404(TaskList2, id=task_id)

        max_time = task.required_time
        max_rating = task.rating

        # Вычисляем рейтинг в зависимости от времени выполнения
        if elapsed_time > max_time:
            rating = 0  # Если время превышено, то рейтинг 0
        else:
            # Рассчитываем пропорциональный рейтинг
            rating = round(max_rating * (1 - (elapsed_time / max_time)))

        if rating != 0:
            user = get_object_or_404(CustomUser, id=user_id)
            user.rating += rating
            user.save()

        user_task = UserTask2.objects.create(
            user_id=user_id,
            task=task,
        )

        # Сохраняем объект в БД
        user_task.save()

        return JsonResponse({'success': True, 'rating': rating, 'inf_aft_complete': task.inf_aft_complete})
    except Exception as e:
        # В случае ошибки возвращаем ошибку
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def logout_view(request):
    logout(request)
    return redirect(register_and_login)
