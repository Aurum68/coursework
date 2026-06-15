from typing import Any

from django import forms

from models_3d.models import Color, Material


class AddToCartForm(forms.Form):
    material = forms.ChoiceField(
        label='Материал',
        error_messages={'invalid_choice': 'Выбран некорректный тип материала.'}
    )

    color = forms.ModelChoiceField(
        queryset=Color.objects.all(),
        label='Цвет',
        error_messages={'invalid_choice': 'Выбран некорректный цвет.'}
    )

    scale = forms.IntegerField(
        min_value=50,
        max_value=200,
        initial=100,
        widget=forms.NumberInput(
            attrs={
                'type': 'range',
                'min': '50',
                'max': '200',
                'step': '10',
                'class': 'form-range',
            }
        )
    )

    def __init__(self, *args, aggregated_options: list[dict[str, Any]]|None = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['scale'].widget.attrs.update(
            {
                'id': 'scale'
            }
        )

        self.fields['color'].widget.attrs.update(
            {
                'id': 'colorSelect',
            }
        )

        if aggregated_options:
            material_choices = [(material['name'], material['name']) for material in aggregated_options]
            self.fields['material'].choices = material_choices

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material')
        color = cleaned_data.get('color')

        if not Material.objects.is_combination_possible(material_type, color):
            raise forms.ValidationError(
                "Извините, выбранный цвет недоступен для данного типа материала."
            )

        return cleaned_data