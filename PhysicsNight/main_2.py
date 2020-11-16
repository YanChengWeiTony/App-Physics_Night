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

import random

### using chinese charactor ###
import kivy
kivy.resources.resource_add_path('.')  
chinese_ch = kivy.resources.resource_find('STHeiti Medium.ttc')

### network
from kivy.network.urlrequest import UrlRequest



### textinput ###
Builder.load_string('''
<TreasureInput@TextInput>:
	id: textinput
	multiline: False
	on_text_validate: app.input_ans(self.text)
	font_size: 60
	text: 'xxxx'
''')

class FailureMessage(Label):
	pass

class TreasureInput(TextInput):
	pass

class RadioButton(ToggleButton):
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)


class Screen_Canvas(Screen):
	background_image = ObjectProperty(Image(source='pline_background.png'))


class Physics_nightApp(App):
### baisc settings ###
	def build(self):
		self.sm = ScreenManager()
		Config.set('graphics', 'width', '375')
		Config.set('graphics', 'height', '667')

		Clock.schedule_interval(self.update_time, 1)
		self.state = 1
		self.storynum = 0
		self.money = 900
		self.processions_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.busy = 0
		self.doing_treasure = 0
		self.doing_exchange = 0
		self.need_money = 0
		self.choosing_product = 0
		All = ToggleButtonBehavior.get_widgets('p_line')
		for i in All:
			i.state = 'normal'
		return self.sm

	def on_start(self): ### read storystate, money and procession list
		f = open('storystate.txt', 'r')
		self.storystate = f.readline()
		self.storystate = self.storystate[:-1]
		self.money = int(f.readline())
		f.close()

		f = open('processions_list.txt', 'r')
		for i in range(len(self.processions_list)):
			string = f.readline()
			self.processions_list[i] = int(string[:-1])
		f.close()

		for i in range(12):
			if(self.storystate[i] == '1'):
				digit = chr(ord('0') + int((i + 1) / 10)) + chr(ord('0') + int((i + 1) % 10))
				self.root.ids["p_line_" + digit].background_normal = 'cyan_dot.png' 

	def start_game(self):
		pass


	def update_time(self, nap): ### update time
		self.root.ids.money.text = ('$ %04d' % self.money)
		countdown = datetime.datetime(year=2017, month=04, day=07) - datetime.datetime.now()
		seconds = countdown.seconds % 60
		minutes = int(countdown.seconds / 60) % 60
		hours = int(int(countdown.seconds / 60) / 60)
		self.root.ids.time.text = ('[b][size=30]%d[/size][/b][size=12]days[/size]  %02d[size=12]hr[/size]%02d[size=12]m[/size]%02d[size=12]s[/size]' % (countdown.days, hours, minutes, seconds))

	def change_state(self, newstate):###press the bottum button  ### left adding
		if(self.busy): 
			self.root.ids["bottum_" + chr(ord('0') + int(newstate))].state = 'normal'
			self.root.ids["bottum_" + chr(ord('0') + int(self.state))].state = 'down'
			return
		if(self.state == newstate): return ### nothing have to do
		if(newstate == 1):  ### change to the right screen and add or delete text
			self.sm.current = 'Home'
			self.root.ids.product_0.text =  self.root.ids.product_0.text[:-1]
		if(newstate == 2): 
			self.sm.current = 'P_coin_exchange'
			self.root.ids.product_0.text += ('%d' % (4))

		self.state = newstate

### remove busy condition ###
	def remove_busy(self,state):#press the "back" button
		self.busy = 0
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
			self.textfile.close()
			self.storystring = ''
			digit = chr(ord('0') + int(self.storynum / 10)) + chr(ord('0') + int(self.storynum % 10))
			self.root.ids["p_line_" + digit].state = 'normal'
			return 

### open to read the stories ###
	def change_dot(self, newstorynum):###press the story dot
		if(self.busy == 1): ### let story button to be effectless
			newdigit = chr(ord('0') + int(newstorynum / 10)) + chr(ord('0') + int(newstorynum % 10))
			self.root.ids["p_line_" + newdigit].state = 'normal'
			return
		if(self.state == 1): ### only when state = 1 && busy == 0 can operate
			if(self.storystate[newstorynum - 1] == '1'):
				self.busy = 1
				self.storynum = newstorynum			
				self.textfile = open('chinese.txt', 'r')
				self.storystring = self.textfile.read()
				self.sm.current = 'Story_page'
				self.root.ids.StoryWindow.text = self.storystring
				return
			
			newdigit = chr(ord('0') + int(newstorynum / 10)) + chr(ord('0') + int(newstorynum % 10))
			self.root.ids["p_line_" + newdigit].state = 'normal'

	
### treasure ###
	def treasure(self):
		if(self.busy): return
		self.doing_treasure = 1
		self.busy = 1
		self.image_treasure = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.teasure_text = Label(font_name = chinese_ch, halign = 'center', font_size = 100, text = 'Please input your answer', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None))
		self.textinput = TreasureInput(size = (.5 * self.root.width, .1 * self.root.height))
		self.box.add_widget(self.teasure_text)
		self.box.add_widget(self.textinput)
		self.root.ids.id_home.add_widget(self.image_treasure)
		self.root.ids.id_home.add_widget(self.button)
		self.root.ids.id_home.add_widget(self.box)
		return

	def input_ans(self, inputkey):
		req = UrlRequest('http://hnhn789.pythonanywhere.com/QRcode/superuser/' + inputkey + '/', on_success = self.success, on_failure = self.fail)
		return

		keyfile = open('key.txt', 'r')### to find the key for the answer 
		key = keyfile.readline()
		correct = 0
		while(key != ''):### check for whether get the correct answer
			if(inputkey + '\n' == key):
				correct = 1
				break
			key = keyfile.readline()

		keyfile.close()		
		if(correct == 0): ### wrong answer
			self.teasure_text.text = 'Wrong Answer!\nPlease try again!'
			self.box.remove_widget(self.textinput)	
			return		
		completed = 0
		for i in range(0, 12): ### check for story completeness
			if(self.storystate[i] == '0'): break
			if(i == 11): 
				self.teasure_text.text = 'Correct! But you have already won the game!'
				self.box.remove_widget(self.textinput)	
				return

		r = random.choice([0,1,2,3,4,5,6,7,8,9,10,11]) ### random generation
		while(self.storystate[r] == '1'):### check
			r = random.choice([0,1,2,3,4,5,6,7,8,9,10,11])

		digit = chr(ord('0') + int((r + 1)/ 10)) + chr(ord('0') + int((r + 1) % 10))
		self.root.ids["p_line_" + digit].background_normal = 'cyan_dot.png' 

		self.storystate = self.storystate[:r] + '1' + self.storystate[(r + 1):]
		f = open('storystate.txt', 'w') ### save to file(storystate.txt)
		self.money += 10
		f.write(self.storystate + '\n' + str(self.money))
		f.close()
		self.teasure_text.text = 'Correct!\nYou can read new story ' + str(r) + ' now!'
		self.box.remove_widget(self.textinput)
		return	

	def success(self, request, results):
		self.teasure_text.text = results['messages']
		if(results['success'] == True):
			self.money += int(results['point_received'])
			return
		self.teasure_text.text = results['messages']
		return



	def fail(self, request, results):
		self.teasure_text.text = results['messages']


### P_coin ###
	def P_coin_exchange(self, need_money, choosing_product): ### press the icon of the product to exchange product with P_coin
		self.busy = 1
		self.doing_exchange = 1
		self.need_money = need_money
		self.choosing_product = choosing_product

		self.image_exchange = Image(color = get_color_from_hex('#FFFFFF'), opacity = 0.8, size = (.75 * self.root.width, .72* self.root.height), pos = (.125 * self.root.width, .15 * self.root.height))

		self.button_yes = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'yes.png', background_down = 'yes.png', pos = (.175 * self.root.width, .18 * self.root.height))
		self.button_yes.bind(on_press = self.yes_exchange)

		self.button_no = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'no.png', background_down = 'no.png', pos = (.525 * self.root.width, .18 * self.root.height))
		self.button_no.bind(on_press = self.no_exchange)

		self.box = BoxLayout(size = (.6 * self.root.width, .5 * self.root.height), size_hint = (None, None), pos = (.2 * self.root.width, .3 * self.root.height), orientation = 'vertical', spacing = .1 * self.root.height , padding = .1 * self.root.width)
		self.exchange_text = Label(halign = 'center', font_size = 100, text = 'Do you really want to make exchangement?', color = get_color_from_hex('#000000'), markup = True, text_size = (self.box.width, None))
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

		if(self.money < self.need_money):
			self.exchange_text.text = ('Sorry!\nYou do not have enough money!!\n You have \n%d\n p_coin now' % self.money)
		else:
			self.money -= self.need_money
			self.processions_list[self.choosing_product] += 1
		
			self.exchange_text.text = ('You have successfully made exchangement!!\n You have \n%d\n p_coin now' % self.money)
			
			f = open('storystate.txt', 'w') ### save to file(storystate.txt)
			f.write(self.storystate + '\n' + str(self.money))
			f.close()

			f = open('procession_list.txt', 'w') ### save to file(procession_list.txt) ###left adding
			for i in range(len(self.processions_list)):
				f.write(str(self.processions_list[i]) + '\n')
			f.write('end')
			f.close()

		return

	def no_exchange(self, state): ### don't want to make exchangement
		self.root.ids.id_p_coin_exchange.remove_widget(self.button_yes)
		self.root.ids.id_p_coin_exchange.remove_widget(self.button_no)
		self.button = Button(size = (.3 * self.root.width, .06 * self.root.height), size_hint = (None, None), background_normal = 'back.png', background_down = 'back.png', pos = (.35 * self.root.width, .18 * self.root.height))
		self.button.bind(on_press = self.remove_busy)
		self.root.ids.id_p_coin_exchange.add_widget(self.button)
		self.exchange_text.text = ('Nothing happen!!\n You have \n%d\n p_coin now' % self.money)

### Processions ###
	def processions(self, string): ### add or delete text  ###left adding
		if(string == 'in'):
			self.root.ids.processions_0.text += (('%d') % self.processions_list[0])
		if(string == 'out'):
			self.root.ids.processions_0.text = self.root.ids.processions_0.text[:-1]


if __name__ == '__main__':
	#Config.set('graphics', 'width', '375')
	#Config.set('graphics', 'height', '667')
	#Config.set('input', 'mouse', 'mouse,disable_multitouch')
	#from kivy.core.window import Window
	#Window.clearcolor = get_color_from_hex('#000000')

	Physics_nightApp().run()