from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from login import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'uniplanner.views.home', name='home'),
    # url(r'^uniplanner/', include('uniplanner.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')), #Don't add this line if you use django registration or userena for registration and auth.

    url(r'^', include('login.urls', namespace='login')),

    url(r'^courses/', include('courses.urls', namespace='courses')),
    url(r'^stats/', 'stats.views.index', name='test_delete'),

#https://docs.djangoproject.com/en/1.5/howto/static-files/#serving-files-uploaded-by-a-user
) #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #this works but i need to remove it for deployment for safety.

# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
