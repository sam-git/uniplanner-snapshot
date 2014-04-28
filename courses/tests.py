"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

'''
from login.models import Student
from courses.models import *
from django.db.transaction import *
#rollback()

Semester.objects.all().delete()
University.objects.all().delete()
EmailDomains.objects.all().delete()
TestUser.objects.all().delete()
Course.objects.all().delete()

University.objects.all()

u1 = University(name="The University of Auckland", short_name="UoA")
u1.semester_set.all() #will be empty
u1.save()

#check that adding the same semester to this university doesn't crash.
#this is why i think i need year to be a FIELD and I can;t use unique_for_year on semester name.
#instead i will use unique_together .. .., YEAR
u2 = University(name="Victoria University of Wellington", short_name="Vic")
u2.save()
#http://www.victoria.ac.nz/home/study/publications/dates-2013.pdf
#https://docs.djangoproject.com/en/1.5/intro/tutorial01/


from django.utils import timezone
from datetime import date
#u1.semester_set.create(semester_name='SS', start_date=timezone.now(), end_date=timezone.now())

#2013 academic year
u1.semester_set.create(semester_name='SS', start_date=date(2013,1,4), end_date=date(2013,2,20))
sem1 = u1.semester_set.create(semester_name='S1', start_date=date(2013,3,4), end_date=date(2013,7,1))
sem2 = u1.semester_set.create(semester_name='S2', start_date=date(2013,7,22), end_date=date(2013,11,18))

#2014 academic year
u1.semester_set.create(semester_name='SS', start_date=date(2014,1,6), end_date=date(2014,2,19))
u1.semester_set.create(semester_name='S1', start_date=date(2014,3,3), end_date=date(2014,6,30))
u1.semester_set.create(semester_name='S2', start_date=date(2014,7,21), end_date=date(2014,11,17))

#2013 Vic should crash
u2.semester_set.create(semester_name='S1', start_date=date(2013,3,4), end_date=date(2013,7,1))
u2.semester_set.create(semester_name='S1', start_date=date(2013,3,5), end_date=date(2013,7,1))

for s in Semester.objects.all():
	print s
	s.validate_unique()

u1.emaildomain_set.create(domain="auckland.ac.nz")
u1.emaildomain_set.create(domain="aucklanduni.ac.nz")

c1 = Course(semester=sem1, course_subject="SOFTENG", course_number="725", course_name="Formal Methods")
c1.save()

c2 = Course(semester=sem2, course_subject="SOFTENG", course_number="750", course_name="Advanced SE")
c2.save()

c3 = Course(semester=sem2, course_subject="PSYCH", course_number="107", course_name="Brain Psychology")
c3.save()

user = TestUser(name='Sam', email='sgra168@aucklanduni.ac.nz', university=u1)
user.save()

user.courses.add(c1, c2)
user.courses.all()

c1.testuser_set.all()

c1.assignment_set.create(title='assignmnet 1 c1')
c2.assignment_set.create(title='assignment 2 c2')
c3.assignment_set.create(title='pretend 1')

for course in user.courses.all():
	for ass in course.assignment_set.all():
		print ass

sems = user.university.current_sems
sem = user.university.current_sems[0]

user.courses.filter(semester=user.university.current_sems[0])
'''

'''
from login.models import Student, UsersInCourses
from courses.models import *
from django.db.transaction import *
#rollback()

UsersInCourses.objects.all()
UsersInCourses.objects.all().delete()


sam = Student.objects.all()[0]

c1 = Course.objects.all()[0]

UserInC = UsersInCourses.objects.create(student=sam, course=c1)

c1.student_set
c1.student_set.all()

sam.courses.all()

sams_memb = UsersInCourses.objects.get(course=c1, student=sam)
sams_memb.date_joined


sams_memb2 = c1.usersincourses_set.get(student=sam)

'''