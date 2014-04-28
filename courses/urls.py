

from django.conf.urls import patterns, url

from courses import views

urlpatterns = patterns('courses.views',

    url(r'^(?P<pk>\d+)/$', views.CourseView.as_view(), name='detail'),
    url(r'^addCourse$', 'addCourse', name='addCourse'),

    url(r'^(?P<course_id>\d+)/leave/$', 'leave', name='leave'),
    url(r'^(?P<course_id>\d+)/join/$', 'join', name='join'), #Join Course  from a course page not currently active feature.

    url(r'^(?P<course_id>\d+)/ass/(?P<assessment_id>\d+)/$', views.redirectToCourse, name='ass_detail'),
    url(r'^(?P<course_id>\d+)/test/(?P<assessment_id>\d+)/$', views.redirectToCourse, name='test_detail'),

    url(r'^(?P<course_id>\d+)/ass/create/$', views.AssCreate.as_view(), name='ass_create'),
    url(r'^(?P<course_id>\d+)/test/create/$', views.TestCreate.as_view(), name='test_create'),

    url(r'^(?P<course_id>\d+)/ass/(?P<pk>\d+)/edit/$', views.AssUpdate.as_view(), name='ass_edit'),
    url(r'^(?P<course_id>\d+)/test/(?P<pk>\d+)/edit/$', views.TestUpdate.as_view(), name='test_edit'),

    url(r'^(?P<course_id>\d+)/ass/(?P<assessment_id>\d+)/delete/$', views.ass_delete, name='ass_delete'),
    url(r'^(?P<course_id>\d+)/test/(?P<assessment_id>\d+)/delete/$', views.test_delete, name='test_delete'),
    
)