"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
# UserConnectTest
from django_facebook.test_utils.testcases import FacebookTest #, LiveFacebookTest
from django_facebook.api import get_facebook_graph, FacebookUserConverter#, get_persistent_graph
from django_facebook.connect import _register_user, connect_user, CONNECT_ACTIONS
from django.contrib.auth.models import AnonymousUser

# from django_facebook import exceptions as facebook_exceptions, \
#     settings as facebook_settings, signals
from django_facebook import settings as facebook_settings

from login import views

# class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.assertEqual(1 + 1, 2)
from django_facebook.auth_backends import FacebookBackend

from django_facebook.utils import cleanup_oauth_url, get_profile_model, \
    ScriptRedirect, get_user_model, get_user_attribute, try_get_profile, \
    get_instance_for_attribute, update_user_attributes

class LodggedIsTests(FacebookTest):

    def setUp(self):
        #class ConnectViewTest(FacebookTest):
        FacebookTest.setUp(self)

        self.base_url = base_url = 'http://testserver'
        self.absolute_default_url = base_url + \
            facebook_settings.FACEBOOK_LOGIN_DEFAULT_REDIRECT
        self.url = reverse('facebook_connect')
        self.absolute_url = base_url + reverse('facebook_connect')
        self.example_url = reverse('facebook_example')
        self.absolute_example_url = base_url + reverse('facebook_example')


    def test_anon_user_loads_index(self):
        graph = get_facebook_graph(access_token='new_user')
        action, user = connect_user(self.request, facebook_graph=graph)

        self.request.user = AnonymousUser()
        response = views.index(self.request)
        print response.cookies
        # print response.context

    def testLoggingInDirect(self):
        pass
        # graph = get_facebook_graph(access_token='short_username')
        # action, user = connect_user(self.request, facebook_graph=graph)
        # user.save()
        
        # self.mock_authenticated()
        # response = self.client.get('/login/')
        # # print response

        # print self.client.login
        # print FacebookBackend.login

    def test_auth_backend(self):
        # the auth backend
        backend = FacebookBackend()
        facebook = get_facebook_graph(access_token='new_user')
        action, user = connect_user(self.request, facebook_graph=facebook)
        facebook_email = user.email
        profile = try_get_profile(user)
        user_or_profile = get_instance_for_attribute(
            user, profile, 'facebook_id')
        facebook_id = user_or_profile.facebook_id
        auth_user = backend.authenticate(facebook_email=facebook_email)

        #I GOT IT WORKING!!!!!!!!!!
        self.client.login(facebook_email=facebook_email)


        # response = self.client.get('/login/?testing=True')
        response = self.client.get('/login/')

        self.assertTemplateUsed(response, )
        template_names = []
        for template in response.templates:
            template_names.append(template.name)
        print template_names



        # logger.info('%s %s %s', auth_user.email, user.email, facebook_email)
        self.assertEqual(auth_user, user)

        auth_user = backend.authenticate(facebook_id=facebook_id)
        self.assertEqual(auth_user, user)

        auth_user = backend.authenticate(facebook_id=facebook_id,
                                         facebook_email=facebook_email)
        self.assertEqual(auth_user, user)

        auth_user = backend.authenticate()
        self.assertIsNone(auth_user)

    # def test_decorator_authenticated(self):
    #     '''
    #     Here we fake that we have permissions
    #     This should enter the view and in this test return "authorized"
    #     '''
    #     self.mock_authenticated()
    #     response = self.client.get(self.url, follow=True)
    #     self.assertEqual(response.content, 'authorized')

    def test_connect_redirect_default(self):
        # Now try without next
        self.mock_authenticated()
        accepted_url = self.url + '?attempt=1&client_id=215464901804004'
        response = self.client.get(accepted_url, follow=True)
        redirect_url = response.redirect_chain[0][0]
        self.assertEqual(redirect_url, self.absolute_default_url)



class UniplannerUserConnectTests(FacebookTest):
    def test_check_connect_facebook(self):
        graph = get_facebook_graph(access_token='new_user')
        facebook = FacebookUserConverter(graph)
        data = facebook.facebook_registration_data()
        self.assertEqual(data['gender'], 'm')

        response = self.client.get(reverse('login:index'))
        # print response.content

    def test_login_with_Facebook2(self):
        graph = get_facebook_graph(access_token='short_username')
        action, user = connect_user(self.request, facebook_graph=graph)
        user.save()
        self.request.user = AnonymousUser()
        graph = get_facebook_graph(access_token='same_username')
        action, new_user = connect_user(self.request, facebook_graph=graph)


        self.request.GET._mutable = True
        self.request.GET['testing'] = 'True'
        response = views.index(self.request)
        print response.content
        # response = self.client.get(reverse('login:index'))
        # print response.content

    def test_login_with_Facebook(self):
        pass


    #line 561 django-facebook/tests.py
    def test_full_connect(self):
        # going for a register, connect and login
        graph = get_facebook_graph(access_token='short_username')
        FacebookUserConverter(graph)
        action, user = connect_user(self.request, facebook_graph=graph)
        self.assertEqual(action, CONNECT_ACTIONS.REGISTER)
        # and now we do a login, not a connect
        action, user = connect_user(self.request, facebook_graph=graph)
        self.assertEqual(action, CONNECT_ACTIONS.LOGIN)
        self.request.GET._mutable = True
        self.request.GET['connect_facebook'] = 1
        action, user = connect_user(
            self.request, facebook_graph=graph, connect_facebook=True)
        self.assertEqual(action, CONNECT_ACTIONS.CONNECT)
        self.request.user = AnonymousUser()
        action, user = connect_user(
            self.request, facebook_graph=graph, connect_facebook=True)
        self.assertEqual(action, CONNECT_ACTIONS.LOGIN)



class AnonUserTests(TestCase):
    #tests 302 status_code after valid email address
    def test_check_post_url_with_post(self):
        response = self.client.post(reverse('login:anon:check'), {'email':'sam@aucklanduni.ac.nz'}, follow=False)
        self.assertEqual(response.status_code, 302)


    #tests 200 status_code after valid email address and following redirect
    def test_check_post_url_redirect_with_post(self):
        response = self.client.post(reverse('login:anon:check'), {'email':'sam@aucklanduni.ac.nz'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        response = self.client.get('/login/')

# >>> response = c.post('/login/check/', {'email':'sam@aucklanduni.ac.nz'}, follow=True)
# >>> response.redirect_chain
# [('http://testserver/login/anon/connect/', 302)]
# >>> response.status_code
# 200
    def test_unsupported_email(self):
        #new way
        response = self.client.post(reverse('login:anon:check'), {'email':'joe@unsupported.ac.nz'}, follow=True)
        self.assertRedirects(response, reverse('login:anon:unsupportedEmail'))

        #original way
        # response = self.client.post(reverse('login:anon:check'), {'email':'joe@unsupported.ac.nz'}, follow=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.context[1]['request'].path, reverse('login:anon:unsupportedEmail'))
        # self.assertEqual(len(response.redirect_chain) , 1)
        # self.assertTrue(response.redirect_chain[0][0].endswith(reverse('login:anon:unsupportedEmail')))
        # self.assertEqual(response.redirect_chain[0][1], 302)

    def test_supported_email(self):
        #new way
        response = self.client.post(reverse('login:anon:check'), {'email':'sam@aucklanduni.ac.nz'}, follow=True)
        self.assertRedirects(response, reverse('login:anon:connect'))

        #original way
        # response = self.client.post(reverse('login:anon:check'), {'email':'sam@aucklanduni.ac.nz'}, follow=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.context[0]['request'].path, reverse('login:anon:connect'))
        # self.assertEqual(response.context[1]['request'].path, reverse('login:anon:connect'))
        # self.assertEqual(len(response.redirect_chain) , 1)
        # self.assertTrue(response.redirect_chain[0][0].endswith(reverse('login:anon:connect')))
        # self.assertEqual(response.redirect_chain[0][1], 302)

    def test_login_with_no_credentials(self):
        self.assertFalse(self.client.login())
        





