import struct, os
from glob import glob

categories = [
{"name" : "Physical", "attributes" : ["strength", "endurance", "toughness2", "dexterity", "perception", 
#"survival", #currently not used? always zero
"athletics", "swimming", 
#"warrior spirit", #currently seems to have some pre-set value, zero for most characters
"mass combat"]},

{"name" : "Combat", "attributes" : ["attack", "defence", 
"arrow defence", #not displayed in-game, do I need this?
"dodge"]},

{"name" : "Melee", "attributes" : ["katana", "blunt", "sabres", "hackers", "poles", "heavy weapons", "unarmed"]},

{"name" : "Shooting", "attributes" : ["bow", "turrets"]},

{"name" : "Healing", "attributes" : [
#"doctor", #always zero
"medic"]},

{"name" : "Stealing", "attributes" : ["lockpicking", "thievery", "stealth", "assassin"]},

{"name" : "Crafting", "attributes" : ["weapon smith", "armour smith", "bow smith", "cooking", "labouring", "farming", "science", "engineer", "robotics"]},

{"name" : "WTF", "attributes" : ["tracking", 
"climbing", #may have something to do with different path finding - e. g., for some it's faster to climb straight through, for some - to go around
#"bluff" #always zero
]}
]

attribs = {}

def get_float_record(input_string, starting_position):
	pos = starting_position
	text_name_length = struct.unpack("i", input_string[pos:pos+4])[0]
	if text_name_length <= 0: return (None, None, pos)
	pos += 4
	text_name_itself = input_string[pos : pos + text_name_length].decode()
	pos += text_name_length
	float_parameter_value = struct.unpack("f", input_string[pos:pos+4])[0]
	pos += 4
	return (text_name_itself, float_parameter_value, pos)

def get_character_stats(input_string, starting_position = 0):
	stats = {}
	pos = starting_position
	
	character_begin_block = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00"
	pos = input_string.find(character_begin_block, starting_position)
	if pos < 0: return (None, None, starting_position)
	pos += len(character_begin_block) + 4
	
	name_length = struct.unpack("i", input_string[pos:pos+4])[0]
	pos += 4	#skip 4 mysterious bytes...
	character_name = input_string[pos : pos + name_length].decode()
	pos += name_length
	internal_length = struct.unpack("i", input_string[pos:pos+4])[0]
	pos += 4
	internal_name = input_string[pos : pos + internal_length]
	pos += internal_length

	_internal_magic_number_001 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x2C\x00\x00\x00"
	if not (input_string[pos : pos + len(_internal_magic_number_001)] == _internal_magic_number_001):
		return (None, None, pos)
	pos += len(_internal_magic_number_001)

	while True:
		name, value, pos = get_float_record(input_string, pos)
		if not name: break
		stats[name] = value
	
	return (character_name, stats, pos)

def character_stats(input_file_name):
	with open(input_file_name, "rb") as f_in:
		s = f_in.read()
	
	pos = 0
	while True:
		character_name, character_stats, pos = get_character_stats(s, pos)
		if not character_name: break
		yield (character_name, character_stats)

def parse(wildcard):
	file_names = glob(wildcard)
	
	#same character names may occur in several .platoon files,
	#so let's sort them by modification date, and the latest
	#values will owerwrite eariler values as we parse
	file_names.sort(key = lambda x: os.path.getmtime(x))

	for fn in file_names:
		for nm, st in character_stats(fn):
			attribs[nm] = st