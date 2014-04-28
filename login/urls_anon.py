from django.conf.urls import patterns, url

from login import views_anon

urlpatterns = patterns('',

	url(r'^check/$', views_anon.check_email, name='check'),
	
    # url(r'^confirm/$', views_anon.check_email_connect_confirm, name='confirm'),

    # url(r'^unsupportedEmail/$', views_anon.unsupportedEmail, name='unsupportedEmail'),
    url(r'^add/$', views_anon.unsupported_email_add, name='unsupported_email_add'),

)