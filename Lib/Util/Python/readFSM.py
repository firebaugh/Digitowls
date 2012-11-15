"""
ReadFSM class reads text of lua files and generates a list of states and a list of states with their transitions, using the 'get_states' and 'get_transitions' methods, respectively.

*******
You will need to change the path to the lua files since this is based on my account. I guess it would be the same, you just need to change the path to include your account name. Is there a better way to do this?
"""

import os

game = open("/home/" + str(os.getenv('USER')) + "/UPennalizers/Player/GameFSM/RoboCup/GameFSM.lua", "r").readlines()
body = open("/home/" + str(os.getenv('USER')) + "/UPennalizers/Player/BodyFSM/NaoPlayer/BodyFSM.lua", "r").readlines()
head = open("/home/" + str(os.getenv('USER')) + "/UPennalizers/Player/HeadFSM/NaoPlayer/HeadFSM.lua", "r").readlines()


class ReadFSM:

	def __init__(self, text):
	    self.text = text

	def get_states(self):

	    new_state = "sm = fsm.new"
	    add_state = "sm:add_state"
	    
	    # append lines
	    output = []
	    for line in self.text:
	    	if new_state in line or add_state in line:
	    	    output.append(line)
	    
	    output2 = []
	    for i in output:
	    	start = i.index("(") + 1
	    	end = i.index(")")
	    	output2.append(i[start:end])
	    	
	    return output2
    

	def get_transitions(self):

	    tran = "sm:set_transition"

	    # appends lines
	    output = []
	    for line in self.text:
		if tran in line:
		    output.append(line)

	    # selects transition string
	    output2 = []
	    for i in output:
		start = i.index("(") + 1
		end = i.index(")")
		output2.append(i[start:end])

	    # manipulates final string
	    # different files use different types of quotes
	    output3 = []
	    for i in output2:
		i = i.replace(', "', ':')
		i = i.replace('", ', ':')
		i = i.replace(", '", ":")
		i = i.replace("', ", ":")
		output3.append(i)

	    return output3
	    
	    
# initializing the class


def getBGHfsm():
	g = ReadFSM(game)
	b = ReadFSM(body)
	h = ReadFSM(head)

	# these are your lists!
	game_states = g.get_states()
	game_trans = g.get_transitions()

	body_states = b.get_states()
	body_trans = b.get_transitions()

	head_states = h.get_states()
	head_trans = h.get_transitions()

	fsm_states = [game_states, body_states, head_states]
	return fsm_states

        


