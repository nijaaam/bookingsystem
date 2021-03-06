from django.test import TestCase, Client, RequestFactory, LiveServerTestCase
from selenium.webdriver.common.keys import Keys
import json, time
from bksys.models import *
from django.contrib.sessions.middleware import SessionMiddleware
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from django.conf import settings
from django.contrib.auth.models import User
from selenium.webdriver.support.ui import Select

class requirementsTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)
        rooms.objects.create(room_name="testing",room_size=10,room_location="loc",room_features="feat")
        self.browser.get(self.live_server_url)

    def insertInput(self,id,value):
        self.browser.find_element_by_id(id).clear()
        self.browser.find_element_by_id(id).send_keys(value)

    def tearDown(self):
        for bk in bookings.objects.all():
            bookings.objects.delete(bk.booking_ref)  
        self.browser.quit()
    
    def testSignUp(self):
        self.browser.find_element_by_xpath("//a[contains(text(), 'Sign Up')]").click()
        self.browser.implicitly_wait(3)
        self.insertInput('id_name','user')
        self.insertInput('id_email','user@user.com')
        self.browser.find_element_by_xpath("//button[contains(text(), 'Sign Up')]").click()
        self.browser.implicitly_wait(3)
        self.browser.find_element_by_xpath("//a[contains(text(), 'Back')]").click()
    
    def testBookRoom(self):
        '''
        Pre-conditions: User needs to have an account
        Post-conditions: Booked room
        Steps: 1) User opens the website
               2) User selects a room
               3) User fills the form
               4) User submits it 
               5) System shows the confirmation of booking
        '''
    	users.objects.create_user('user','yser@user.com')
        self.browser.find_element_by_xpath("//button[contains(text(), 'Book')]").click()
        self.insertInput('contact','contact')
        self.insertInput('description','description')
        select = Select(self.browser.find_element_by_id('recurring'))
        select.select_by_visible_text('Never')
        self.insertInput('search','user')
        self.browser.execute_script("$('#search').typeahead('close');")
        #Submit
        self.browser.find_element_by_xpath("//button[contains(text(), 'Book')]").click()
        self.browser.implicitly_wait(3)
        #Assert Values
        self.assertEqual(self.browser.find_element_by_id('modal_roomname').get_attribute('value'),"testing")
        start_time = self.browser.find_element_by_id('modal_stime').get_attribute('value')
        end_time = self.browser.find_element_by_id('modal_etime').get_attribute('value')
        time.sleep(1)
        self.browser.find_element_by_id('exit_modal1').click()
        booking = bookings.objects.all()[0]
        self.assertEqual(booking.room.room_name,"testing")
        self.assertEqual(str(booking.start_time),start_time.strip())
        self.assertEqual(str(booking.end_time),str(end_time))

    def testUpdateBooking(self):
        room = rooms.objects.create(room_name="test1",room_size=10,room_features="feat",room_location="loc")
        users.objects.create_user('name','email@a.com')
        user_id = users.objects.getUser('name')
        start = datetime.now() + timedelta(minutes=5)
        end = datetime.now() + timedelta(minutes=20)
        bk = bookings.objects.newBooking(
            room.room_id,
            time.strftime("%Y-%m-%d"),
            start.strftime('%H:%M'),
            end.strftime('%H:%M'),
            "contact",
            "description",
            user_id,
        )
        view_booking_path = '//*[@id="bs-example-navbar-collapse-1"]/ul/li[2]/a'
        self.browser.find_element_by_xpath(view_booking_path).click()
        self.insertInput('search','name')
        self.browser.find_element_by_xpath('//*[@id="authUser"]/div/div/span[2]/button').click()
        #Click the first booking
        self.browser.find_element_by_xpath('//*[@id="userBookings"]/div/div[2]/table/tbody/tr[1]/td[5]/div/button').click()
        #update contact and description
        self.insertInput('contact','update_c')
        self.insertInput('description','update_d')
        #open calendar
        self.browser.find_element_by_xpath('//*[@id="openCal"]').click()
        #move an event
        time.sleep(1)
        self.browser.execute_script('testMoveEvent(1)')
        time.sleep(1)
        #update
        self.browser.find_element_by_id('update').click()
        time.sleep(1)
        #exit
        self.browser.find_element_by_id('exit_modal1').click()
        time.sleep(1)
        #asserting fields
        booking = bookings.objects.get(booking_ref=1)
        self.assertEqual(booking.contact,"update_c")
        self.assertEqual(booking.description,"update_d")
        start = datetime.strptime(bk.start_time,"%H:%M") + timedelta(minutes=15)
        end = datetime.strptime(bk.end_time,"%H:%M") + timedelta(minutes=30)
        self.assertEqual(str(booking.start_time),start.strftime("%H:%M:%S"))
        self.assertEqual(str(booking.end_time),end.strftime("%H:%M:%S"))

    def testCancelBooking(self):
        room = rooms.objects.create(room_name="test1",room_size=10,room_features="feat",room_location="loc")
        users.objects.create_user('name','email@a.com')
        user_id = users.objects.getUser('name')
        start = datetime.now() + timedelta(minutes=5)
        end = datetime.now() + timedelta(minutes=20)
        bk = bookings.objects.newBooking(
            room.room_id,
            time.strftime("%Y-%m-%d"),
            start.strftime('%H:%M'),
            end.strftime('%H:%M'),
            "contact",
            "description",
            user_id,
        )
        view_booking_path = '//*[@id="bs-example-navbar-collapse-1"]/ul/li[2]/a'
        self.browser.find_element_by_xpath(view_booking_path).click()
        self.insertInput('search','name')
        self.browser.find_element_by_xpath('//*[@id="authUser"]/div/div/span[2]/button').click()
        #Click the first booking
        self.browser.find_element_by_xpath('//*[@id="userBookings"]/div/div[2]/table/tbody/tr[1]/td[5]/div/button').click()
        self.browser.find_element_by_id('cancelBooking').click()
        time.sleep(0.5)
        #click yes
        self.browser.find_element_by_xpath('//*[@id="remCurrent"]').click()
        time.sleep(0.5)
        self.browser.find_element_by_id('exit').click()
        self.assertEqual(len(bookings.objects.all()),0)

    def testRecurringBooking(self):
        users.objects.create_user('user','yser@user.com') #User
        self.browser.find_element_by_xpath("//button[contains(text(), 'Book')]").click()
        #Enter values
        self.insertInput('contact','contact')
        self.insertInput('description','description')
        select = Select(self.browser.find_element_by_id('recurring'))
        select.select_by_visible_text('Weekly')
        self.insertInput('search','user')
        self.browser.execute_script("$('#search').typeahead('close');")
        #Submit
        next_month = datetime.now() + timedelta(days=30)
        self.insertInput('recurr_end',next_month.strftime("%d-%m-%Y"))
        self.browser.find_element_by_xpath("//button[contains(text(), 'Book')]").click()
        time.sleep(2)
        self.browser.find_element_by_id('exit_modal1').click()
        self.assertEqual(len(bookings.objects.all()),5)
    
    def testCancelRecurringBooking(self):
        room = rooms.objects.create(room_name="test1",room_size=10,room_features="feat",room_location="loc")
        users.objects.create_user('name','email@a.com')
        user_id = users.objects.getUser('name')
        start = datetime.now() + timedelta(minutes=5)
        end = datetime.now() + timedelta(minutes=20)
        next_month = datetime.now() + timedelta(days=30)
        bk = bookings.objects.newRecurringBooking(
            room.room_id,
            time.strftime("%Y-%m-%d"),
            start.strftime('%H:%M'),
            end.strftime('%H:%M'),
            "contact",
            "description",
            2,#Weekly
            next_month.strftime("%d-%m-%Y"),
            user_id,
        )
        bk_len = len(bookings.objects.all())
        view_booking_path = '//*[@id="bs-example-navbar-collapse-1"]/ul/li[2]/a'
        self.browser.find_element_by_xpath(view_booking_path).click()
        self.insertInput('search','name')
        self.browser.find_element_by_xpath('//*[@id="authUser"]/div/div/span[2]/button').click()
        #Click the first booking
        self.browser.find_element_by_xpath('//*[@id="userBookings"]/div/div[2]/table/tbody/tr[1]/td[5]/div/button').click()
        self.browser.find_element_by_id('cancelBooking').click()
        #Delete Currrent Event only
        time.sleep(2)
        self.browser.find_element_by_xpath("//button[contains(text(), 'Delete this event only')]").click()
        time.sleep(2)
        self.browser.find_element_by_xpath("//button[contains(text(), 'Close')]").click()
        time.sleep(2)
        self.assertEqual(len(bookings.objects.all()),bk_len-1)
        #Delet All
        view_booking_path = '//*[@id="bs-example-navbar-collapse-1"]/ul/li[2]/a'
        self.browser.find_element_by_xpath(view_booking_path).click()
        self.insertInput('search','name')
        self.browser.find_element_by_xpath('//*[@id="authUser"]/div/div/span[2]/button').click()
        #Click the first booking
        self.browser.find_element_by_xpath('//*[@id="userBookings"]/div/div[2]/table/tbody/tr[1]/td[5]/div/button').click()
        self.browser.find_element_by_id('cancelBooking').click()
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="remAll"]').click()
        time.sleep(1)
        self.browser.find_element_by_xpath("//button[contains(text(), 'Close')]").click()
        time.sleep(1)
        self.assertEqual(len(bookings.objects.all()),0)
    
class validationTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.room = rooms.objects.create(room_name="testing",room_size=10,room_location="loc",room_features="feat")
        self.browser.get(self.live_server_url)

    def insertInput(self,id,value):
        self.browser.find_element_by_id(id).clear()
        self.browser.find_element_by_id(id).send_keys(value)
    
    def tearDown(self): 
        self.browser.quit()
  
    def testPastDates(self):
        date = datetime.now() - timedelta(days=1)
        date = date.strftime("%d-%m-%Y")
        post_time = datetime.now() - timedelta(minutes=10)
        post_time = post_time.strftime('%H:%M')
        self.insertInput('id_date',date)
        self.insertInput('id_time',post_time)
        self.browser.find_element_by_id('find_room_btn').click()
        date = self.browser.find_element_by_id('id_date').get_attribute('value')
        bk_time = self.browser.find_element_by_id('id_time').get_attribute('value')
        self.assertEqual(date,time.strftime("%d-%m-%Y"))
        self.assertEqual(bk_time,time.strftime("%H:%M"))

    def testDuplicateSignup(self):
        users.objects.create_user('name','name@email.com')
        self.browser.find_element_by_xpath("//a[contains(text(), 'Sign Up')]").click()
        self.browser.implicitly_wait(3)
        self.insertInput('id_name','name')
        self.insertInput('id_email','name@email.com')
        self.browser.find_element_by_xpath("//button[contains(text(), 'Sign Up')]").click()
        name_error = self.browser.find_element_by_xpath('//*[@id="username_group"]/span').text
        email_error = self.browser.find_element_by_xpath('//*[@id="email_group"]/span').text
        self.assertEqual(name_error,"Username is taken")
        self.assertEqual(email_error,"Email address is taken")
    

        

