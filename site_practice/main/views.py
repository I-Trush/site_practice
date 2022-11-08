from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


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


