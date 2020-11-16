from kivy.app import App
from kivy.uix.button import Button

from kivy.uix.screenmanager import RiseInTransition 
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.config import Config
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.clock import Clock
from time import strftime
import datetime
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.lang import Builder

from kivy.uix.textinput import TextInput 
from kivy.uix.boxlayout import BoxLayout
import urllib

import random

### using chinese charactor ###
import kivy
kivy.resources.resource_add_path('.')  
chinese_ch = kivy.resources.resource_find('STHeiti Medium.ttc')

### network
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import AsyncImage



### textinput ###
Builder.load_string('''
<TreasureInput@TextInput>:
	id: textinput
	multiline: False
	on_text_validate: app.input_ans(self.text)
	font_size: 60
	hint_text: 'Press enter to send your answer'
''')

TIMEOUT = 3.
LOGO = [1, 2, 3, 4, 5, 6]

class TreasureInput(TextInput):
	pass

class RadioButton(ToggleButton):
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)


class Screen_Canvas(Screen):
	pass
	#background_image = ObjectProperty(Image(color = get_color_from_hex('#FFFFFF'), source='pline_background.png'))

#class ScreenManager_Canvas(ScreenManager):
#	background_image = ObjectProperty(Image(color = get_color_from_hex('#FFFFFF'), source='pline_background.png'))

class Physics_nightApp(App):
##### baisc settings #####
	def build(self):
		self.sm = ScreenManager()
		Config.set('graphics', 'width', '375')
		Config.set('graphics', 'height', '667')

		Clock.schedule_interval(self.update_time, 1)

		self.username = '' ### start setting
		self.money = 900 ### start setting		
		self.storystate = '00000000000000000000000000000000000' ### start setting
		self.processions_list = []


		self.product_list = []	
		self.url_image = []
		self.state = 1
		self.storynum = 0
		self.busy = 0
		self.linename = 'p'

		self.doing_create = 0 # to create new id
		self.doing_loginout = 0 # to log in without internet, which is in 'Login' screen
		self.doing_treasure = 0 # to use key to open the treasure, which is in 'Home' screen
		self.doing_exchange = 0 # to press the products icon to exchange with coins, which is in 'Home' screen
		self.doing_network = 0 # to enter shoppping mall but without internet, which is in 'Home' screen
		self.doing_homeloading = 0 # to wait for connecting, which is in 'Home' screen
		self.doing_loginloading = 0 #to wait for connecting, which is in 'Login' screen
		self.doing_shoploading = 0 #to wait for connecting, which is in 'P_coin_exchange' screen
		
		self.start_counting = 0 # to dealing with loading
		self.seconds = 0 #to dealing with loading

		self.product_id = 0
		
		All = ToggleButtonBehavior.get_widgets('all_line')
		for i in All:
			i.state = 'normal'

		return self.sm

	def on_start(self): ### read username, storystate, money and procession list
		
		f = open('user.txt', 'r') ### username
		self.username = f.readline()
		f.close()
		if(self.username == ''): ### Log out state
			return

		### Log in state ###
		f = open('storystate.txt', 'r') ### storystate and money
		self.storystate = f.readline()
		self.storystate = self.storystate[:-1]
		self.money = int(f.readline())
		f.close()

		self.processions_list = []
		f = open('processions_list.txt', 'r')
		string = f.readline().split(' ')
		while(string[0] != ''):
			self.processions_list.append({'item_name': int(string[0]), 'item_quantity': int(string[1])})
			string = f.readline().split(' ')

		for i in range(35):
			if(self.storystate[i] == '1'):
				digit = chr(ord('0') + int((i + 1) / 10)) + chr(ord('0') + int((i + 1) % 10))
				self.root.ids["all_line_" + digit].background_normal = 'cyan_dot.png' 

		self.sm.current = 'Home'
		self.root.ids.username_label.text += self.username ### right, top, Label of username
		self.root.ids.username_label_y.text += self.username ### right, top, Label of username
		self.root.ids.username_label_h.text += self.username ### right, top, Label of username
		return

	def start_game(self): ### Logout state
		if(self.busy == 1): return
		self.doing_loginloading = 1
		self.busy = 1
	
		self.logo_loginloading = Image(source = 'logo_' + str(random.choice(LOGO)) + '.png',  opacity = 0.8, allow_stretch = True, keep_ratio = True)
		self.image_loginloading = Image(color = get_color_from_hex('#FFFFFF'),  opacity = 0.8, size = (.3 * self.root.width, .1 * self.root.height), pos = (.7 * self.root.width, .9 * self.root.height))
		self.box_loginloading = BoxLayout(size = (.3 * self.root.width, .1 * self.root.height), size_hint = (None, None), pos = self.image_loginloading.pos, orientation = 'vertical', spacing = 0, padding = 0)
		self.loginloading_text = Label(halign = 'center', font_size = 30, text = 'Loading......', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box_loginloading.width, None))
		self.box_loginloading.add_widget(self.loginloading_text)
			
		self.root.ids.id_login.add_widget(self.logo_loginloading)
		self.root.ids.id_login.add_widget(self.image_loginloading)
		self.root.ids.id_login.add_widget(self.box_loginloading)

		self.start_counting = 1
		self.seconds = 0
	
		###############################
		#params = urllib.parse.urlencode({'username': 'superuser', 'password': 'test1234'})
		self.doing_loginout = 1
		params = urllib.urlencode({'username': self.root.ids.username.text, 'password': self.root.ids.password.text})
		headers = {'Content-type': 'application/x-www-form-urlencoded'}
		req = UrlRequest('http://hnhn789.pythonanywhere.com/accounts/login/', on_success = self.success_login, on_failure = self.fail_login, req_body = params, req_headers = headers) 
		###############################
		return


	def success_login(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		if(results['success'] == True):
			self.doing_loginout = 0

			self.sm.current = 'Home'
			### read in state ###
			self.username = self.root.ids.username.text
			self.storystate = results['stories']
			self.money = int(results['points'])		


			self.root.ids.username_label.text += str(self.username)
			self.root.ids.username_label_y.text += str(self.username)
			self.root.ids.username_label_h.text += str(self.username)
			
			### write into file ###
			f = open('user.txt','w') ### username
			f.write(self.username)
			f.close()

			f = open('storystate.txt', 'w') ### storystate and money
			f.write(self.storystate + '\n' + str(self.money))
			f.close()


			self.processions_list = [] ### processions list
			f = open('processions_list.txt', 'w') 

			for i in range(len(results['boughtitems'])):
				self.processions_list.append({'item_name': results['boughtitems'][i]['item_name'], 'item_quantity': results['boughtitems'][i]['item_quantity']})
				f.write(str(results['boughtitems'][i]['item_name']) + ' ' + str(results['boughtitems'][i]['item_quantity']) + '\n')
			f.close()
			
            ### story states have to been processed
			All = ToggleButtonBehavior.get_widgets('all_line')
			for i in All:
				i.background_normal = 'gray_dot.png'
				i.state = 'normal'

			for i in range(35):
				if(self.storystate[i] == '1'):
					digit = chr(ord('0') + int((i + 1) / 10)) + chr(ord('0') + int((i + 1) % 10))
					self.root.ids["all_line_" + digit].background_normal = 'cyan_dot.png' 
			return

		else:
			self.busy = 1 ### self.doing_loginout = 1 ###
			self.image_loginout =Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
			self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.35 * self.root.width, .18 * self.root.height))
			self.button.bind(on_press = self.remove_busy)
			self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
			self.loginout_text = Label(font_name = chinese_ch, halign = 'center', font_size = 100, color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), text = results['messages'])
			self.box.add_widget(self.loginout_text)
			self.root.ids.id_login.add_widget(self.image_loginout)
			self.root.ids.id_login.add_widget(self.button)
			self.root.ids.id_login.add_widget(self.box)

			return


	def fail_login(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.doing_loginout = 1
		self.image_loginout =Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.loginout_text = Label(halign = 'center', font_size = 100, color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), text = 'Please make sure the Internet is available.\n')
		self.box.add_widget(self.loginout_text)
		self.root.ids.id_login.add_widget(self.image_loginout)
		self.root.ids.id_login.add_widget(self.button)
		self.root.ids.id_login.add_widget(self.box)
		return


	def create(self):
		if(self.busy == 1): return
		if(self.root.ids.passwordcheck.text != self.root.ids.password.text):
			self.busy = 1
			self.doing_create = 1
			self.image_create =Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
			self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.35 * self.root.width, .18 * self.root.height))
			self.button.bind(on_press = self.remove_busy)
			self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
			self.create_text = Label(halign = 'center', font_size = 100, color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), text = 'Please make sure if passwordcheck is the same as your password!\n')
			self.box.add_widget(self.create_text)
			self.root.ids.id_login.add_widget(self.image_create)
			self.root.ids.id_login.add_widget(self.button)
			self.root.ids.id_login.add_widget(self.box)
			return
	
		self.doing_loginloading = 1
		self.busy = 1

		self.logo_loginloading = Image(source = 'logo_' + str(random.choice(LOGO)) + '.png',  opacity = 0.8, allow_stretch = True, keep_ratio = True)
		self.image_loginloading = Image(color = get_color_from_hex('#FFFFFF'),  opacity = 0.8, size = (.3 * self.root.width, .1 * self.root.height), pos = (.7 * self.root.width, .9 * self.root.height))
		self.box_loginloading = BoxLayout(size = (.3 * self.root.width, .1 * self.root.height), size_hint = (None, None), pos = self.image_loginloading.pos, orientation = 'vertical', spacing = 0, padding = 0)
		self.loginloading_text = Label(halign = 'center', font_size = 30, text = 'Loading......', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box_loginloading.width, None))
		self.box_loginloading.add_widget(self.loginloading_text)
			
		self.root.ids.id_login.add_widget(self.logo_loginloading)
		self.root.ids.id_login.add_widget(self.image_loginloading)
		self.root.ids.id_login.add_widget(self.box_loginloading)



		self.start_counting = 1
		self.seconds = 0

		self.doing_create = 1

		params = urllib.urlencode({'username': self.root.ids.username.text, 'password': self.root.ids.password.text, 'department': self.root.ids.department.text, 'realname' : self.root.ids.realname.text})
		headers = {'Content-type': 'application/x-www-form-urlencoded'}
		req = UrlRequest('http://hnhn789.pythonanywhere.com/accounts/signup/', on_success = self.success_create, on_failure = self.fail_create, req_body = params, req_headers = headers, timeout = TIMEOUT) 

	def success_create(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.image_create =Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.create_text = Label(font_name = chinese_ch, halign = 'center', font_size = 100, color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), text = results['messages'])
		self.box.add_widget(self.create_text)
		self.root.ids.id_login.add_widget(self.image_create)
		self.root.ids.id_login.add_widget(self.button)
		self.root.ids.id_login.add_widget(self.box)

	def fail_create(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.image_create =Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.create_text = Label(font_name = chinese_ch, halign = 'center', font_size = 100, color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), text = 'Please make sure you are connected!')
		self.box.add_widget(self.create_text)
		self.root.ids.id_login.add_widget(self.image_create)
		self.root.ids.id_login.add_widget(self.button)
		self.root.ids.id_login.add_widget(self.box)


	def logout(self):
		if(self.busy == 1): return
		self.doing_homeloading = 1
		self.busy = 1

		self.logo_homeloading = Image(source = 'logo_' + str(random.choice(LOGO)) + '.png',  opacity = 0.8, allow_stretch = True, keep_ratio = True)
		self.image_homeloading = Image(color = get_color_from_hex('#FFFFFF'),  opacity = 0.8, size = (.3 * self.root.width, .1 * self.root.height), pos = (.7 * self.root.width, .9 * self.root.height))
		self.box_homeloading = BoxLayout(size = (.3 * self.root.width, .1 * self.root.height), size_hint = (None, None), pos = self.image_homeloading.pos, orientation = 'vertical', spacing = 0, padding = 0)
		self.homeloading_text = Label(halign = 'center', font_size = 30, text = 'Loading......', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box_homeloading.width, None))
		self.box_homeloading.add_widget(self.homeloading_text)
			
		self.root.ids.id_home.add_widget(self.logo_homeloading)
		self.root.ids.id_home.add_widget(self.image_homeloading)
		self.root.ids.id_home.add_widget(self.box_homeloading)

		self.start_counting = 1
		self.seconds = 0

		params = urllib.urlencode({'username': self.username, 'points': self.money, 'stories': self.storystate})
		headers = {'Content-type': 'application/x-www-form-urlencoded'}
		req = UrlRequest('http://hnhn789.pythonanywhere.com/accounts/logout/', on_success = self.success_logout, on_failure = self.fail_logout, req_body = params, req_headers = headers, timeout = TIMEOUT) 
		return

	def success_logout(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		### write in file ###

		f = open('user.txt', 'w')
		f.write('')
		f.close()
		self.sm.current = 'login'

		self.busy = 1
		self.doing_loginout = 1
		self.image_loginout =Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.loginout_text = Label(font_name = chinese_ch, halign = 'center', font_size = 100, color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), text = 'Successfully logged out!')
		self.box.add_widget(self.loginout_text)
		self.root.ids.id_login.add_widget(self.image_loginout)
		self.root.ids.id_login.add_widget(self.button)
		self.root.ids.id_login.add_widget(self.box)

		self.root.ids.username_label.text = self.root.ids.username_label.text[:-1 * len(self.username)]
		self.root.ids.username_label_y.text = self.root.ids.username_label_y.text[:-1 * len(self.username)]
		self.root.ids.username_label_h.text = self.root.ids.username_label_h.text[:-1 * len(self.username)]

		return

	def fail_logout(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.doing_network = 1
		self.busy = 1
		self.image_network = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.network_text = Label(halign = 'center', font_size = 100, text = 'Disconnected\nPlease make sure the Internet is available and then enter the app again!', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None))
		self.box.add_widget(self.network_text)
		self.root.ids.id_home.add_widget(self.image_network)
		self.root.ids.id_home.add_widget(self.button)
		self.root.ids.id_home.add_widget(self.box)
		return

	def update_time(self, nap): ### update time
		self.root.ids.money.text = ('$ %04d' % self.money)
		self.root.ids.money_y.text = ('$ %04d' % self.money)
		self.root.ids.money_h.text = ('$ %04d' % self.money)

		countdown = datetime.datetime(year=2017, month=04, day=07, hour = 18, minute = 30) - datetime.datetime.now()
		seconds = countdown.seconds % 60
		minutes = int(countdown.seconds / 60) % 60
		hours = int(int(countdown.seconds / 60) / 60)
		self.root.ids.time.text = ('[b][size=30]%d[/size][/b][size=12]days[/size]  %02d[size=12]hr[/size]%02d[size=12]m[/size]%02d[size=12]s[/size]' % (countdown.days, hours, minutes, seconds))
		self.root.ids.time_y.text = ('[b][size=30]%d[/size][/b][size=12]days[/size]  %02d[size=12]hr[/size]%02d[size=12]m[/size]%02d[size=12]s[/size]' % (countdown.days, hours, minutes, seconds))
		self.root.ids.time_h.text = ('[b][size=30]%d[/size][/b][size=12]days[/size]  %02d[size=12]hr[/size]%02d[size=12]m[/size]%02d[size=12]s[/size]' % (countdown.days, hours, minutes, seconds))
		if(self.start_counting):
			self.seconds += nap
		if(self.seconds >= 5 * TIMEOUT):
			if(self.doing_homeloading):
				if(self.doing_loginout):
					self.fail_logout(0, 0)
					return
				if(self.doing_treasure):
					self.fail_treasure(0, 0)
					return
				self.fail_shop(0, 0)
				return
			if(self.doing_loginloading):
				if(self.doing_loginout):
					self.fail_login(0, 0)
					return
				if(self.doing_create):
					self.fail_create(0, 0)
					return
			if(self.doing_shoploading):
				self.fail_buy_in(0, 0)
				return
		return

	def switch(self, linename):
		if(linename == 'y'):
			self.sm.current = 'YLine'
		if(linename == 'p'):
			self.sm.current = 'Home'
			return
		if(linename == 'h'):
			self.sm.current = 'HLine'
			return


	def change_state(self, newstate):###press the bottum button  ### left adding
		if(self.busy): 
			self.root.ids["bottum_" + chr(ord('0') + int(2 * newstate - 1))].state = 'normal'
			self.root.ids["bottum_" + chr(ord('0') + int(2 * self.state - 1))].state = 'down'
			return
		if(self.state == newstate): return ### nothing have to do
		if(newstate == 1):  ### change to the right screen and add or delete text
			self.sm.current = 'Home'
			self.state = 1
			self.root.ids.bottum_1.state = 'down'
			self.root.ids.bottum_3.state = 'normal'
			for i in range(len(self.shopbox)):
				self.root.ids.id_shopgrid.remove_widget(self.shopbox[i])

		if(newstate == 2):
			self.state = 2

			self.doing_homeloading = 1
			self.busy = 1
			
			self.logo_homeloading = Image(source = 'logo_' + str(random.choice(LOGO)) + '.png',  opacity = 0.8, allow_stretch = True, keep_ratio = True)
			self.image_homeloading = Image(color = get_color_from_hex('#FFFFFF'),  opacity = 0.8, size = (.3 * self.root.width, .1 * self.root.height), sin_hint = (None, None), pos = (.7 * self.root.width, .9 * self.root.height))
			self.box_homeloading = BoxLayout(size = (.3 * self.root.width, .1 * self.root.height), size_hint = (None, None), pos = self.image_homeloading.pos, orientation = 'vertical', spacing = 0 , padding = 0)
			self.homeloading_text = Label(valign = 'top', halign = 'center', font_size = 30, text = 'Loading......', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box_homeloading.width, None))
			self.box_homeloading.add_widget(self.homeloading_text)
			
			self.root.ids.id_home.add_widget(self.logo_homeloading)
			self.root.ids.id_home.add_widget(self.image_homeloading)
			self.root.ids.id_home.add_widget(self.box_homeloading)

			self.start_counting = 1
			self.seconds = 0
			
			req = UrlRequest('http://hnhn789.pythonanywhere.com/shop/update/', on_success = self.success_shop, on_failure = self.fail_shop, timeout = TIMEOUT) 
			return

	def success_shop(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.product_list = []
		for i in range(len(results)):
			self.product_list.append({'pk': results[i]['pk'], 'price': results[i]['price'], 'name': results[i]['name'], 'remain': results[i]['remain']})
#			self.product_list.append({'pk': 1, 'price': 1, 'name': '2', 'remain': 2})

		self.sm.current = 'P_coin_exchange'

		self.shopbox = []
		btn = []
		for i in range(len(self.product_list)):
			self.shopbox.append(BoxLayout(orientation = 'vertical', padding = 10, spacing = 10))
			#btn.append(Button(image = AsyncImage(source = str(results[i]['image']))))
			btn.append(Button(text = 'Buy it!'))
			btn[i].fbind('on_press', self.P_coin_exchange, i)

			self.url_image.append(str(results[i]['image']))

			self.shopbox[i].add_widget(AsyncImage(source = str(results[i]['image'])))
			self.shopbox[i].add_widget(btn[i])
			self.shopbox[i].add_widget(Label(halign = 'center', text_size = (.4 * self.root.width, None), font_name = chinese_ch, font_size = 30, text = self.product_list[i]['name'] + ' $' + str(self.product_list[i]['price']) + '\nremain : ' + str(self.product_list[i]['remain'])))
			self.root.ids.id_shopgrid.add_widget(self.shopbox[i])

		return
	def fail_shop(self, request, results):
		self.state = 1

		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)
		
		self.doing_network = 1
		self.busy = 1
		self.image_network = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.network_text = Label(halign = 'center', font_size = 100, text = 'Disconnected\nPlease make sure the Internet is available and then enter the app again!', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None))
		self.box.add_widget(self.network_text)
		self.root.ids.id_home.add_widget(self.image_network)
		self.root.ids.id_home.add_widget(self.button)
		self.root.ids.id_home.add_widget(self.box)
		return


##### 'Son' function, which are usually used by other functions #####

### remove busy condition ###
	def remove_busy(self,state):#press the "back" button
		if(self.start_counting): return ### must be loading

		self.busy = 0
		if(self.doing_homeloading): ### remove loading window -> login screen
			self.doing_homeloading = 0
			self.root.ids.id_home.remove_widget(self.logo_homeloading)
			self.root.ids.id_home.remove_widget(self.image_homeloading)
			self.root.ids.id_home.remove_widget(self.box_homeloading)
			return

		if(self.doing_loginloading): ### remove loading window -> home screen
			self.doing_loginloading = 0
			self.root.ids.id_login.remove_widget(self.logo_loginloading)
			self.root.ids.id_login.remove_widget(self.image_loginloading)
			self.root.ids.id_login.remove_widget(self.box_loginloading)
			return

		if(self.doing_shoploading): ### remove loading window -> shopping mall screen
			self.doing_shoploading = 0
			self.root.ids.id_p_coin_exchange.remove_widget(self.logo_shoploading)
			self.root.ids.id_p_coin_exchange.remove_widget(self.image_shoploading)
			self.root.ids.id_p_coin_exchange.remove_widget(self.box_shoploading)
			return


		if(self.doing_create):
			self.doing_create = 0
			self.root.ids.id_login.remove_widget(self.image_create)
			self.root.ids.id_login.remove_widget(self.button)
			self.root.ids.id_login.remove_widget(self.box)
			return

		if(self.doing_loginout):
			self.doing_loginout = 0
			self.root.ids.id_login.remove_widget(self.image_loginout)
			self.root.ids.id_login.remove_widget(self.button)
			self.root.ids.id_login.remove_widget(self.box)
			return

		if(self.doing_network):
			self.doing_network = 0
			self.root.ids.id_home.remove_widget(self.image_network)
			self.root.ids.id_home.remove_widget(self.button)
			self.root.ids.id_home.remove_widget(self.box)
			self.root.ids.bottum_3.state = 'normal'
			self.root.ids.bottum_1.state = 'down'
			return

		if(self.doing_treasure):
			self.doing_treasure = 0
			self.root.ids.id_home.remove_widget(self.image_treasure)
			self.root.ids.id_home.remove_widget(self.button)
			self.root.ids.id_home.remove_widget(self.box)
			self.root.ids.bottum_2.state = 'normal'
			if(self.state == 1): self.root.ids.bottum_1.state = 'down'
			else: self.root.ids.bottum_3.state = 'down'
			return

		if(self.doing_exchange):
			self.doing_exchange = 0
			self.root.ids.id_p_coin_exchange.remove_widget(self.image_exchange)
			self.root.ids.id_p_coin_exchange.remove_widget(self.box)
			self.root.ids.id_p_coin_exchange.remove_widget(self.button)
			return

		if(self.state == 1):
			self.sm.current = 'Home'
			self.storystring = ''
			digit = chr(ord('0') + int(self.storynum / 10)) + chr(ord('0') + int(self.storynum % 10))
			self.root.ids["all_line_" + digit].state = 'normal'
			return 

##### 'Parents' functions #####

### P_coin adding or consuming ###
	def p_coin_add(self, money):
		self.money += int(money)
		f = open('storystate.txt', 'w') ### save to file(storystate.txt)
		f.write(self.storystate + '\n' + str(self.money))
		f.close()

### Activation of New Story dot ###
	def storystate_activate(self):
		for i in range(35): ### check for story completeness
			if(self.storystate[i] == '0'): break
			if(i == 34): 
				return
		r = random.choice([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34]) ### random generation
		while(self.storystate[r] == '1'):### check
			r = random.choice([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34])

		digit = chr(ord('0') + int((r + 1)/ 10)) + chr(ord('0') + int((r + 1) % 10))
		self.root.ids["all_line_" + digit].background_normal = 'cyan_dot.png' 

		self.storystate = self.storystate[:r] + '1' + self.storystate[(r + 1):]
		f = open('storystate.txt', 'w') ### save to file(storystate.txt)
		f.write(self.storystate + '\n' + str(self.money))
		f.close()

### buy in product ###
	def buy_in(self, product_id): ### product_id is the type of (int)
		done = 0
		for i in range(len(self.processions_list)): ### update processions_list
			if(self.product_list[product_id]['pk'] == int(self.processions_list[i]['item_name'])):
				self.processions_list[i]['item_quantity'] += 1
				done = 1
		if(done == 0):
			self.processions_list.append({'item_name': self.product_list[product_id]['pk'], 'item_quantity': 1})


		f = open('processions_list.txt', 'w') ### save to file(processions_list.txt)
		for i in range(len(self.processions_list)):
			f.write(str(self.processions_list[i]['item_name']) + ' ' + str(self.processions_list[i]['item_quantity']) + '\n')
		f.close()



### open to read the stories ###
	def change_dot(self, newstorynum):###press the story dot
		if(self.busy == 1): ### let story button to be effectless
			newdigit = chr(ord('0') + int(newstorynum / 10)) + chr(ord('0') + int(newstorynum % 10))
			self.root.ids["all_line_" + newdigit].state = 'normal'
			return
		if(self.state == 1): ### only when state = 1 && busy == 0 can operate
			newdigit = chr(ord('0') + int(newstorynum / 10)) + chr(ord('0') + int(newstorynum % 10))
			if(self.storystate[newstorynum - 1] == '1'):
				self.busy = 1
				self.storynum = newstorynum			
				self.textfile = open('story_' + newdigit +'.txt', 'r')
				self.storystring = self.textfile.read()
				self.textfile.close()
				#self.storystring = 'test'
				self.sm.current = 'Story_page'
				if(24 >= newstorynum >= 13): self.root.ids.StoryWindow.font_size = 35
				else: self.root.ids.StoryWindow.font_size = 50
				self.root.ids.StoryWindow.text = self.storystring
				return
			self.root.ids["all_line_" + newdigit].state = 'normal'
			return

	
### treasure ###
	def treasure(self):
		if(self.busy): return
		self.doing_treasure = 1
		self.busy = 1
		self.image_treasure = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.8 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.1 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.treasure_text = Label(font_name = chinese_ch, halign = 'center', font_size = 80, text = 'Please Enter the \nKey from QRcode', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None), timeout = TIMEOUT)
		self.textinput = TreasureInput(size = (.7 * self.root.width, .1 * self.root.height))
		self.box.add_widget(self.treasure_text)
		self.box.add_widget(self.textinput)
		self.root.ids.id_home.add_widget(self.image_treasure)
		self.root.ids.id_home.add_widget(self.button)
		self.root.ids.id_home.add_widget(self.box)
		return

	def input_ans(self, inputkey):
		self.doing_homeloading = 1
		self.busy = 1

		self.logo_homeloading = Image(source = 'logo_' + str(random.choice(LOGO)) + '.png',  opacity = 0.8, allow_stretch = True, keep_ratio = True)
		self.image_homeloading = Image(color = get_color_from_hex('#FFFFFF'),  opacity = 0.8, size = (.3 * self.root.width, .1 * self.root.height), pos = (.7 * self.root.width, .9 * self.root.height))
		self.box_homeloading = BoxLayout(size = (.3 * self.root.width, .1 * self.root.height), size_hint = (None, None), pos = self.image_homeloading.pos, orientation = 'vertical', spacing = 0 , padding = 0)
		self.homeloading_text = Label(halign = 'center', font_size = 30, text = 'Loading......', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box_homeloading.width, None))
		self.box_homeloading.add_widget(self.homeloading_text)
			
		self.root.ids.id_home.add_widget(self.logo_homeloading)
		self.root.ids.id_home.add_widget(self.image_homeloading)
		self.root.ids.id_home.add_widget(self.box_homeloading)

		self.start_counting = 1
		self.seconds = 0

		req = UrlRequest('http://hnhn789.pythonanywhere.com/QRcode/' + self.username + '/' + inputkey + '/', on_success = self.success_treasure, on_failure = self.fail_treasure, timeout = TIMEOUT)
		return

	def success_treasure(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.treasure_text.text = results['messages']
		if(results['success'] == True):
			self.p_coin_add(int(results['point_received']))
			self.storystate_activate()
			self.treasure_text.text += '\nYou get ' + str(results['point_received']) + 'points !'
		self.box.remove_widget(self.textinput)
		return

	def fail_treasure(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.treasure_text.text = 'Disconnected\nPlease make sure the Internet is available and then enter the app again!'
		self.box.remove_widget(self.textinput)
		return

### P_coin ###
	def P_coin_exchange(self, product_id, obj): ### press the icon of the product to exchange product with P_coin
		if(self.busy == 1): return
		self.busy = 1
		self.doing_exchange = 1
		self.product_id = product_id

		self.image_exchange = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))

		self.button_yes = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.175 * self.root.width, .18 * self.root.height))
		self.button_yes.bind(on_press = self.yes_exchange)

		self.button_no = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'no.png', background_down = 'no.png', pos = (.525 * self.root.width, .18 * self.root.height))
		self.button_no.bind(on_press = self.no_exchange)

		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.exchange_text = Label(halign = 'center', font_size = 100, text = 'Do you really want to make buy it?', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None))
		self.box.add_widget(self.exchange_text)
		
		self.root.ids.id_p_coin_exchange.add_widget(self.image_exchange)
		self.root.ids.id_p_coin_exchange.add_widget(self.button_yes)
		self.root.ids.id_p_coin_exchange.add_widget(self.button_no)
		self.root.ids.id_p_coin_exchange.add_widget(self.box)
		return

	def yes_exchange(self, state): ### exchange with p_coin
		self.root.ids.id_p_coin_exchange.remove_widget(self.button_yes)
		self.root.ids.id_p_coin_exchange.remove_widget(self.button_no)
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.root.ids.id_p_coin_exchange.add_widget(self.button)

		self.doing_shoploading = 1
		self.busy = 1


		self.logo_shoploading = Image(source = 'logo_' + str(random.choice(LOGO)) + '.png',  opacity = 0.8, allow_stretch = True, keep_ratio = True)
		self.image_shoploading = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.3 * self.root.width, .1 * self.root.height), pos = (.7 * self.root.width, .9 * self.root.height))
		self.box_shoploading = BoxLayout(size = (.3 * self.root.width, .1 * self.root.height), size_hint = (None, None), pos = self.image_shoploading.pos, orientation = 'vertical', spacing = 0 , padding = 0)
		self.shoploading_text = Label(halign = 'center', font_size = 30, text = 'Loading......', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box_shoploading.width, None))
		self.box_shoploading.add_widget(self.shoploading_text)
		self.root.ids.id_p_coin_exchange.add_widget(self.logo_shoploading)
		self.root.ids.id_p_coin_exchange.add_widget(self.image_shoploading)
		self.root.ids.id_p_coin_exchange.add_widget(self.box_shoploading)

		self.start_counting = 1
		self.seconds = 0


		req = UrlRequest('http://hnhn789.pythonanywhere.com/shop/' + self.username + '/' + str(self.product_list[self.product_id]['pk']) + '/', on_success = self.success_buy_in, on_failure = self.fail_buy_in, timeout = TIMEOUT)
		return

	def success_buy_in(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.exchange_text.font_name = chinese_ch
		self.exchange_text.text = results['messages']
		if(results['success'] == True):
			self.p_coin_add( -1. * self.product_list[self.product_id]['price'])
			self.buy_in(self.product_id)
			self.product_list[self.product_id]['remain'] -= 1
			self.shopbox[self.product_id].children[0].text = self.product_list[self.product_id]['name'] + ' $' + str(self.product_list[self.product_id]['price']) + '\nremain : ' + str(self.product_list[self.product_id]['remain'])
		return

	def fail_buy_in(self, request, results):
		self.seconds = 0
		self.start_counting = 0
		self.remove_busy(0)

		self.busy = 1
		self.exchange_text.text = 'Disconnected'
		return

	def no_exchange(self, state): ### don't want to make exchangement
		self.root.ids.id_p_coin_exchange.remove_widget(self.button_yes)
		self.root.ids.id_p_coin_exchange.remove_widget(self.button_no)
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.root.ids.id_p_coin_exchange.add_widget(self.button)
		self.exchange_text.text = ('Nothing happened!!\n You have \n%d\n p-coins now' % self.money)

### Processions ###
	def processions(self, string): ### in or out of your backpack
		if(self.busy): return

		if(string == 'in'):
			self.sm.current = 'Your_Processions'

			self.processionsbox = []
	
			for i in range(len(self.processions_list)):
				###  item_name(pk) -> idx(index)
				if(self.processions_list[i]['item_name'] <= 11):
					idx = self.processions_list[i]['item_name'] - 1
				else:
					idx = self.processions_list[i]['item_name'] - 2
				self.processionsbox.append(BoxLayout(orientation = 'vertical'))
				self.processionsbox[i].add_widget(AsyncImage(source = self.url_image[idx]))
				#self.processionsbox[i].add_widget(btn[i])
				self.processionsbox[i].add_widget(Label(text_size = (.4 * self.root.width, None), font_name = chinese_ch, font_size = 30, text = self.product_list[idx]['name'] + ' $' + str(self.product_list[idx]['price']) + '\nI have : ' + str(self.processions_list[i]['item_quantity'])))
				self.root.ids.id_processionsgrid.add_widget(self.processionsbox[i])

			return
		if(string == 'out'):
			self.sm.current = 'P_coin_exchange'
			for i in range(len(self.processions_list)):
				self.root.ids.id_processionsgrid.remove_widget(self.processionsbox[i])
			return

if __name__ == '__main__':
	#Config.set('graphics', 'width', '375')
	#Config.set('graphics', 'height', '667')
	#Config.set('input', 'mouse', 'mouse,disable_multitouch')
	#from kivy.core.window import Window
	#Window.clearcolor = get_color_from_hex('#FFFFFF')

	Physics_nightApp().run()