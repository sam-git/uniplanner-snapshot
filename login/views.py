from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import RequestContext, loader
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET


from django.db.models import Q

import re #regualr expressions

# from login.views_anon import unsupported_email_add
from login.models import Student

from courses.models import Assignment, Test

from itertools import chain
from operator import attrgetter
from datetime import timedelta

def overview(request):
    user = request.user
    if user.is_authenticated() and user.is_uni_verified(): #"Home View: email verified"
        assignments = Assignment.objects.filter(
            Q(course__in=user.current_courses, due_date__gte=timezone.now(), deleted=False, private=False) |
            Q(course__in=user.current_courses, due_date__gte=timezone.now(), deleted=False, private=True, created_by=user)
        )
        tests = Test.objects.filter(course__in=request.user.current_courses, due_date__gte=timezone.now(), deleted=False)
        #http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
        latest = sorted(list(chain(assignments, tests)), key=attrgetter('due_date'))[:5]

        assignments_next_7_days = Assignment.objects.filter(
            Q(course__in=user.current_courses, due_date__lt=timezone.now()+timedelta(days=7), due_date__gte=timezone.now(), deleted=False, private=False) |
            Q(course__in=user.current_courses, due_date__lt=timezone.now()+timedelta(days=7), due_date__gte=timezone.now(), deleted=False, private=True, created_by=user)
        )
        tests_next_7_days = Test.objects.filter(course__in=request.user.current_courses, due_date__gte=timezone.now(), due_date__lt=timezone.now()+timedelta(days=7), deleted=False)
        
        next_7_days = list(chain(assignments_next_7_days, tests_next_7_days))

        return render(request, 'omicron/userhome.html', { 
            'assignments' : assignments,
            'tests' : tests,
            'latest' : next_7_days,
        })
    else:
        return redirect('login:index')

def index(request):
    user = request.user
    if user.is_authenticated(): #"Home View: User Authenticated" 
        if user.is_uni_verified(): #"Home View: email verified"
            if request.session.get('course', False): #set if viewing a course page and not uni_authenticated.
                url = request.session.get('course')
                try:
                    del request.session['course']
                except KeyError:
                    pass
                return redirect(url)
            else:
                return redirect('login:overview')
        else: #"Home view: uni email not activated"
            return determineUniEmailState(request)
    else:
        current_site = get_current_site(request)
        return render(request, 'omicron/index.html', {'site' : current_site})


def invite(request):
    current_site = get_current_site(request)
    return render(request, 'courses/invite.html', {'site' : current_site})

#assumption that user is authenticated at this point.
def determineUniEmailState(request):
    uni_email_status = request.user.uni_email_status

    if uni_email_status == Student.NO_UNI_EMAIL:
        return render(request, 'omicron/attachEmailToFB.html')

    #abnormal state that could occur if server crashes before sending email after adding it.
    elif uni_email_status == Student.ATTACHED_UNI_EMAIL:
        current_site = get_current_site(request)
        request.user.sendActivationEmail(current_site)
        return HttpResponseRedirect(reverse('login:index')) #should this be to where they came from?
    
    elif uni_email_status == Student.ACTIVATION_EMAIL_SENT:
        return render(request, 'omicron/activationEmailSent.html')
    
    else:
        #LOG ERROR
        messsage = "Something went wrong. Contact support."
        messages.add_message(request, messages.ERROR, message)
        return render(request, "omicron/message.html")

#user should be logged in to Facebook and not have an email address associated with account.
#@login_required #causes error at the moment.
@require_POST
def addEmailToFB(request):
    user = request.user

    #if user in not authenticated the user.is_uni_verified will cause an error, so check must be second
    if user.is_authenticated() and not user.is_uni_verified(): 

        email = request.POST['email']
        university = matchEmailToUniversity(email)
        if university:
            if not university.is_supported:
                # user.delete()
                return unsupportedEmail(request, email, university)
            if isEmailRegistered(email):
                messages.add_message(request, messages.INFO, "Email address already registered with an account.")
                return render(request, 'omicron/message.html')
            else:
                user.addActivationKeyAndEmail(email, university.pk)
                current_site = get_current_site(request)
                user.sendActivationEmail(current_site)
                return HttpResponseRedirect(reverse('login:index')) #should this be to where they came from?
        else:
            # user.delete()
            return unsupportedEmail(request, email)

    else:
        #LOG ERROR
        messages.add_message(request, messages.INFO, "Error adding email address to account.")
        return render(request, "omicron/message.html")

#assume redirected here.
def unsupportedEmail(request, email, university=None):
    # email = request.session['email']
    context_dict = {'email':email}
    if university:
        context_dict['university'] = university
    if not email is None:
        return render(request, 'omicron/unsupported_email_fb.html', context_dict)
    else:
        #LOG ERROR
        return HttpResponse("unsupported email was blank.")

def no_supported_notify(request):
    user = request.user
    if user.is_authenticated():
        uni_email_status = user.uni_email_status
        if uni_email_status == Student.NO_UNI_EMAIL or uni_email_status == Student.ACTIVATION_EMAIL_SENT:
            request.user.delete()
    return redirect('login:index')


def notify_when_supported(request):
    user = request.user
    if user.is_authenticated():
        uni_email_status = request.user.uni_email_status
        if uni_email_status == Student.NO_UNI_EMAIL or uni_email_status == Student.ACTIVATION_EMAIL_SENT:
            request.user.delete()
            from login.views_anon import unsupported_email_add
            return unsupported_email_add(request)
    return redirect('login:index')
        
    # return redirect('login:anon:unsupported_email_add')


def registration_activate(request, activation_key):
    message = attemptActivationAndReturnMessage(activation_key, request.user)
    messages.add_message(request, messages.INFO, message)
    if message == ActivationStrings.ACTIVATE_SUCCESS:
        return redirect('login:index') 
    else:
        return render(request, "omicron/message.html")

from login.strings import ActivationStrings
SHA1_RE = re.compile('^[a-f0-9]{40}$')
def attemptActivationAndReturnMessage(activation_key, current_user):
    # Make sure the key we're trying conforms to the pattern of a
    # SHA1 hash; if it doesn't, no point trying to look it up in
    # the database.
    if not current_user.is_authenticated():
        return ActivationStrings.NOT_LOGGED_IN
    if current_user.is_uni_verified():
            return ActivationStrings.ALREADY_ACTIVATED
    if not SHA1_RE.search(activation_key):
        return ActivationStrings.INVALID_CODE
    try:
        user = Student.objects.get(activation_key=activation_key)
        #LOG
        # print "activation user", user.id
        # print "current user", current_user.id
        if user.is_uni_verified():
            return ActivationStrings.ALREADY_ACTIVATED
        if user.id != current_user.id:
            return "Error. You must be logged in to Uniplanner as %s to activate %s's account." %(user.facebook_name, user.facebook_name) #figure out how to test this String
        else:
            if user.activate():
                return ActivationStrings.ACTIVATE_SUCCESS
            else:
                return ActivationStrings.ERROR
    except Student.DoesNotExist:
        return "Activation code no longer valid."

@login_required
def reset_email(request):
    if request.user.is_authenticated():
        uni_email_status = request.user.uni_email_status
        if uni_email_status == Student.ACTIVATION_EMAIL_SENT:
            request.user.uni_email_status = Student.NO_UNI_EMAIL
    return determineUniEmailState(request)

def isEmailRegistered(email):
    return Student.objects.filter(uni_email=email, uni_email_status=Student.ACTIVATED).exists()

from courses.models import EmailDomain
def matchEmailToUniversity(email):
    email = email.strip()
    domain = email.split('@')[1]
    try: 
        domain = EmailDomain.objects.get(domain=domain)
        return domain.university
    except EmailDomain.DoesNotExist:
        return False
