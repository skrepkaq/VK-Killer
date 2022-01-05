"""social URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from account.views import register_view, login_view, home_view, logout_view, profile_view, myprofile_view, search_view
from account.views import message_view, friends_view, dms_view, myfriends_view, settings_view, post_view, feed_view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('search/', search_view, name='search'),
    path('profile/', myprofile_view, name='myprofile'),
    path('profile/<slug:slug>', profile_view, name='profile'),
    path('friends/', myfriends_view, name='myfriends'),
    path('friends/<slug:slug>', friends_view, name='friends'),
    path('dm/', dms_view, name='dms'),
    path('dm/<slug:slug>', message_view, name='message'),
    path('settings/', settings_view, name='settings'),
    path('post/<int:id>', post_view, name='post'),
    path('feed/', feed_view, name='feed'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='password_reset/index.html',
                                              email_template_name='password_reset/email.txt',
                                              subject_template_name='password_reset/email_subject.txt'),
         name='password_reset'),
    path('password-reset/done',
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset/done.html'),
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset/confirm.html'),
         name='password_reset_confirm'),
    path('password-reset/complete',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/complete.html'),
         name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
