from django.contrib import admin
from .models import Cat, Mission, Target

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ("name", "breed", "years_of_experience", "salary", "hired_at")
    search_fields = ("name", "breed")
    list_filter = ("breed",)

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("title", "assigned_cat", "completed", "created_at")
    search_fields = ("title", "description")
    list_filter = ("completed",)
    raw_id_fields = ("assigned_cat",)

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "mission", "completed", "completed_at")
    search_fields = ("name", "country")
    list_filter = ("completed", "country")
    raw_id_fields = ("mission",)
