from django.contrib import admin
from .models import CustomUser, AttrList, AttrFile, TaskList, TaskFile, UserTask, TaskList2, UserTask2, Filter, AttrFilter

# CustomUser admin class
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'rating', 'date_joined', 'rating')
    search_fields = ('email', 'rating', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined', 'rating')
    ordering = ('-date_joined',)

admin.site.register(CustomUser, CustomUserAdmin)

# AttrList admin class
class AttrListAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

admin.site.register(AttrList, AttrListAdmin)

# AttrFile admin class
class AttrFileAdmin(admin.ModelAdmin):
    list_display = ('attr_list', 'file')
    search_fields = ('attr_list__name',)
    list_filter = ('attr_list',)

admin.site.register(AttrFile, AttrFileAdmin)

# TaskList admin class
class TaskListAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'longitude', 'latitude')
    search_fields = ('name',)
    list_filter = ('longitude', 'latitude')

admin.site.register(TaskList, TaskListAdmin)

# TaskFile admin class
class TaskFileAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'uploaded_at')
    search_fields = ('task__name',)
    list_filter = ('task',)

admin.site.register(TaskFile, TaskFileAdmin)

# UserTask admin class
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'task_number', 'longitude', 'latitude')
    search_fields = ('user__email', 'task__name')
    list_filter = ('task',)

admin.site.register(UserTask, UserTaskAdmin)

# TaskList2 admin class
class TaskList2Admin(admin.ModelAdmin):
    list_display = ('name', 'inf_aft_complete', 'image', 'amount_of_divisions', 'rating', 'required_time')
    search_fields = ('name',)
    list_filter = ('amount_of_divisions', 'rating', 'required_time')

admin.site.register(TaskList2, TaskList2Admin)

# UserTask2 admin class
class UserTask2Admin(admin.ModelAdmin):
    list_display = ('user', 'task', 'execution_time', 'image')
    search_fields = ('user__email', 'task__name')
    list_filter = ('task',)

admin.site.register(UserTask2, UserTask2Admin)

# Filter admin class
class FilterAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')

admin.site.register(Filter, FilterAdmin)

# AttrFilter admin class
class AttrFilterAdmin(admin.ModelAdmin):
    list_display = ('attr', 'filter')
    search_fields = ('attr__name', 'filter__key', 'filter__value')

admin.site.register(AttrFilter, AttrFilterAdmin)