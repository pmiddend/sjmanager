# Man definiert einen Graphen. Die Knoten sind die Funktionen
# (continue_or_new_show, ...), die Kanten sind die Übergänge.
#
# Jeder Übergang hat noch eine Bedingung in Form einer Funktion an
# sich drankleben.
#
# Es wird ein "result"-Dictionary angelegt, wo die Zustände ihre Resultate
# reinlegen können, damit andere Zustände darauf zugreifen können. Man
# kann auch einen Übergang von diesem result-Dictionary abhängig
# machen.
#
# Außerdem wird eine History geführt in Form eines Arrays, wo die
# vergangenen Zustände drinstehen.
#
# Ein Knoten im Graphen (also eine Funktion) kann zwei "Returncodes"
# zurückgeben: Entweder "nächster Zustand" oder "zum n'ten vorherigen
# Zustand"
#
# Die Zustände sind Methoden eines Objekts. Daher wird bei
# execute_state_machine unten noch ein "my_object" übergeben.

from sjmanager.log import log

# Siehe unten
class return_code_back:
	def __init__(self,levels = None):
		if levels == None:
			levels = 1
		assert levels >= 1
		self.levels = levels

class return_code_forward:
	pass

class return_code_exit:
	pass

def execute_state_machine(
	state_object,
	state_infos,
	initial_state,
	transitions):

	for state,info in state_infos.items():
		if 'provides' not in info or 'requires' not in info:
			raise Exception("The state '{}' lacks at least one of the required fields 'requires', 'provides'".format(state))

		if getattr(state_object,state,None) == None:
			raise Exception("The state '{}' is not defined in the state class".format(state))

		if isinstance(info['provides'],dict) or isinstance(info['requires'],dict):
			raise Exception("The 'provides' and 'requires' attributes of '{}' are dicts".format(state))


	for transition in transitions:
		if 'from' not in transition or 'to' not in transition:
			raise Exception("The transition '{}' lacks at least one of the required fields 'from', 'to'".format(transition))

		if getattr(state_object,transition['from'],None) == None:
			raise Exception("The method '{}' is not defined in the state class".format(transition['from']))

		if getattr(state_object,transition['to'],None) == None:
			raise Exception("The method '{}' is not defined in the state class".format(transition['to']))

		if transition['from'] not in state_infos:
			raise Exception("The state '{}' is not defined in the state information".format(transition['from']))

		if transition['to'] not in state_infos:
			raise Exception("The state '{}' is not defined in the state information".format(transition['to']))

	result = {}
	current_state = initial_state
	history = []

	while True:
		if not state_infos[current_state]['requires'].issubset(result.keys()):
			raise Exception("Requirement violation: State {} didn't get {}".format(current_state,state_infos[current_state]['requires'] - result.keys()))


		return_code = getattr(state_object,current_state)(
			result)

		# We want "transient" states like "Display an error dialog" not to appear
		# in the history. Also, currently, we don't want the same state twice in a
		# row in the history. This happens with "resolve_linklist", for example.
		# Preventing this behavior is just a quick fix, however.
		if (not 'nohistory' in state_infos[current_state]) and (len(history) == 0 or history[len(history)-1] != current_state):
			history.append(
				current_state)
		log('Executed command. History is {}'.format(history))

		# Check what needs to be done
		if isinstance(return_code,return_code_back):
			assert len(history) >= return_code.levels
			# Set new current state
			current_state = history[len(history) - return_code.levels - 1]
			# Cut down history
			history = history[0:len(history) - return_code.levels - 1]
		elif isinstance(return_code,return_code_forward):
			if not state_infos[current_state]['provides'].issubset(result.keys()):
				raise Exception(
					"Provides violation: State {} should provide {}, but didn't provide {}, keys are {}".format(
						current_state,
						state_infos[current_state]['provides'],
						state_infos[current_state]['provides'] - result.keys(),
						result.keys()))

			found = False
			for transition in transitions:
				if transition['from'] != current_state or ('condition' in transition and not transition['condition'](result,state_object)):
					continue

				current_state = transition['to']
				found = True
				break

			if not found:
                                raise Exception("Didn't find a continuation from state '{}'".format(source_state))
		elif isinstance(return_code,return_code_exit):
			break
		else:
			raise Exception('The state {} returned an unusable value (neither back nor forward nor exit): {}'.format(current_state,type(return_code)))
