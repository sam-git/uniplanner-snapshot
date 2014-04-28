from django.contrib import messages

def join_course(request, course):
    message = "You have joined %s." %(course.list_name)
    messages.add_message(request, messages.SUCCESS, message)

def create_course(request, course):
    message = "You are the first person to join %s. Get started by adding any upcoming tests and assignments." %(course.list_name)
    messages.add_message(request, messages.SUCCESS, message)

def leave_course(request, course):
    message = "You have left %s." %(course.list_name)
    messages.add_message(request, messages.SUCCESS, message)

def assessment_added(request, course, title):
    message = "%s added." %(title)#, course.list_name)
    messages.add_message(request, messages.SUCCESS, message)

def assessment_updated(request, course, title):
    message = "%s updated." %(title)#, course.list_name)
    messages.add_message(request, messages.SUCCESS, message)

def assessment_deleted(request, course, title):
    message = "%s deleted." %(title)#, course.list_name)
    messages.add_message(request, messages.SUCCESS, message)

# def no_tests_or_assignments(request, course):
#     # message = "Get started by adding a test or assignment to %s" %(course.list_name)
#     message = "It looks like no one has added any tests or assignemnts to %s yet. Why not add one now?" %(course.list_name)
#     messages.add_message(request, messages.INFO, message)
