from typing import Any

from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.db.models import Max

from core.models import Country


class Model3D(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='stl_files/', max_length=255)
    image = models.ImageField(upload_to="model_images/", null=True, blank=True)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image.url,
            'length': self.length,
            'width': self.width,
            'height': self.height,
            'price': self.price,
        }


class Color(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    hex_code = ColorField(default='#FF0000', format='hex')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name.strip() or self.hex_code

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hex_code': self.hex_code,
        }


class MaterialBrand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.ForeignKey(to=Country, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name.strip()


class MaterialManager(models.Manager):
    def get_aggregated_options(self) -> list[dict[str, Any]]:
        material_names = self.get_queryset().values_list('name', flat=True).distinct().order_by('name')

        aggregated_options = []
        for name in material_names:
            materials_with_same_name = self.get_queryset().filter(name=name)

            max_price_per_gram = materials_with_same_name.aggregate(Max('price_per_gram'))['price_per_gram__max']

            available_colors_pks = materials_with_same_name.values_list('colors', flat=True).distinct()

            colors = list(Color.objects.filter(pk__in=available_colors_pks).values('id', 'name', 'hex_code'))

            aggregated_options.append({
                'name': name,
                'price': max_price_per_gram,
                'colors': colors,
            })

        return aggregated_options

    def is_combination_possible(self, material_name: str, color: int|Color) -> bool:
        if not  material_name or not color:
            return False

        material_name = material_name.strip()
        color_id = color.id if isinstance(color, Color) else color

        return self.get_queryset().filter(
            name__iexact=material_name,
            colors__id=color_id
        ).exists()


class Material(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(to=MaterialBrand, on_delete=models.PROTECT, null=True, blank=True)
    price_per_gram = models.DecimalField(max_digits=5, decimal_places=2)
    colors = models.ManyToManyField(to=Color, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name if self.brand else ''} {self.name}".strip()

    objects = MaterialManager()


