from django.db import models

# Create your models here.
# from datetime import date 
from django.utils import timezone
# from login.models import Student
from django.core.exceptions import PermissionDenied

class University(models.Model):
    short_name = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    is_supported = models.BooleanField() #empty value = false

    def __unicode__(self):
        return self.name

    def _get_current_sems(self):
        now = timezone.now()
        return self.semester_set.filter(start_date__lt=now, end_date__gt=now)
        # try:
        #     return self.semester_set.get(start_date__lt=now, end_date__gt=now)
        # except Semester.MultipleObjectsReturned:
        #     return "Multiple Options Returned"
        # except Semester.DoesNotExist:
        #     return "No semesters currently defined"
    current_sems = property(_get_current_sems)
        
        # samples = Sample.objects.filter(date__gt=datetime.date(2011, 1, 1),
        #                                 date__lt=datetime.date(2011, 1, 31)


class EmailDomain(models.Model):
    university = models.ForeignKey(University)
    domain = models.CharField(max_length=75, unique=True, primary_key=True)

    def __unicode__(self):
        return self.domain

    #this would potentially be bad. Multiple universities could have the same domain.
    # class Meta:
    #     unique_together = ('university', 'domain')

class Semester(models.Model):
    '''
    An improvement would be to make unique together include a 'year' FIELD.
    At the moment an error is only detected if start_dates match, when in fact an
    error should be detected when years match.
    '''
    university = models.ForeignKey(University)
    start_date = models.DateField()
    end_date = models.DateField()

    SEMESTER_NAMES = (
        ('SS', 'Summer School'),
        ('S1', 'Semester 1'),
        ('S2', 'Semester 2'),
    )
    semester_name = models.CharField(max_length=2,
        choices=SEMESTER_NAMES,
    )

    def _get_year(self):
        if self.start_date.year == self.end_date.year:
            return self.start_date.year
        else:
            return "Cannot determine year"
    year = property(_get_year)

    def __unicode__(self):
        return ' '.join([self.university.short_name, str(self.year), self.semester_name])

    class Meta:
        unique_together = ('university', 'semester_name', 'start_date')

class Course(models.Model):
    semester = models.ForeignKey(Semester)
    #UOA COURSE DETAILS
    course_subject = models.CharField('Course Subject Code', max_length=8)
    course_number = models.CharField('Course Number', max_length=4)
    course_name = models.CharField(max_length=255, blank=True) #length arbitrary
    created_by = models.ForeignKey('login.Student')
    created_on = models.DateTimeField(auto_now_add=True)

    def _get_list_name(self):
        return "{0} {1}".format(self.course_subject, self.course_number)
    list_name = property(_get_list_name)


    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('courses:detail', args=[str(self.id)])

    def __unicode__(self):
        return ' '.join([str(self.semester), self.course_subject, str(self.course_number)])

    #This was used in form validation and we can't use it now as part of the add course form, because
    #semester gets added BEFORE validation.
    # class Meta:
    #     unique_together = ('semester', 'course_subject', 'course_number')

    def save(self, *args, **kwargs):
        #AddCourseForm also make course_subject uppercase. This is a backup for when the AddCourseForm is not used.
        self.course_subject = self.course_subject.upper()
        super(Course, self).save(*args, **kwargs) # Call the "real" save() method.
    

class Assessment(models.Model):
    class Meta:
        abstract = True

    deleted = models.BooleanField() #empty value = false
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255) #length arbitrary    
    weighting = models.DecimalField('Weighting (%)', blank=True, null=True, max_digits=5, decimal_places=2)
    last_edited_by = models.ForeignKey('login.Student', related_name="%(app_label)s_%(class)s_related_last_edited_by")
        # related_name="%(app_label)s_%(class)s_related")
    created_by = models.ForeignKey('login.Student', related_name="%(app_label)s_%(class)s_related_created_by")


    def __unicode__(self):
        return ' '.join([str(self.course), self.title])

    def is_in_past(self):
        return timezone.now().date() > self.due_date

    # def get_absolute_url(self):
    #     from django.core.urlresolvers import reverse
    #     return reverse('courses:detail', args=[str(self.course.id)])

    def save(self, *args, **kwargs):
        if self.course not in self.last_edited_by.courses.all():
            return
        super(Assessment, self).save(*args, **kwargs) # Call the "real" save() method.


class Assignment(Assessment):
    private = models.BooleanField() #empty value = false
    due_date = models.DateField(blank=True, null=True)
    due_time = models.TimeField(blank=True, null=True)
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('courses:ass_detail', kwargs={'course_id':self.course.id, 'assessment_id':self.id})

class Test(Assessment):
    due_date = models.DateField('date', blank=True, null=True)
    due_time = models.TimeField('time', blank=True, null=True)
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('courses:test_detail', kwargs={'course_id':self.course.id, 'assessment_id':self.id})

class UsersInCourses(models.Model):
    course = models.ForeignKey(Course)
    student = models.ForeignKey('login.Student')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')

class TestUser(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(primary_key=True)
    university = models.ForeignKey(University)

    courses = models.ManyToManyField(Course)

    def _get_current_courses(self):
        return self.courses.filter(semester=user.university.current_sems)
    current_courses = property(_get_current_courses)

    # email_domain = models.ForeignKey(EmailDomain)
    # semesters = models.ManyToManyField(Semester)
    

    def __unicode__(self):
        return self.email