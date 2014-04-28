from django.contrib import admin
from login.models import Student
from courses.models import UsersInCourses#, Course


# class ChoiceInline(admin.StackedInline): #v5.0
class CourseInline(admin.TabularInline): #v5.1 TabularInline
    # model = Course
    model = UsersInCourses
    extra = 1
    readonly_fields = ('course',)




class StudentAdmin(admin.ModelAdmin):
	list_display = ('facebook_name', 'last_name', 'uni_email')
	fields = ['facebook_name', 'uni_email', 'uni_email_status', 'is_staff', 'is_superuser' ]
	inlines = [CourseInline]


admin.site.register(Student, StudentAdmin)

# admin.site.register(Student)