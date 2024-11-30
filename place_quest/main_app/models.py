from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()
    is_staff = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Filter(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} - {self.value}"

class AttrList(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    filters = models.ManyToManyField(Filter, through='AttrFilter')
    def __str__(self):
        return self.name



class AttrFile(models.Model):
    attr_list = models.ForeignKey(AttrList, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"Файл для {self.attr_list.name}"



class TaskList(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    inf_aft_complete = models.TextField(blank=True)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class TaskFile(models.Model):
    task = models.ForeignKey(TaskList, related_name="files", on_delete=models.CASCADE,)
    file = models.FileField(upload_to="task_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Файл для задачи: {self.task.name}"


class TaskList2(models.Model):
    name = models.CharField(max_length=255)
    inf_aft_complete = models.TextField(blank=True)
    image = models.ImageField(upload_to='task2_images/', null=True, blank=True)
    amount_of_divisions = models.IntegerField(default=9)
    rating = models.IntegerField(default=100)
    required_time = models.IntegerField(null=True, blank=True)
    parts = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name




class UserTask(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='user_tasks')
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    task_number = models.IntegerField()  # Номер задания для пользователя

class UserTask2(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks2')
    task = models.ForeignKey(TaskList2, on_delete=models.CASCADE, related_name='user_tasks')
    execution_time = models.TimeField(null=True, blank=True)  # Время выполнения задачи (можно записывать как время)
    image = models.ImageField(upload_to='task2_images/', null=True, blank=True)  # Поле для изображения




# Промежуточная модель для связывания AttrList и Filter
class AttrFilter(models.Model):
    attr = models.ForeignKey(AttrList, on_delete=models.CASCADE)
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.attr.name} - {self.filter.key}: {self.filter.value}"

    class Meta:
        unique_together = ('attr', 'filter')  # Уникальная пара атрибута и фильтра, чтобы не было дубликатов