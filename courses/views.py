
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse

from django.contrib.sites.models import get_current_site
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator

from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from django.db.models import Q

from courses.forms import AddCourseForm, AddAssignmentForm, AddTestForm, EditAssignmentForm
from courses.models import Course, Assignment, UsersInCourses, Test

from courses import messager

import json
import datetime

def _user_in_course_or_permission_denied(user, course):
    if not user.is_authenticated():
        raise PermissionDenied
    elif course not in user.courses.all():
        raise PermissionDenied

# Create your views here.
class CourseView(generic.DetailView):
    model = Course
    # form = AddAssignmentForm()

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated() and not self.request.user.is_uni_verified():
            self.request.session['course'] = self.request.path
            return redirect('login:index')
        else:
            return super(CourseView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # context = super(CourseView, self).get_context_data(**kwargs)
        # context['number'] = random.randrange(1, 100)
        # return context

        context = super(CourseView, self).get_context_data(**kwargs)
        context['site'] = get_current_site(self.request)
        user = self.request.user
        if user.is_authenticated() and user.is_uni_verified():
            context['active_assignments'] = self.object.assignment_set.filter(
                    Q(deleted=False, private=False) |
                    Q(deleted=False, private=True, created_by=user)
                )
            context['active_tests'] = self.object.test_set.filter(deleted=False)

            context['user_sidebar'] = user.get_sidebar_data()

            context['all_students_in_random_order'] = self.object.student_set.all().order_by('?')

            if self.object in user.current_courses:
                context['leave_link'] = reverse('courses:leave', args=(self.object.id,))
                join_info = self.object.usersincourses_set.get(student=user)
                context['date_joined'] = join_info.date_joined

                # if len(context['active_assignments']) == 0 and len(context['active_tests']) == 0:
                #     messager.no_tests_or_assignments(self.request, self.object)

            elif self.object.semester.university == user.university:
                context['join_link'] = reverse('courses:join', args=(self.object.id,))

        return context

    def get_template_names(self):
        user = self.request.user
        if user.is_authenticated() and user.is_uni_verified():
            if self.object in user.current_courses:
                return 'courses/course_editable.html'
            if self.object.semester.university == user.university:
                return 'courses/course_read_only.html'
        # else :
        return 'courses/course_external.html'

'''
I should get the current semester in this method a better way, or do some sort of check.
'''
@login_required
@require_POST
def addCourse(request):
    if not request.is_ajax():
        return HttpResponseBadRequest()
        pass
    # print "HERE!@$##@$%$#@%$#@%$#@%$@#%"
    # response_data = {}
    # response_data['message'] = 'You messed up bad'
    # response_data = "hey"
    # return redirect('login:index')
    
    # return HttpResponse(json.dumps(response_data), content_type='application/json') 

    form = AddCourseForm(request.user, request.POST)

    if form.is_valid():
        # form.save()
        course_number = form.cleaned_data['course_number']
        course_subject = form.cleaned_data['course_subject'].strip()#.upper()
        semester = form.cleaned_data['semester']

        if request.user.university != semester.university:
            raise PermissionDenied
        if semester not in request.user.university.current_sems:
            raise PermissionDenied

        try:
            course = Course.objects.get(
                course_number=course_number, 
                course_subject=course_subject, 
                semester=semester,
            )
        except Course.DoesNotExist:
            created_by = request.user
            course = Course.objects.create(
                course_number=course_number, 
                course_subject=course_subject, 
                semester=semester,
                created_by=created_by,
            )
            messager.create_course(request, course)
        
        #Using a 'through' table so can't do this anymore.
        #request.user.courses.add(course)

        if not UsersInCourses.objects.filter(course=course, student=request.user).exists():
            m1 = UsersInCourses.objects.create(course=course, student=request.user)
            # messager.join_course(request, course)#  - It is pretty obvious they have joined a course.    
        response_data = {'course_url':course.get_absolute_url()}

    else:
        response_data = {'errors': dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()] ) }

    return HttpResponse(json.dumps(response_data), content_type='application/json') 

# @require_POST
@login_required
def leave(request, course_id):
    user = request.user
    if user.is_authenticated():
        c = get_object_or_404(Course, pk=course_id)
        if c in user.courses.all():
            # user.courses.remove(c) #dones't work suince using 'through'
            c.usersincourses_set.get(student=user).delete()
            messager.leave_course(request, c)
    return redirect('login:index')

# @require_POST
@login_required
def join(request, course_id):
    user = request.user
    if user.is_authenticated():
        c = get_object_or_404(Course, pk=course_id)
        if c.semester.university == user.university:
            if c not in user.courses.all():
                UsersInCourses.objects.create(course=c, student=user)
                messager.join_course(request, c)
                # user.courses.add(c) #dones't work suince using 'through'
    return redirect('courses:detail',  pk=c.id)


#https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
class AssessmentCreate(CreateView):
    '''
    Abstract class.
    In Django 1.6+ I can use the following. Right now I need to do this in the form.
    # exclude = ('course',)
    # fields = ['course']s
    '''
    # template_name_suffix = '_create_form'
    template_name = 'courses/assessment_create.html'

    def get_initial(self):
        initials = {
            "course" : self.kwargs['course_id'],
            'due_date': datetime.datetime.now().date() + datetime.timedelta(days=1),
        }
        return initials

    "context data is used to put Course name on the create page."
    def get_context_data(self, **kwargs):
        context = super(AssessmentCreate, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk=self.kwargs['course_id'])
        return context

    # The following method is no longer needed since Course Model has def get_absolute_url(self):
    # def get_success_url(self):
    #     # print self.form_class
    #     return reverse('courses:detail', args=(self.object.course.id,) ) 

    #see page 260 of django.pdf
    def form_valid(self, form):
        form.instance.last_edited_by = self.request.user
        form.instance.created_by = self.request.user

        messager.assessment_added(self.request, form.instance.course, form.instance.title)
        # form.instance.course_id = self.kwargs['course_id']
        # print self.kwargs['course_id']
        
        #check here that user state is correct etc...
        return super(AssessmentCreate, self).form_valid(form)

    "was using incorrectly returning a permission denied template here originally"
    def get_template_names(self):
        return super(AssessmentCreate, self).get_template_names()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs['course_id'])
        _user_in_course_or_permission_denied(self.request.user, course)
        return super(AssessmentCreate, self).dispatch(*args, **kwargs)

class AssCreate(AssessmentCreate):
    model = Assignment
    def get_form_class(self):
        # if self.request.user.is_authenticated():
        return AddAssignmentForm
    def get_context_data(self, **kwargs):
        context = super(AssCreate, self).get_context_data(**kwargs)
        context['assessment_type'] = 'Assignment'
        return context

class TestCreate(AssessmentCreate):
    model = Test
    def get_form_class(self):
        return AddTestForm
    def get_context_data(self, **kwargs):
        context = super(TestCreate, self).get_context_data(**kwargs)
        context['assessment_type'] = 'Test'
        return context




class AssessmentUpdate(UpdateView):
    '''
    Abstract class.
    '''
    template_name = 'courses/assessment_update.html'
    def get_context_data(self, **kwargs):
        context = super(AssessmentUpdate, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk=self.kwargs['course_id'])
        return context

    def form_valid(self, form):
        form.instance.last_edited_by = self.request.user
        messager.assessment_updated(self.request, form.instance.course, form.instance.title)
        return super(AssessmentUpdate, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs['course_id'])
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        elif course not in self.request.user.courses.all():
            raise PermissionDenied
        return super(AssessmentUpdate, self).dispatch(*args, **kwargs)

#https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/
class AssUpdate(AssessmentUpdate):
    model = Assignment
    def get_form_class(self):
        return EditAssignmentForm

    def get_context_data(self, **kwargs):
        context = super(AssUpdate, self).get_context_data(**kwargs)
        context['assessment_type'] = 'Assignment'
        return context

class TestUpdate(AssessmentUpdate):
    model = Test
    def get_form_class(self):
        return AddTestForm
    def get_context_data(self, **kwargs):
        context = super(TestUpdate, self).get_context_data(**kwargs)
        context['assessment_type'] = 'Test'
        return context


def redirectToCourse(request, course_id, assessment_id=None):
    return redirect('courses:detail', pk=course_id)

@login_required
def ass_delete(request, course_id, assessment_id):
    assignment = get_object_or_404(Assignment, pk=assessment_id, course_id=course_id)
    return _assessment_delete(request, assignment)
    # return HttpResponse("you are a genius, " + course_id + type + assessment_id)

@login_required
def test_delete(request, course_id, assessment_id):
    test = get_object_or_404(Test, pk=assessment_id, course_id=course_id)
    return _assessment_delete(request, test)

#perhaps I should require POST for this view.
def _assessment_delete(request, assessment):
    # if user.
    _user_in_course_or_permission_denied(request.user, assessment.course)
    assessment.deleted = True
    assessment.last_edited_by = request.user
    assessment.save()
    messager.assessment_deleted(request, assessment.course, assessment.title)
    return redirectToCourse(request, assessment.course.id)




