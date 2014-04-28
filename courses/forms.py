from django import forms
from django.forms import ModelForm
from courses.models import Course, UsersInCourses
from django.core.exceptions import ValidationError



import re
_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))

# class AjaxableResponseMixin(object):
#     """
#     Mixin to add AJAX support to a form.
#     Must be used with an object-based FormView (e.g. CreateView)
#     """
#     def render_to_json_response(self, context, **response_kwargs):
#         data = json.dumps(context)
#         response_kwargs['content_type'] = 'application/json'
#         return HttpResponse(data, **response_kwargs)

#     def form_invalid(self, form):
#         response = super(AjaxableResponseMixin, self).form_invalid(form)
#         if self.request.is_ajax():
#             return self.render_to_json_response(form.errors, status=400)
#         else:
#             return response

#     def form_valid(self, form):
#         # We make sure to call the parent's form_valid() method because
#         # it might do some processing (in the case of CreateView, it will
#         # call form.save() for example).
#         response = super(AjaxableResponseMixin, self).form_valid(form)
#         if self.request.is_ajax():
#             data = {
#                 'pk': self.object.pk,
#             }
#             return self.render_to_json_response(data)
#         else:
#             return response

# class AddCourseForm(AjaxableResponseMixin, forms.ModelForm):
class AddCourseForm(forms.ModelForm):

    #http://stackoverflow.com/questions/8112859/django-how-do-i-add-data-to-a-modelform-subclass-before-validation
    def __init__(self, user, *args, **kwargs):
        super(AddCourseForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Course
        fields = ('course_subject', 'course_number', 'semester')
        widgets = {
            # "semester" : forms.HiddenInput(),
            'course_subject' : forms.TextInput(attrs={'placeholder': 'eg PSYCH'}),
            'course_number' :  forms.TextInput(attrs={'placeholder': 'eg 109'}),
            "semester" : forms.HiddenInput(),
        }

    def clean_course_subject(self):
        if contains_digits(self.cleaned_data['course_subject']):
            raise forms.ValidationError("Course subject cannot contain digits!")
        return self.cleaned_data['course_subject'].upper()

    def clean(self):
        cleaned_data = super(AddCourseForm, self).clean()
        if len(self.user.current_courses) >= 6:
            raise forms.ValidationError("You cannot be in more than 6 course at a time.")
        # Always return the full collection of cleaned data.

        return cleaned_data

    #     cleaned_data = super(AddCourseForm, self).clean()
    #     course_subject = cleaned_data.get("course_subject")
    #     course_number = cleaned_data.get("course_number")

    #     # course = Courses.objects.filter(course_subject='course_subject', course_number='course_number').exists():
    #     if Course.objects.filter(course_subject='course_subject', course_number='course_number').exists():
    #         course = Courses.objects.get(course_subject='course_subject', course_number='course_number')

    #         if UsersInCourses.objects.filter(course=course, course_number='course_number').exists():
    #             raise forms.ValidationError("You are already in this course.")

    #     # Always return the full collection of cleaned data.
    #     return cleaned_data

from courses.models import Assignment, Test
from django.forms.extras.widgets import SelectDateWidget
from courses.select_time_widget import SelectTimeWidget

class AddAssessmentForm(forms.ModelForm):
    class Meta:
        # fields = ('title',)
        fields = ['course', 'title', 'due_date', 'due_time', 'weighting', ]
        # exclude = ('last_edited_by', 'created_by', 'deleted')
        widgets = {
            "course" : forms.HiddenInput(),
            'due_date': SelectDateWidget,
            'due_time' :  forms.TextInput(attrs={'placeholder': 'eg 22:00'}),
            # 'due_time': SelectTimeWidget(hour_step=None, minute_step=5, twelve_hr=False, use_seconds=False),
        }

    def clean_due_date(self):
        course = self.cleaned_data['course']
        if self.cleaned_data['due_date']:
            if not course.semester.start_date <= self.cleaned_data['due_date'] <= course.semester.end_date:
                raise ValidationError('Due date must be during the current semester. %s to %s' %(course.semester.start_date, course.semester.end_date))
        return self.cleaned_data['due_date']

    def clean_title(self):
        return self.cleaned_data['title'].strip()

    def clean_weighting(self):
        if self.cleaned_data['weighting']:
            if not 0 <= self.cleaned_data['weighting'] <= 100:
                raise ValidationError('Weighting must be a percentage between 0 and 100.')
        return self.cleaned_data['weighting']

class AddAssignmentForm(AddAssessmentForm):
    class Meta(AddAssessmentForm.Meta):
        model = Assignment
        fields = ['course', 'title', 'due_date', 'due_time', 'weighting', 'private']

class AddTestForm(AddAssessmentForm):
    class Meta(AddAssessmentForm.Meta):
        model = Test

class EditAssignmentForm(AddAssignmentForm):
    class Meta(AddAssignmentForm.Meta):
        fields = ['course', 'title', 'due_date', 'due_time', 'weighting',] #no 'private'
        # exclude = ('last_edited_by', 'created_by', 'deleted', 'private',)