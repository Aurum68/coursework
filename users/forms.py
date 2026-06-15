from django import forms
from django.contrib.auth.forms import UserChangeForm
from phonenumber_field.formfields import SplitPhoneNumberField

from users.models import User


class RegisterUserForm(forms.ModelForm):
    password_confirm = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)
    phone = SplitPhoneNumberField(
        label='Номер телефона',
        required=False,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }


    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают')

        return cleaned_data


class LoginUserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class EditUserForm(UserChangeForm):
    password = None
    phone = SplitPhoneNumberField(
        label='Номер телефона',
        required=False,
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        full_width_field = ['email', 'phone']

        for field_name, field in self.fields.items():
            if field_name in full_width_field:
                field.widget.attrs['is_full_width'] = True