from django.conf.urls import patterns, include, url

from login import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^overview/$', views.overview, name='overview'),
    url(r'^anon/', include('login.urls_anon', namespace='anon')),

    #I think I need this for forms to redirect to
    url(r'^addEmailToFB/$', views.addEmailToFB, name='addEmailToFB'),

    url(r'^activate/(?P<activation_key>\w+)/$', views.registration_activate, name='registration_activate'),
    url(r'^reset_email/$', views.reset_email, name='reset_email'),

    # url(r'^invite$', views.invite, name='invite'), #test page for invite debugging

    url(r'^notify_when_supported/$', views.notify_when_supported, name='notify_when_supported'),
    url(r'^no_supported_notify/$', views.no_supported_notify, name='no_supported_notify'),
)