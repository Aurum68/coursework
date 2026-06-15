from typing import Any

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.html import format_html

from models_3d.models import Model3D, Color, MaterialBrand, Material


# Register your models here.

@admin.register(Model3D)
class Model3DAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'file_name', 'image_preview', 'dimensions', 'created_at', 'updated_at']

    list_display_links = ['id', 'name']

    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'image'],
            'classes': ['wide'],  # CSS-классы для стилизации
        }),
        ('Характеристики', {
            'fields': ['length', 'width', 'height'],
            'classes': ['collapse'],  # свернуть эту секцию
        }),
        ('Цена и файл', {
            'fields': ['price', 'file'],
        }),
    ]

    def save_model(self,
                   request: HttpRequest,
                   obj: Model3D,
                   form: Any,
                   change: Any
                   ) -> None:
        if not obj.author:
            obj.author = request.user

        if obj.author.id != request.user.id:
            raise PermissionDenied

        super().save_model(request, obj, form, change)


    def file_name(self, obj: Model3D) -> str:
        return obj.file.name


    def image_preview(self, obj: Model3D) -> str:
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '—'


    def dimensions(self, obj: Model3D) -> str:
        return f'{obj.length}x{obj.width}x{obj.height}'


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'hex_code', 'created_at', 'updated_at']
    list_display_links = ['id', 'name', 'hex_code']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'name', 'created_at', 'updated_at']
    list_display_links = ['id', 'name']