from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST

from courses.models import University
from login.models import UnsupportedMailingList

# from login.login_utilities import 
from login.views import isEmailRegistered, matchEmailToUniversity
from login.strings import AnonStrings


# def check_email_connect(request):
#     email = request.session['email']
#     return render(request, 'anon/attachFBtoEmail.html', {'email':email} )

'''removed because only want a single log in flow. This sign up flow ran the risk of 
associating an email address with who ever was logged 
in to facebook on the computer. This may not have been the expected person.'''
# #assume signed in with Facebook now.
# def check_email_connect_confirm(request):
#     if request.user.is_uni_verified():
#         messages.add_message(request, messages.INFO, AnonStrings.FB_ACCOUNT_ALREADY_LINKED_TO_A_UNI_EMAIL)
#         return render(request, "omicron/message.html")

#     # uni_email_status = request.user.uni_email_status
#     email = request.session['email']
#     university_id = request.session['university_id']
#     user = request.user
#     user.addActivationKeyAndEmail(email, university_id)
#     current_site = get_current_site(request)
#     user.sendActivationEmail(current_site)
#     return HttpResponseRedirect(reverse('login:index')) #should this be to where they came from?

@require_POST
def check_email(request):
    email = request.POST['email']
    request.session['email'] = email
    university = matchEmailToUniversity(email)
    if university:
        if not university.is_supported:
            return unsupported_anon_email(request, email, university)
        else:
            return render(request, 'anon/supported_email.html', {
                'email':email,
                'university':university,
                } )
    else:
        return unsupported_anon_email(request, email)

#assume redirected here for check_email.
def unsupported_anon_email(request, email, university=None):
    # email = request.session['email']
    context_dict = {'email':email}
    if university:
        context_dict['university'] = university
    if not email is None:
        return render(request, 'anon/unsupported_email_anon.html', context_dict)
    else:
        #LOG ERROR
        return HttpResponse("unsupported email was blank.")

@require_POST
def unsupported_email_add(request):
    email = request.POST['email']
    usml = UnsupportedMailingList(email=email, notified=False)
    usml.save()
    messages.add_message(request, messages.INFO, "Thanks for registering you interest in UniPlanner. We will endeavour to send you an email when your university is supported.")
    return render(request, 'anon/message.html')
