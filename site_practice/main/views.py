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
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView  # 32.4.1.2
from django.core.signing import BadSignature    # 32.4.2
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator     # 34.4.1
from django.db.models import Q


from .models import *
from .forms import *
from .utilities import signer   #32.4.2


def index(request):
    bbs = Bb.objects.filter(is_active=True)[:10]
    context = {'bbs': bbs}
    return render(request, 'main/index.html', context)


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
    bbs = Bb.objects.filter(author=request.user.pk)     #  вывод объявлений оставленных текущим пользователем
    context = {'bbs': bbs}
    return render(request, 'main/profile.html', context)


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
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)


# def detail(request, rubric_pk, pk):
#     bb = get_object_or_404(Bb, pk=pk)
#     ais = bb.additionalimage_set.all()      # 34.4.2 additionalimage_set какой-то втроенный метод - перечень доп иллюстраций
#     context = {'bb': bb, 'ais': ais}
#     return render(request, 'main/detail.html', context)


@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()      # 34.4.2 additionalimage_set какой-то втроенный метод - перечень доп иллюстраций
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/profile_bb_detail.html', context)


@login_required
def profile_bb_add(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset':formset}
    return render(request, 'main/profile_bb_add.html', context)


@login_required
def profile_bb_change(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_change.html', context)


@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'bb': bb}
        return render(request, 'main/profile_bb_delete.html', context)


def detail(request, rubric_pk, pk):     # 35.3
    bb = Bb.objects.get(pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)    # bb=pk? или же bb.pk
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен!')
    context = {'bb': bb,'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)


