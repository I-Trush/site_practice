from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, CreateView, DeleteView    #32.3 редактирование данных пользователя
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView  # 32.4.1.2
from django.core.signing import BadSignature    # 32.4.2
from django.contrib.auth import logout
from django.contrib import messages

from .models import *
from .forms import *
from .utilities import signer   #32.4.2


def index(request):
    return render(request, 'main/index.html')


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class BBLoginView(LoginView):
    template_name = 'main/login.html'


@login_required()   # 32.2.2. доступ только авторизованным пользователям
def profile(request):
    return render(request, 'main/profile.html')


class BBLogoutView(LoginRequiredMixin, LogoutView):     # LoginRequiredMixin примесь делающая контроллер класс доступным только авторизованным пользователям
    template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):  # 32.3
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):  # наилучший способ получение ключа текущего пользователя
        self.user_id = request.user.pk          # сохраним ключ текущ. пользователя в атрибут user_id
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):    # метод осуществляющий извлечение исправляемой записи по ключу user_id
        if not queryset:                    # если набор записей оказался пустым, получить набор записей
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)     # ищем запись пользователя в наборе


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль успешно изменен'


class RegisterUserView(CreateView):     # 32.4.1.2
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def user_activate(request, sign):       # 32.4.2
    try:
        username = signer.unsign(sign)  # извлекаем имя пользователя из подписи
    except BadSignature:    # если подпись скомпрометирована -то сообщение об ошибке
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)  # берем запись польз из базы по имени
    if user.is_activated:
        template= 'main/user_is_activated.html'     # если пользователь уже активирован то сообщаем об этом
    else:
        template = 'main/activation_done.html'      # если не активирован, то активируем и сохраняем запись
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён.')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def by_rubric(request, pk):
    pass



