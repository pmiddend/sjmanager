#!/usr/bin/python3

from sjmanager import states

class my_state_object:
	def __init__(self):
		self.iterations = 0

	def initial_state(self,result):
		self.iterations += 1
		print('In initial state')
		result['first_value'] = 1
		if self.iterations == 5:
			return states.return_code_exit()
		else:
			return states.return_code_forward()

	def second_state(self,result):
		print('In second state')
		return states.return_code_forward()

	def third_state(self,result):
		print('In third state')
		return states.return_code_back(2)

m = my_state_object()

states.execute_state_machine(
	m,
	{
		'initial_state' : { 'requires' : set({}), 'provides' : set({}) },
		'second_state' : { 'requires' : set({'first_value'}), 'provides' : set({}) },
		'third_state' : { 'requires' : set({}), 'provides' : set({}) }
	},
	'initial_state',
	[
		{
			'from' : 'initial_state',
			'to' : 'second_state',
		},
		{
			'from' : 'second_state',
			'to' : 'third_state',
			'condition' : lambda menu,result : True
		}
	])
