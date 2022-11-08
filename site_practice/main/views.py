from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView    #32.3 редактирование данных пользователя
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import *
from .forms import *


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


