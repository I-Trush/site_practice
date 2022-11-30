from django import forms
from .models import *
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .apps import user_registered
from django.forms import inlineformset_factory


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class RegisterUserForm(forms.ModelForm):    # 32.4 регистрация и активация пользователя
    email = forms.EmailField(required=True, label='Адрес электронной почты')    # полное объявление полей, которые хотим сделать обязательными для заполнения
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput, help_text=password_validation.password_validators_help_text_html()) # сообщение с требованиями к паролю осущ. всеми доступными в системе валидаторами
    password2 = forms.CharField(label='Пароль повторно', widget=forms.PasswordInput, help_text='Введите пароль еще раз')

    def clean_password1(self):  # метод выполняет валидацию пароля введенного в 1е поле
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):    # проверка на совпадение паролей осущ. только если 1й пароль прошел валидацию
        super().clean()
        password1 = self.cleaned_data['password1']      # если пароль левый qwerty123 то valid=False и вылетает ошибка на этой строке в дебагере, вместо того чтоб выдать сообщение об ошибке
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code = 'password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False      # пользователь активен?
        user.is_activated = False   # пользователь прошел активацию? пока False пользователь не может выполнить вход
        if commit:
            user.save()         # сохраняем запись и закодированный пароль
        user_registered.send(RegisterUserForm, instance=user)   # сигнал для отправки письма активации. instance - параметр - это объект вновь созданного пользователя. Сигнал объявляется в модуле apps - этот модуль выполняется при инициализации приложения
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')


class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(), empty_label=None, label='Надрубрики', required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'


class SearchForm(forms.Form):   # у forms.Form нет атрибута save(), форма не связана с моделью
    keyword = forms.CharField(required=False, max_length=20, label='')


class BbForm(forms.ModelForm):  # 34.5 только ModelForm
    class Meta:
        model = Bb
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')