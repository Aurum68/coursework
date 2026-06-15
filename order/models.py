from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import models_3d.models


# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class OrderStatus(models.TextChoices):
        PROCESSING = 'PROC', _('В обработке')
        COMPLETED = 'COMP', _('Выполнен')
        CANCELLED = 'CANC', _('Отменен')

    status = models.CharField(max_length=4, choices=OrderStatus.choices, default=OrderStatus.PROCESSING)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    model_3d = models.ForeignKey(models_3d.models.Model3D, on_delete=models.SET_NULL, null=True)

    # Для сохранения истории
    model_3d_name = models.CharField(max_length=255)
    model_3d_image = models.ImageField(upload_to="model_images/", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    material = models.ForeignKey(models_3d.models.Material, on_delete=models.SET_NULL, null=True)

    # Для сохранения истории
    material_name = models.CharField(max_length=255)
    material_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    color = models.ForeignKey(models_3d.models.Color, on_delete=models.SET_NULL, null=True)

    # Для сохранения истории
    color_name = models.CharField(max_length=255, null=True, blank=True)
    color_hex_code = ColorField(default='#FF0000', format='hex')

    quantity = models.PositiveIntegerField()
    scale = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.model_3d_name = self.model_3d.name
            self.model_3d_image = self.model_3d.image

            if self.material:
                self.material_name = self.material.name
                self.material_price = self.material.price_per_gram
            if self.color:
                self.color_name = self.color.name
                self.color_hex_code = self.color.hex_code
        super().save(*args, **kwargs)

