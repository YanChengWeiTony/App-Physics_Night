#coding=utf-8

#qpy:2

 

from kivy.app import App

from kivy.uix.label import Label

import kivy

kivy.resources.resource_add_path('/System/Library/Fonts')  #指字字体路径

p=kivy.resources.resource_find('STHeiti Medium.ttc')    #指定字体

 

class TestApp(App):

	def build(self):

		return Label(text='一二三',font_name= p)

TestApp().run()

 