from django.urls import path, re_path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('imprint/', views.imprint, name='imprint'),
    path('privacy/', views.privacy, name='privacy'),
    path('lobby/<str:instance_name>/<str:participant_label>/', views.lobby, name="lobby"),

    path('user/login/', auth_views.login, { 'template_name': 'om/login.html' }, name='login'),
    path('user/logout/', auth_views.logout, {'template_name': 'om/logout.html' }, name="logout"),

    path('user/new/', views.new_user, name='new_user'),
    path('user/list/', views.list_users, name="list_users"),
    path('user/edit/<int:user_id>', views.edit_user, name="edit_user"),
    path('user/edit/keyfile/', views.change_key_file, name='change_key_file'),
    path('user/password/reset/', auth_views.password_reset, {'template_name': 'om/password_reset.html' }, name='password_reset'),
    path('user/password/reset/done/', auth_views.password_reset_done, {'template_name': 'om/password_reset_done.html' },
    	name='password_reset_done'),
    re_path(r'^user/password/reset/token/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'template_name': 'om/password_reset_confirm.html' }, name='password_reset_confirm'),
    path('user/password/reset/done/', auth_views.password_reset_complete, {'template_name': 'om/password_reset_complete.html' }, name='password_reset_complete'),
    path('user/password/change/', auth_views.password_change, { 'template_name': 'om/password_change.html'}, name='password_change'),
    path('user/password/change/done/', auth_views.password_change_done, { 'template_name': 'om/password_change_complete.html' }, name='password_change_done'),


    path('app/new/', views.new_app, name='new_app'),
    path('app/delete/<int:instance_id>', views.delete, name='delete'),
    path('app/detail/<int:instance_id>', views.detail, name='detail'),
    path('app/restart/<int:instance_id>', views.restart_app, name="restart"),
    path('app/scale/<int:instance_id>', views.scale_app, name="scale_app"),

    path('app/otree/reset_password/<int:instance_id>', views.reset_otree_password, name="reset_otree_password"),
    path('app/otree/change_password/<int:instance_id>', views.change_otree_password, name="change_otree_password"),
    path('app/otree/reset_database/<int:instance_id>', views.reset_database, name="reset_database"),
]