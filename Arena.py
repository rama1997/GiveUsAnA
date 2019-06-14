# import random
# import json
# import time
# from collections import defaultdict
#
#
# video_width = 160 * 3
# video_height = 120 * 3
#
# TICK_LENGTH = 50
# DEFAULT_HEIGHT = 10
# DEFAULT_SIDELENGTH = 80
# TNT_BUFFER = 10
# ENTITY_BUFFER = 2
# TNT_CHANCE = 0.2
#
# class ArenaException(Exception):
# 	pass
#
# class Arena:
# 	def __init__(self, agent_host, seed=1):
# 		random.seed(seed)
# 		self.agent_host = agent_host
# 		self.layer_list = []
# 		self.position = (15, 0, 72)
# 		self.arenaXYZs = defaultdict(list)
# 		self.sideLength = DEFAULT_SIDELENGTH
# 		self.height = DEFAULT_HEIGHT
# 		self.worldHeight = 0
# 		self.tnt = 0.0
# 		self.opponents = []
# 	def withPosition(self, x, y, z):
# 		self.position = (x,y,z)
# 		return self
# 	def withLayer(self, count, block):
# 		self.layer_list.append((count, block))
# 		self.worldHeight += count
# 		self.position = (self.position[0], self.position[1]+count, self.position[2])
# 		return self
# 	def withFlatArena(self, sideLength=DEFAULT_SIDELENGTH, height=DEFAULT_HEIGHT):
# 		GLOWSTONE_BUFFER = 5
# 		(x, y, z) = self.position
# 		self.sideLength = sideLength
# 		self.height = height
# 		self.arenaXYZs['enclosure'].append((x-sideLength//2, y-self.worldHeight+1, z+sideLength//2, x+sideLength//2, y+height, z+sideLength//2))
# 		self.arenaXYZs['enclosure'].append((x+sideLength//2, y-self.worldHeight+1, z+sideLength//2, x+sideLength//2, y+height, z-sideLength//2))
# 		self.arenaXYZs['enclosure'].append((x+sideLength//2, y-self.worldHeight+1, z-sideLength//2, x-sideLength//2, y+height, z-sideLength//2))
# 		self.arenaXYZs['enclosure'].append((x-sideLength//2, y-self.worldHeight+1, z-sideLength//2, x-sideLength//2, y+height, z+sideLength//2))
# 		self.arenaXYZs['enclosure'].append((x-sideLength//2, y+height+1, z-sideLength//2, x+sideLength//2, y+height+1, z+sideLength//2))
# 		for i in range(1, sideLength):
# 			placeX = x-sideLength//2+i
# 			if (placeX % GLOWSTONE_BUFFER):
# 				continue
# 			for j in range(1, sideLength):
# 				placeZ = z-sideLength//2+j
# 				if (placeZ % GLOWSTONE_BUFFER):
# 					continue
# 				self.arenaXYZs['glowstone'].append((placeX, int(y+height*0.75), placeZ))
# 				self.arenaXYZs['torch'].append((placeX, y, placeZ))
# 		return self
#
# 	def withEntity(self, entity):
# 		self.opponents.append(entity)
# 		return self
#
# 	def withTnt(self, chance=TNT_CHANCE):
# 		self.tnt = chance
# 		return self
#
# 	def _loadGrid(self):
# 		world_state = self.agent_host.getWorldState()
# 		while world_state.is_mission_running:
# 		    #sys.stdout.write(".")
# 		    time.sleep(0.1)
# 		    world_state = self.agent_host.getWorldState()
# 		    if len(world_state.errors) > 0:
# 		        raise AssertionError('Could not load grid.')
#
# 		    if world_state.number_of_observations_since_last_state > 0:
# 		        msg = world_state.observations[-1].text
# 		        observations = json.loads(msg)
# 		        grid = observations.get(u'arena', 0)
# 		return grid
#
# 	def _generateTntStr(self):
# 		(x, y, z) = self.position
# 		tntXYZs = set()
# 		toPlaceAmount = int(self.tnt * self.sideLength)
# 		for tntX in range(x-self.sideLength//2+1, x+self.sideLength//2):
# 			if (random.random() > self.tnt):
# 				continue
# 			for _ in range(toPlaceAmount):
# 				tntZ = random.randint(z-self.sideLength//2+1, z+self.sideLength//2)
# 				tntY = random.randint(0, y+2)
# 				if (tntX, tntY, tntZ) in tntXYZs:
# 					continue
# 				if (abs(tntX-x) <= TNT_BUFFER and abs(tntZ-z) <= TNT_BUFFER):
# 					# make sure agent starts on flat platform
# 					continue
# 				tntXYZs.add((tntX, tntY, tntZ))
# 		drawTntString = ''
# 		for xyz in tntXYZs:
# 			drawTntString += '''<DrawEntity type="PrimedTnt" x="{}" y="{}" z="{}"/>\n'''.format(*xyz)
# 		return drawTntString
#
# 	def _generateArenaStr(self):
# 		drawArenaString = ''
# 		for arg in self.arenaXYZs['enclosure']:
# 			drawArenaString += '''<DrawCuboid type="bedrock" x1="{}" y1="{}" z1="{}" x2="{}" y2="{}" z2="{}"/>\n'''.format(*arg)
# 		for arg in self.arenaXYZs['glowstone']:
# 			for y in [i for i in range(self.position[1]) if i % 3 == 0] + [arg[1]]:
# 				drawArenaString += '''<DrawBlock type="glowstone" x="{}" y="{}" z="{}"/>\n'''.format(arg[0], y, arg[2])
# 		for arg in self.arenaXYZs['torch']:
# 			drawArenaString += '''<DrawBlock type="torch" x="{}" y="{}" z="{}"/>\n'''.format(*arg)
# 		return drawArenaString
#
# 	def _clearSpawnAreaStr(self):
# 		x1 = self.position[0] - 2
# 		x2 = x1 + 4
# 		y1 = self.position[1]
# 		y2 = y1 + 3
# 		z1 = self.position[2] - 2
# 		z2 = z1 + 4
# 		return '''<DrawCuboid type="air" x1="{}" y1="{}" z1="{}" x2="{}" y2="{}" z2="{}"/>\n'''.format(x1, y1, z1, x2, y2, z2)
#
# 	def _exclRange(self, low, high, lowExcl, highExcl):
# 		return random.choice(list(range(low, lowExcl))+list(range(highExcl, high)))
#
# 	def _generateOpponents(self):
# 		x, y, z = self.position
# 		for e in self.opponents:
# 			maxDistFromAgent = self.sideLength // 4
# 			eX = self._exclRange(x-maxDistFromAgent, x+maxDistFromAgent+1, x-ENTITY_BUFFER+1, x+ENTITY_BUFFER)
# 			eZ = self._exclRange(z-maxDistFromAgent, z+maxDistFromAgent+1, z-ENTITY_BUFFER+1, z+ENTITY_BUFFER)
# 			self.agent_host.sendCommand("chat /summon {} {} {} {}".format(e, eX, y, eZ))
#
# 	def afterMissionStart(self):
# 		self._generateOpponents()
# 		#self.agent_host.sendCommand("chat /kill @e[type=Item]") Currently using force reset
#
# 	def eraseEntities(self):
# 		for e in self.opponents:
# 			self.agent_host.sendCommand("chat /kill @e[type={}]".format(e))
#
# 	def GetMissionXML(self):
# 		generatorString = "3;"
# 		for count, block in self.layer_list:
# 			generatorString += "{}*minecraft:{},".format(count, block)
# 		generatorString = generatorString[:-1] + ";4;decoration"
# 		placementString = '''x="{}" y="{}" z="{}"'''.format(*self.position)
# 		drawArenaString = self._generateArenaStr()
# 		drawTntString = self._generateTntStr()
# 		obsGridStr = '''<min x="{}" y="{}" z="{}"/>\n'''.format(self.position[0]-self.sideLength//2, 0, self.position[2]-self.sideLength//2)
# 		obsGridStr += '''<max x="{}" y="{}" z="{}"/>\n'''.format(self.position[0]+self.sideLength//2, self.position[1]+self.height+1, self.position[2]+self.sideLength//2)
# 		clrSpawnStr = self._clearSpawnAreaStr()
# 		#<PrioritiseOffscreenRendering> 1 </PrioritiseOffscreenRendering>
# 		xml =  '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
# 			<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
# 			  <About>
# 				<Summary>Advanced Fighting!</Summary>
# 			  </About>
# 			  <ModSettings>
# 				<MsPerTick>''' + str(TICK_LENGTH) + '''</MsPerTick>
# 				<PrioritiseOffscreenRendering> 1 </PrioritiseOffscreenRendering>
# 			  </ModSettings>
# 			  <ServerSection>
# 				<ServerInitialConditions>
# 					<Time>
# 						<StartTime>1</StartTime>
# 					</Time>
# 				</ServerInitialConditions>
# 				<ServerHandlers>
# 				  <FlatWorldGenerator generatorString="'''+generatorString+'''" forceReset="true"/>
# 				  <DrawingDecorator>
# 				  	'''+drawArenaString+'''
# 				  	'''+clrSpawnStr+'''
# 				  	'''+drawTntString+'''
# 				  </DrawingDecorator>
# 				  <ServerQuitFromTimeUp timeLimitMs="100000"/>
#                   <ServerQuitWhenAnyAgentFinishes />
# 				</ServerHandlers>
# 			  </ServerSection>
#
# 		   	  <AgentSection mode="Survival">
# 				<Name>Doom Guy</Name>
# 				<AgentStart>
# 		   	  	  <Placement '''+placementString+''' pitch="0" yaw="-180"/>
# 				  <Inventory>
# 					<InventoryObject slot="0" type="diamond_sword" quantity="1"/>
# 				  </Inventory>
# 				</AgentStart>
# 				<AgentHandlers>
# 				  <RewardForDamagingEntity>
# 				    <Mob type="Skeleton" reward="4"/>
# 				  </RewardForDamagingEntity>
# 			      <RewardForTimeTaken initialReward="-1" delta="-0.003" density="PER_TICK"/>
# 				  <ObservationFromFullStats/>
# 				  <ObservationFromRay/>
# 				  <ChatCommands/>
# 				  <ContinuousMovementCommands/>
# 				  <MissionQuitCommands
# 					quitDescription="finished killing">
# 					  <ModifierList
# 						type='allow-list'>
# 						  <command>quit</command>
# 					  </ModifierList>
# 				  </MissionQuitCommands>
# 				  <ObservationFromGrid>
# 			      	<Grid name="arena">
# 			        	'''+obsGridStr+'''
# 			      	</Grid>
# 				  </ObservationFromGrid>
# 				  <VideoProducer want_depth="false">
# 					<Width>''' + str(video_width) + '''</Width>
# 				    <Height>''' + str(video_height) + '''</Height>
# 				  </VideoProducer>
# 				</AgentHandlers>
# 			  </AgentSection>
# 			</Mission>'''
# 		return xml

import xml.etree.ElementTree as ET
import random

DEFAULT_HEIGHT = 10
DEFAULT_SIDELENGTH = 40
VIDEO_WIDTH = 160 * 3
VIDEO_HEIGHT = 120 * 3

_NAME_SPACE = "http://ProjectMalmo.microsoft.com"
XSI_NAME_SPACE = "http://www.w3.org/2001/XMLSchema-instance"


class ArenaError(Exception):
	pass


def getName(name):
	return '{' + _NAME_SPACE + '}' + name


def recurFind(root, name):
	if (root.tag == name):
		return root
	for child in root:
		c = recurFind(child, name)
		if c != None:
			return c
	return None


class Arena:
	def __init__(self, agent_host, base="ArenaBase.xml", sideLength=DEFAULT_SIDELENGTH, height=DEFAULT_HEIGHT, seed=1):
		random.seed(seed)
		ET.register_namespace("", _NAME_SPACE)
		ET.register_namespace("xsi", XSI_NAME_SPACE)
		self.tree = ET.parse(base)
		self.root = self.tree.getroot()
		self.position = (15, 0, 72)
		self.layer_list = []
		self.entity = 'zombie'
		self.agent_host = agent_host
		self.height = DEFAULT_HEIGHT
		self.sideLength = DEFAULT_SIDELENGTH

	def killspawns(self):
		self.agent_host.sendCommand("chat /kill @e[type={}]".format(self.entity))

	def afterMissionStart(self):
		# self.agent_host.sendCommand("chat /difficulty peaceful")
		x,y,z = self.getEntityPos()
		attr = "{IsBaby:0,Attributes:[{Name:\"generic.followRange\", Base:200.0}]}"
		self.agent_host.sendCommand("chat /summon {} {} {} {} {}".format(self.entity, x, y, z, attr))
		self.agent_host.sendCommand("chat /kill @e[type=Item]")


	def getEntityPos(self):
		#etPos = (self.position[0], self.position[1], self.position[2] - self.sideLength // 2 * 0.7)
		etPos = (15.0, 6.0, 72 - self.sideLength // 2 * 0.7)
		#return tuple(map(int, etPos))
		x,y,z = tuple(map(int, etPos))
		return x,y,z


	def withLayer(self, count, block):
		self.layer_list.append((count, block))
		self.position = (self.position[0], self.position[1] + count, self.position[2])
		return self

	def withEntity(self, entity):
		self.entity = entity
		return self

	def _buildAgentStart(self):
		agentStart = ET.Element('AgentStart')
		recurFind(self.root, getName('AgentSection')).insert(1, agentStart)
		placement = ET.SubElement(agentStart, 'Placement', **{
			'x': str(self.position[0]),
			'y': str(self.position[1]),
			'z': str(self.position[2])
		})
		placement.set('pitch', '0')
		placement.set('yaw', '-180')

		inventory = ET.SubElement(agentStart, 'Inventory')
		invObj = ET.SubElement(inventory, 'InventoryObject')
		invObj.set('slot', '0')
		invObj.set('type', "diamond_sword")
		invObj.set('quantity', '1')

	def _buildArena(self):
		GLOWSTONE_BUFFER = 5
		SUB_DIV = 6
		(x, y, z) = self.position
		dd = self._addSubElement('ServerHandlers', 'DrawingDecorator')
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'obsidian',
			'x1': str(x - self.sideLength // 4),
			'y1': str(y - self.height + 1),
			'z1': str(z + self.sideLength // 2),
			'x2': str(x + self.sideLength // 2),
			'y2': str(y + self.height),
			'z2': str(z + self.sideLength // 2)
		})
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'obsidian',
			'x1': str(x + self.sideLength // SUB_DIV),
			'y1': str(y - self.height + 1),
			'z1': str(z + self.sideLength // 2),
			'x2': str(x + self.sideLength // SUB_DIV),
			'y2': str(y + self.height),
			'z2': str(z - self.sideLength // 2)
		})
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'obsidian',
			'x1': str(x + self.sideLength // 2),
			'y1': str(y - self.height + 1),
			'z1': str(z - self.sideLength // 2),
			'x2': str(x - self.sideLength // 2),
			'y2': str(y + self.height),
			'z2': str(z - self.sideLength // 2)
		})
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'obsidian',
			'x1': str(x - self.sideLength // SUB_DIV),
			'y1': str(y - self.height + 1),
			'z1': str(z - self.sideLength // 2),
			'x2': str(x - self.sideLength // SUB_DIV),
			'y2': str(y + self.height),
			'z2': str(z + self.sideLength // 2)
		})
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'obsidian',
			'x1': str(x - self.sideLength // 2),
			'y1': str(y + self.height + 1),
			'z1': str(z - self.sideLength // 2),
			'x2': str(x + self.sideLength // 2),
			'y2': str(y + self.height),
			'z2': str(z + self.sideLength // 2)
		})

		for j in range(1, self.sideLength):
			placeZ = z - self.sideLength // 2 + j
			if placeZ % 2:
				continue
			for i in range(1, self.sideLength):
				placeX = x - self.sideLength // 2 + i
				if placeX % 2:
					continue

				if random.random() < 0.5:
					ET.SubElement(dd, 'DrawBlock', **{
						'type': 'gold_block',
						'x': str(placeX),
						'y': str(y),
						'z': str(placeZ)
					})
				if random.random() < 0.5:
					ET.SubElement(dd, 'DrawBlock', **{
						'type': 'gold_block',
						'x': str(placeX),
						'y': str(y + 1),
						'z': str(placeZ)
					})
		# clear areas
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'air',
			'x1': str(x - 2),
			'y1': str(y),
			'z1': str(z - 2),
			'x2': str(x + 2),
			'y2': str(y + 2),
			'z2': str(z + 2)
		})
		etX, etY, etZ, = self.getEntityPos()
		ET.SubElement(dd, 'DrawCuboid', **{
			'type': 'air',
			'x1': str(etX - 4),
			'y1': str(etY),
			'z1': str(etZ - 4),
			'x2': str(etX + 4),
			'y2': str(etY + 2),
			'z2': str(etZ + 4)
		})

		for i in range(1, self.sideLength):
			placeX = x - self.sideLength // 2 + i
			if (placeX % GLOWSTONE_BUFFER):
				continue
			for j in range(1, self.sideLength):
				placeZ = z - self.sideLength // 2 + j
				if (placeZ % GLOWSTONE_BUFFER):
					continue
				dbg = ET.SubElement(dd, 'DrawBlock', **{
					'type': 'glowstone',
					'x': str(placeX),
					'y': str(int(y + self.height * 0.75)),
					'z': str(placeZ)
				})
				dbt = ET.SubElement(dd, 'DrawBlock', **{
					'type': 'torch',
					'x': str(placeX),
					'y': str(y),
					'z': str(placeZ)
				})

	def _addSubElement(self, root_name, sub_name, **extra):
		rootEl = recurFind(self.root, getName(root_name))
		if (rootEl == None):
			ArenaError("Cannot find root {}!".format(sub_name))
		return ET.SubElement(rootEl, getName(sub_name), extra)

	def build(self):
		gs = '3;'
		for count, block in self.layer_list:
			gs += "{}*minecraft:{},".format(count, block)
		gs = gs[:-1] + ";3;"
		fwg = self._addSubElement('ServerHandlers', 'FlatWorldGenerator')
		fwg.set('generatorString', gs)
		fwg.set('forceReset', 'true')
		self._buildArena()
		self._buildAgentStart()
		# <ServerQuitFromTimeUp timeLimitMs="15000" description="out_of_time"/>
		sqftu = ET.SubElement(recurFind(self.root, getName('ServerHandlers')), 'ServerQuitFromTimeUp')
		sqftu.set('timeLimitMs', '120000')
		sqftu.set('description', 'out_of_time')
		vp = ET.SubElement(recurFind(self.root, getName("AgentHandlers")), 'VideoProducer')
		vp.set('want_depth', "false")
		vpWidth = ET.SubElement(vp, "Width")
		vpWidth.text = str(VIDEO_WIDTH)
		vpHeight = ET.SubElement(vp, "Height")
		vpHeight.text = str(VIDEO_HEIGHT)

	def write(self):
		self.tree.write('out.xml')

	def getXml(self):
		return str(self)

	def __str__(self):
		# help(ET.tostring)
		return ET.tostring(self.root, 'utf-8', method="xml").decode('UTF-8')


