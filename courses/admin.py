from django.contrib import admin
from courses.models import Course, University, Semester, UsersInCourses, Assignment, Test

class StudentsInline(admin.TabularInline): #v5.1 TabularInline
    # model = Course
    model = UsersInCourses
    extra = 1
    readonly_fields = ('student',)

class CourseAdmin(admin.ModelAdmin):
	list_display = ('semester', 'course_subject', 'course_number', 'created_by', 'created_on')
	inlines = [StudentsInline]
	# fields = ['facebook_name', 'uni_email']
	# inlines = [ChoiceInline]

admin.site.register(Course, CourseAdmin)
admin.site.register(University)
admin.site.register(Semester)
admin.site.register(Assignment)
admin.site.register(Test)

# admin.site.register(Student)