"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve
from django.shortcuts import render_to_response
from main.views import index
from payments.models import User
import mock

#for TestCase the data is cleared out after each test so we need to re-insert user ecc
#TransactionTestCase the data is cleared out at the end of run.(after completing every tests)

class MainPageTests(TestCase):

	#### SETUP ####

	#Create a method that will run prior each tests
	"""Means: created when the class is initialized, and then used for all tests,
	   Without the classmethod it would be created a new one(setUp) before each tests.
	   Use without the class method when you need to isolate each test run"""
	@classmethod 
	def setUpClass(cls):
		super(MainPageTests, cls).setUpClass()#Call the setUpClass method on the parent class of UserModelTest and pass in one argument cls.
		#creating a mock request object so we can manipulate session
		request_factory = RequestFactory()
		cls.request = request_factory.get('/') #this is a web request by the client
		cls.request.session = {} #create a session


	#### TESTING ROUTES ####

	def test_root_resolves_to_main_view(self):
		main_page = resolve('/')
		self.assertEqual(main_page.func, index)

	def test_returns_appropiate_html(self):
		resp = index(self.request) #get() return  the appropiate html
		self.assertEqual(resp.status_code, 200) #check only the status_code


		#### TESTING TEMPLATES AND VIEWS ####

	def test_returns_exact_html(self):
		resp = index(self.request)
		self.assertEqual(
			resp.content, #html of index 
			render_to_response("index.html").content #html of index.html template
		)

	#Integration tests(group tests that will test more funcs or that calls the real db)

	def test_index_handles_logged_in_user(self):
		#user.save() #commit to db, if using mock we don't need to save to db
		self.request.session = {"user": "1"}

		with mock.patch('main.views.User') as user_mock:
			#When we come across the User obj in main.views, 
			#call our mock_object instead of the real one

			#Tell mock what to do when called:
			#When get is called on our User.objects mock, just return our dummy user
			config = {'get_by_id.return_value': mock.Mock()}
			user_mock.objects.configure_mock(**config)

			#request the index page----> call the index func
			resp = index(self.request)
			self.request.session = {} #return the session back to normal so it won't affect other tests

			#verify the return of the user.html page
			expected_html = render_to_response('user.html', 
				{'user': user_mock.get_by_id(1)}
			)
			self.assertEqual(resp.content, expected_html.content)
