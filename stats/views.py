from django.shortcuts import render
from login.models import Student
from courses.models import *
from django.db.models import Q
from django.db.models import F
from django.contrib.admin.views.decorators import staff_member_required

fake_course_subjects = ['PENIS', 'SHADS', 'BOOBS', '<I>P</I>', 'POO', 'SHAD', 'WAAAHT', 'FITE ME', 'RYAN']
fake_course_subjects.sort()

def _get_avg_courses_per_student(students):
    if not students:
        return "no students in group"
    total = 0
    for s in students:
        total = total + s.courses.all().count()
    return float(total) / students.count()

def _get_avg_students_per_course(courses):
    if not courses:
        return "no courses in group"
    total = 0
    for c in courses:
        total = total + c.student_set.all().count()
    return float(total) / courses.count()

def _get_avg_assignments_per_course(courses):
    if not courses:
        return "no courses in group"
    total = 0
    for c in courses:
        total = total + c.assignment_set.all().count()
    return float(total) / courses.count()

def _get_avg_tests_per_course(courses):
    if not courses:
        return "no courses in group"
    total = 0
    for c in courses:
        total = total + c.test_set.all().count()
    return float(total) / courses.count()

# Create your views here.
@staff_member_required
def index(request):
    # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    # context = {'latest_poll_list': latest_poll_list}
  
    #query containing all courses for year group X
    c1yr = Course.objects.filter(course_number__startswith='1').exclude(course_subject__in=fake_course_subjects)
    c2yr = Course.objects.filter(course_number__startswith=('2')).exclude(course_subject__in=fake_course_subjects)
    c3yr = Course.objects.filter(course_number__startswith='3').exclude(course_subject__in=fake_course_subjects)
    c4yr = Course.objects.filter(
        Q(course_number__startswith='4') |
        Q(course_number__startswith='7')
        )
    fake_courses = Course.objects.filter(course_subject__in=fake_course_subjects)

    #queries containg all students in at least one course from year group X
    s1yr = Student.objects.filter(usersincourses__course__in=c1yr).distinct()
    s2yr = Student.objects.filter(usersincourses__course__in=c2yr).distinct()
    s3yr = Student.objects.filter(usersincourses__course__in=c3yr).distinct()
    s4yr = Student.objects.filter(usersincourses__course__in=c4yr).distinct()
    s_in_fake_courses = Student.objects.filter(usersincourses__course__in=fake_courses).distinct()

    #queries containing all SE courses for each year level
    se_c2yr = c2yr.filter(course_subject='SOFTENG') 
    se_c3yr = c3yr.filter(course_subject='SOFTENG') 
    se_c4yr = c4yr.filter(course_subject='SOFTENG') 

    #queries containing all students taking a SE course from level X
    se_s2yr = Student.objects.filter(usersincourses__course__in=se_c2yr).distinct()
    se_s3yr = Student.objects.filter(usersincourses__course__in=se_c3yr).distinct()
    se_s4yr = Student.objects.filter(usersincourses__course__in=se_c4yr).distinct()

    data = [

    {'total users' : Student.objects.all().count() }, 
    {'total uni_verified users' : Student.objects.filter(uni_email_status=Student.ACTIVATED).count() },

    {'<hr>': "<h4> Real courses </h4>"},
    # {'total students in 4th years courses' : Student.objects.filter(pk__in=(UsersInCourses.objects.filter(course__in=c4yr)) },

    # {'total first year courses' : Course.objects.filter(course_number__range=(100,199)) },
    {'total first year courses' :  c1yr.count()},
    # {'total second year courses' : Course.objects.filter(course_number__range=(200,299)) },
    {'total second year courses' : c2yr.count() },
    {'total third year courses' :  c3yr.count() },
    {'total fourth year courses' : c4yr.count() },

    {'': "<b>Users in Courses (distint on student)</b>"},
    {'total students in 1st years courses' :s1yr.count() },
    {'total students in 2nd years courses' :s2yr.count() },
    {'total students in 3rd years courses' :s3yr.count() },
    {'total students in 4th years courses' :s4yr.count() },

    {'<hr>': "<h4> Fake courses </h4>"},
    {'known fake course subjects' : ', '.join(fake_course_subjects) },
    {'total fake courses' : fake_courses.count()},
    {'average users per fake course' : _get_avg_students_per_course(fake_courses) },
    {'number of students in a fake course': s_in_fake_courses.count()},
    {'percent of students in a fake course' : float(s_in_fake_courses.count())/Student.objects.all().count() },


    {'<hr>': "<h4> Average Courses per student (includes fake courses)</h4>"},
    {'average courses joined per student' : _get_avg_courses_per_student(Student.objects.all()) },
    {'num students not in a course': Student.objects.filter(courses=None).count()},
    {'avg courses per student for all students in a 1st year course' : _get_avg_courses_per_student(s1yr) },
    {'avg courses per student for all students in a 2nd year course' : _get_avg_courses_per_student(s2yr) },
    {'avg courses per student for all students in a 3rd year course' : _get_avg_courses_per_student(s3yr) },
    {'avg courses per student for all students in a 4th year course' : _get_avg_courses_per_student(s4yr) },

    {'<hr>': "<h4> Creating Courses </h4>"},
    {'Total Courses' : Course.objects.all().count()},
    {'Number of students who have made a course' : Course.objects.all().distinct('created_by').count()},
    {'Percent of students who have made a course' : float(Course.objects.all().distinct('created_by').count())/Student.objects.all().count() },

    {'<hr>': "<h4> Tests </h4>"},
    {'Total Tests' : Test.objects.all().count() },
    {'Total Deleted Tests' : Test.objects.filter(deleted=True).count() },
    {'Number of students who have made a test' : Test.objects.all().distinct('created_by').count()},
    {'Number of students who were last to edit a test' : Test.objects.all().distinct('last_edited_by').count()},
    {'Percent of students who have made a test' : float(Test.objects.all().distinct('created_by').count())/Student.objects.all().count() },
    {'number of tests that were last edited by someone other than creator' : Test.objects.all().count() - Test.objects.filter(created_by=F('last_edited_by')).count()},
    {'average tests per course in 1st year courses' : _get_avg_tests_per_course(c1yr)},
    {'average tests per course in 2nd year courses' : _get_avg_tests_per_course(c2yr)},
    {'average tests per course in 3rd year courses' : _get_avg_tests_per_course(c3yr)},
    {'average tests per course in 4th year courses' : _get_avg_tests_per_course(c4yr)},



    {'<hr>': "<h4> Assignments </h4>"},
    {'Total Assignments' : Assignment.objects.all().count() },
    {'Total Deleted Assignments' : Assignment.objects.filter(deleted=True).count() },
    {'Number of students who have made an assignment' : Assignment.objects.all().distinct('created_by').count()},
    {'Number of students who were last to edit an assignment' : Assignment.objects.all().distinct('last_edited_by').count()},
    {'Percent of students who have made an assignment' : float(Assignment.objects.all().distinct('created_by').count())/Student.objects.all().count() },
    {'number of assignments that were last edited by someone other than creator' : Assignment.objects.all().count() - Assignment.objects.filter(created_by=F('last_edited_by')).count()},
    {'average assignments per course in 1st year courses' : _get_avg_assignments_per_course(c1yr)},
    {'average assignments per course in 2nd year courses' : _get_avg_assignments_per_course(c2yr)},
    {'average assignments per course in 3rd year courses' : _get_avg_assignments_per_course(c3yr)},
    {'average assignments per course in 4th year courses' : _get_avg_assignments_per_course(c4yr)},

    {'<hr />' : '<h4>SoftEng Studens/Facebook Stats</h4>'},
    {'Total Students in 2nd year SE Facebook group:' : '114'},
    {'Total Students in 3rd year SE Facebook group:' : '94'},
    {'Total Students in 4th year SE Facebook group:' : '68'},
    {' ' : ''},
    {'Total Students in a 2nd year SE course:' : se_s2yr.count() },
    {'Total Students in a 3rd year SE course:' : se_s3yr.count() },
    {'Total Students in a 4th year SE course:' : se_s4yr.count() },
    # {'<hr>': "UsersInCourses distint on student"},
    # {'total students in 1st years courses' :UsersInCourses.objects.filter(course__in=c1yr).distinct('student').count() },
    # {'total students in 2nd years courses' :UsersInCourses.objects.filter(course__in=c2yr).distinct('student').count() },
    # {'total students in 43rd years courses' :UsersInCourses.objects.filter(course__in=c3yr).distinct('student').count() },
    # {'total students in 4th years courses' :UsersInCourses.objects.filter(course__in=c4yr).distinct('student').count() },
    # {'<hr>': "UserInCourse NO distinct"},
    # {'total students in 1st years courses' :UsersInCourses.objects.filter(course__in=c1yr).count() },
    # {'total students in 2nd years courses' :UsersInCourses.objects.filter(course__in=c2yr).count() },
    # {'total students in 43rd years courses' :UsersInCourses.objects.filter(course__in=c3yr).count() },
    # {'total students in 4th years courses' :UsersInCourses.objects.filter(course__in=c4yr).count() },
    # {'<hr>':'Students__Usersincourses__course__in'},
    # {'total students in 1st years courses' :Student.objects.filter(usersincourses__course__in=c1yr).count()},
    # {'total students in 2nd years courses' :Student.objects.filter(usersincourses__course__in=c2yr).count()},
    # {'total students in 3rd years courses' :Student.objects.filter(usersincourses__course__in=c3yr).count()},
    # {'total students in 4th years courses' :Student.objects.filter(usersincourses__course__in=c4yr).count()},
    # {'<hr>':'Students__Usersincourses__course__in DISTINT '},
    # {'total students in 1st years courses' :Student.objects.filter(usersincourses__course__in=c1yr).distinct().count()},
    # {'total students in 2nd years courses' :Student.objects.filter(usersincourses__course__in=c2yr).distinct().count()},
    # {'total students in 3rd years courses' :Student.objects.filter(usersincourses__course__in=c3yr).distinct().count()},
    # {'total students in 4th years courses' :Student.objects.filter(usersincourses__course__in=c4yr).distinct().count()},

    # UsersInCourses
    ]

    context = {'data':data}
    context['sam'] = 'Sam'
    
    return render(request, 'stats/stats.html', context)

    # return render(request, 'stats/stats.html')
