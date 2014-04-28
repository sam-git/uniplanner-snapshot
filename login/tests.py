"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from django_facebook.test_utils.testcases import FacebookTest #, LiveFacebookTest
from django_facebook.api import get_facebook_graph#, FacebookUserConverter#, get_persistent_graph
from django_facebook.connect import connect_user#, _register_user, CONNECT_ACTIONS
# from django.contrib.auth.models import AnonymousUser

# # from django_facebook import exceptions as facebook_exceptions, \
# #     settings as facebook_settings, signals
# from django_facebook import settings as facebook_settings

# from login import views

# from django_facebook.auth_backends import FacebookBackend

# from django_facebook.utils import cleanup_oauth_url, get_profile_model, \
#     ScriptRedirect, get_user_model, get_user_attribute, try_get_profile, \
#     get_instance_for_attribute, update_user_attributes

from login.models import Student
from login.strings import ActivationStrings
from login.strings import AnonStrings

acceptedEmail = 'sam@aucklanduni.ac.nz'
acceptedEmail2 = 'chris@aucklanduni.ac.nz'
unacceptedEmail = 'joe@unsupported.ac.nz'

unacceptedEmailDictionary =  {'email': unacceptedEmail }

def makeEmailDict(email):
    return {'email': email}

class LoggedInAndOutTests(FacebookTest):

    def setUp(self):
        FacebookTest.setUp(self)

    #duplicate of LoggedInTests function.
    def login_fb_user(self, access_token):
        facebook = get_facebook_graph(access_token=access_token)
        action, user = connect_user(self.request, facebook_graph=facebook)
        facebook_email = user.email
        self.client.login(facebook_email=facebook_email)

    def logout_fb_user(self):
        response = self.client.get(reverse('auth_logout') + '?next=' + reverse('login:index'), follow=True)
        return response

    def test_university_is_added_when_registering_by_checking_email(self):
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=True)
        
        self.login_fb_user('new_user')
        response = self.client.get(reverse('login:anon:confirm'), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')

        user = response.context['user']
        self.assertIsNotNone(user.university)
        self.assertEqual(user.university_id, "UoA")
        # response = self.client.get(reverse('login:registration_activate', args=[response.context['user'].activation_key]))
        # for message in response.context['messages']:
        #     self.assertEqual(ActivationStrings.ACTIVATE_SUCCESS, message.message)

    def test_email_address_available_to_anon_before_activated(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        response = self.logout_fb_user()
        #Anon user checks unverifed uni_email
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'anon/attachFBtoEmail.html')
        '''
        The difference is the capitalisation of the word "TO"
        anon/attachFBtoEmail.html
        anon/attachFBToEmail.html
        '''

    def test_email_address_taken_when_anon_checks(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        response = self.client.get(reverse('login:registration_activate', args=[response.context['user'].activation_key]))
        response = self.logout_fb_user()
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=True)
        for message in response.context['messages']:
            self.assertEqual(AnonStrings.EMAIL_NOT_AVAILABLE, message.message)

    def test_anon_user_tries_to_sign_up_with_valid_email_but_existing_fb_account(self):
        #create user and activate account
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        response = self.client.get(reverse('login:registration_activate', args=[response.context['user'].activation_key]))

        #logout and check sign-up with a different enaail
        #slight hack. Can't click on button
        response = self.logout_fb_user()

        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail2), follow=True)
        self.assertTemplateUsed(response, 'anon/attachFBtoEmail.html')
        self.login_fb_user('new_user')
        response = self.client.get(reverse('login:anon:confirm'), follow=True)

        for message in response.context['messages']:
            self.assertEqual(AnonStrings.FB_ACCOUNT_ALREADY_LINKED_TO_A_UNI_EMAIL, message.message)

    def test_anon_user_checks_uni_email_then_attaches_fb(self):
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=True)
        self.login_fb_user('new_user')
        response = self.client.get(reverse('login:anon:confirm'), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        response = self.client.get(reverse('login:registration_activate', args=[response.context['user'].activation_key]))
        for message in response.context['messages']:
            self.assertEqual(ActivationStrings.ACTIVATE_SUCCESS, message.message)

class LoggedInTests(FacebookTest):
    def login_fb_user(self, access_token):
        facebook = get_facebook_graph(access_token=access_token)
        action, user = connect_user(self.request, facebook_graph=facebook)
        facebook_email = user.email
        self.client.login(facebook_email=facebook_email)

    def setUp(self):
        FacebookTest.setUp(self)

    def test_new_user_university_added_after_email_sent(self):
        self.login_fb_user('new_user')
        response = self.client.get(reverse('login:index'))
        user = response.context['user']
        self.assertIsNone(user.university)

        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        user = response.context['user']
        self.assertIsNotNone(user.university)
        self.assertEqual(user.university_id, "UoA")

    def test_new_user_sees_add_email(self):
        self.login_fb_user('new_user')
        response = self.client.get(reverse('login:index'))
        self.assertTemplateUsed(response, 'omicron/attachEmailToFB.html')

    def test_new_user_add_valid_email(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')

    def test_new_user_add_invalid_email(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), unacceptedEmailDictionary, follow=True)
        self.assertTemplateUsed(response, 'anon/unsupportedEmail.html')

    #also need to test user state.
    def test_new_user_activation_link_template(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        response = self.client.get(reverse('login:registration_activate', args=[response.context['user'].activation_key]))
        self.assertTemplateUsed(response, 'omicron/message.html')

    #also need to test user state.
    def test_new_user_activation_link_message(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        self.assertTemplateUsed(response, 'omicron/activationEmailSent.html')
        response = self.client.get(reverse('login:registration_activate', args=[response.context['user'].activation_key]))
        for message in response.context['messages']:
            self.assertEqual(ActivationStrings.ACTIVATE_SUCCESS, message.message)

    #works, but I need to do an extra get (response 3), before user shows the correct uni_email state.
    def test_user_email_states(self):
        self.login_fb_user('new_user')
        response0 = self.client.get(reverse('login:index'))
        user0 = response0.context['user']
        #print user0.uni_email_status, user0.id
        self.assertEqual(user0.uni_email_status, Student.NO_UNI_EMAIL)
        response1 = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        user1 = response1.context['user']
        #print user1.uni_email_status, user1.id, self.client.cookies
        self.assertEqual(user1.uni_email_status, Student.ACTIVATION_EMAIL_SENT)
        response2 = self.client.get(reverse('login:registration_activate', args=[response1.context['user'].activation_key]))
        user2 = response2.context['user']
        # I SHOULD CHECK THE MESSAGE HERE TOO PROBABLY
        # for message in response2.context['messages']:
        #     print "user2", message.message
        # FOR SOME REASON uni_email_status IS INCORRECT HERE
        # print "user2", user2.uni_email_status, user2.id, "cookies",self.client.cookies
        response3 = self.client.get(reverse('login:index'))
        # print response3.content
        user3 = response3.context['user']
        # print "user3", user3.uni_email_status, user3.id, self.client.cookies
        self.assertEqual(user3.uni_email_status, Student.ACTIVATED)

    def test_user_email_states_unsupported(self):
        self.login_fb_user('new_user')
        response = self.client.get(reverse('login:index'))
        user = response.context['user']
        self.assertEqual(user.uni_email_status, Student.NO_UNI_EMAIL)
        response = self.client.post(reverse('login:addEmailToFB'), unacceptedEmailDictionary, follow=True)
        user = response.context['user']
        # print response.content
        # print user.uni_email_status
        # self.assertIsNone(user.uni_email_status)
        # self.assertFalse(user.is_authenticated())
        self.assertEqual(user.uni_email_status, Student.NO_UNI_EMAIL)

    def test_add_unsupported_email_template(self):
        self.login_fb_user('new_user')
        response = self.client.post(reverse('login:addEmailToFB'), unacceptedEmailDictionary, follow=True)
        self.assertTemplateUsed(response, 'anon/unsupportedEmail.html')

    #works, but I need to do an extra get (response 3), before user shows the correct uni_email state.
    def test_activation_fails_when_logged_in_with_different_fb_account(self):
        self.login_fb_user('new_user')
        response0 = self.client.get(reverse('login:index'))
        user0 = response0.context['user']
        self.assertEqual(user0.uni_email_status, Student.NO_UNI_EMAIL)
        response1 = self.client.post(reverse('login:addEmailToFB'), makeEmailDict(acceptedEmail), follow=True)
        user1 = response1.context['user']
        self.assertEqual(user1.uni_email_status, Student.ACTIVATION_EMAIL_SENT)

        self.login_fb_user('long_username')
        response2 = self.client.get(reverse('login:registration_activate', args=[response1.context['user'].activation_key]))
        user2 = response2.context['user']
        # for message in response2.context['messages']:
        #     print "user2", message.message
        # print "user2", user2.uni_email_status, user2.id, "cookies",self.client.cookies
        response3 = self.client.get(reverse('login:index'))
        # print response3.content
        user3 = response3.context['user']
        # print "user3", user3.uni_email_status, user3.id, self.client.cookies
        self.assertEqual(user3.uni_email_status, Student.NO_UNI_EMAIL)

class AnonUserTests(TestCase):
    #tests 302 status_code after valid email address
    def test_check_post_url_with_post(self):
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=False)
        self.assertEqual(response.status_code, 200)

    #tests 200 status_code after valid email address and following redirect
    def test_check_post_url_redirect_with_post(self):
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unsupported_email(self):
        #new way
        response = self.client.post(reverse('login:anon:check'), unacceptedEmailDictionary,follow=True)
        # self.assertRedirects(response, reverse('login:anon:unsupportedEmail'))
        self.assertTemplateUsed(response, 'anon/unsupportedEmail.html')

    def test_supported_email(self):
        #new way
        response = self.client.post(reverse('login:anon:check'), makeEmailDict(acceptedEmail), follow=True)
        # self.assertRedirects(response, reverse('login:anon:connect'))
        self.assertTemplateUsed(response, 'anon/attachFBtoEmail.html')

    def test_login_with_no_credentials(self):
        self.assertFalse(self.client.login())
