from django.db import models

# Create your models here.
from django_facebook.models import FacebookCustomUser
from django.contrib.auth.models import UserManager

from django.core.mail import send_mail

import hashlib
import random
import re

from django.template.loader import render_to_string
from uniplanner.settings import DEFAULT_FROM_EMAIL
from courses.models import University, Course
# from courses import models


# class FacebookCustomUser(AbstractUser, FacebookModel):
class Student(FacebookCustomUser):
    courses = models.ManyToManyField(Course, through='courses.UsersInCourses')

    def _get_current_courses(self):
        return self.courses.filter(semester=self.university.current_sems).order_by('course_subject', 'course_number')
    current_courses = property(_get_current_courses)

    university = models.ForeignKey(University, null=True) #null can't be true (university should always be a value), but I will fix it later.
    uni_email = models.EmailField()

    # receive_uni_notification = models.BooleanField(default=False)
    receive_uni_notification = models.NullBooleanField(null=True)
    activation_key = models.CharField('activation key', max_length=40)

    #redundant fields
    done_survey_1 = models.BooleanField() #empty value = false
    done_survey_2 = models.BooleanField() #empty value = false
    bool_1 = models.BooleanField() #empty value = false
    bool_2 = models.BooleanField() #empty value = false

    NO_UNI_EMAIL = 'NONE'
    ATTACHED_UNI_EMAIL = 'ATCH'
    ACTIVATION_EMAIL_SENT = 'SENT'
    ACTIVATED = 'ACTV'

    UNI_EMAIL_CHOICES = (
        (NO_UNI_EMAIL, 'No Uni Email'),
        (ATTACHED_UNI_EMAIL, 'Uni Email Attached to Account'), #temporary state. user should never see this state.
        (ACTIVATION_EMAIL_SENT, 'Activation Email Sent'),
        (ACTIVATED, 'Activated'),
    )
    uni_email_status = models.CharField(max_length=4,
                                      choices=UNI_EMAIL_CHOICES,
                                      default=NO_UNI_EMAIL)

    def get_sidebar_data(self):
        from courses.forms import AddCourseForm

        sidebar_data = []
        for semester in self.university.current_sems.order_by('start_date'):
            sem_data = {}
            sem_data['semester'] = semester
            sem_data['courses'] = self.current_courses.filter(semester=semester)
            sem_data['add_course_form'] = AddCourseForm(self, initial={'semester':semester})
            sidebar_data.append(sem_data)

        return sidebar_data

    objects = UserManager()

    # def __unicode__(self):
        # return self.uni_email
    def __unicode__(self):
        return ' '.join([self.facebook_name, self.uni_email])

    def is_uni_verified(self):
        if not self.is_authenticated():
            return False
        else:
            return self.uni_email_status == Student.ACTIVATED

    def sendActivationEmail(self, site):
        
        ctx_dict = {
            'activation_key': self.activation_key,
            'site': site,
            'name': self.first_name
        }

        subject = render_to_string('registration/activation_email_subject.txt', ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('registration/activation_email.txt', ctx_dict)

        # user.send_uni_email(subject, message, DEFAULT_FROM_EMAIL)

        send_mail(subject, message, DEFAULT_FROM_EMAIL, [self.uni_email], fail_silently=False)
        self.uni_email_status = Student.ACTIVATION_EMAIL_SENT
        self.save()

    #code taken from django-registration models.py
    def addActivationKeyAndEmail(self, email, university_id):
        self.addUniversity(university_id)

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        username = self.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = hashlib.sha1(salt+username).hexdigest()
        # return self.create(user=user, activation_key=activation_key)
        #LOG print activation_key + email
        self.activation_key = activation_key
        self.uni_email = email
        self.uni_email_status = Student.ATTACHED_UNI_EMAIL
        self.save()

    def activate(self):
        if self.uni_email_status == Student.ACTIVATION_EMAIL_SENT:
            self.uni_email_status = Student.ACTIVATED
            self.save()
            return True
        else: 
            return False

    def addUniversity(self, university_id):
        self.university_id = university_id
        self.save()


class UnsupportedMailingList(models.Model):
    email = models.EmailField(primary_key=True)
    notified = models.BooleanField(default=False)

