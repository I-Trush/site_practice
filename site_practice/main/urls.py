from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/profile/change/<int:pk>/', profile_bb_change, name='profile_bb_change'),
    path('accounts/profile/delete/<int:pk>/', profile_bb_delete, name='profile_bb_delete'),
    path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),   # 34.5.2
    path('accounts/profile/<int:pk>/', profile_bb_detail, name='profile_bb_detail'),    # 34.5 для доступа к деталям объявлений созданных пользователем (для возврата на стр. пользователя кнопкой назад)
    path('accounts/profile/', profile, name='profile'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('account/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),   # для общего доступа к деталям объявлений со страници *по рубрикам*
    path('<int:pk>/', by_rubric, name='by_rubric'),     # если этот маршрут поместить после other_page то django примет этот адрес за имя шаблона страници other_page и выдаст 404
    path('<str:page>/', other_page, name='other'),      # порядок имеет значение
]