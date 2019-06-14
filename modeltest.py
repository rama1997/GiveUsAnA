import uuid
from builtins import range
from builtins import object
import MalmoPython
import json
import logging
import os
import random
import sys
import time
import errno
import plotille

import matplotlib as plt
import threading
import tensorflow as tf
from tensorflow.contrib import slim
import scipy
import numpy as np
from threading import Thread, Lock
from utility import *
from PIL import Image

video_width = 160 * 3
video_height = 120 * 3
batch_size = 100
PIXELS = 84 * 84
clear = lambda: os.system('cls')

if sys.version_info[0] == 2:
	# Workaround for https://github.com/PythonCharmers/python-future/issues/262
	import Tkinter as tk
else:
	import tkinter as tk

action_space = ["move 1", "move 0", "move -1", "turn 0.7", "turn 0",
				"turn -0.7", "strafe 1", "strafe -1", "strafe 0", "attack 1"]

class AC_Network:
	def __init__(self, scope, trainer):
		with tf.variable_scope(scope):
			self.inputs = tf.placeholder(shape=[None, PIXELS], dtype=tf.float32)
			self.imageIn = tf.reshape(self.inputs, shape=[-1, 84, 84, 1])
			self.conv1 = slim.conv2d(activation_fn=tf.nn.elu,
									inputs=self.imageIn, num_outputs=16,
									kernel_size=[8, 8], stride=[4, 4],
									padding='VALID')
			self.conv2 = slim.conv2d(activation_fn=tf.nn.elu,
									inputs=self.conv1, num_outputs=32,
									kernel_size=[4, 4], stride=[2, 2],
									padding='VALID')
			hidden = slim.fully_connected(slim.flatten(self.conv2), 256, activation_fn=tf.nn.elu)

			lstm_cell = tf.contrib.rnn.BasicLSTMCell(256,state_is_tuple=True)
			c_init = np.zeros((1, lstm_cell.state_size.c), np.float32)
			h_init = np.zeros((1, lstm_cell.state_size.h), np.float32)
			self.state_init = [c_init, h_init]
			c_in = tf.placeholder(tf.float32, [1, lstm_cell.state_size.c])
			h_in = tf.placeholder(tf.float32, [1, lstm_cell.state_size.h])
			self.state_in = (c_in, h_in)
			rnn_in = tf.expand_dims(hidden, [0])
			step_size = tf.shape(self.inputs)[:1]
			state_in = tf.nn.rnn_cell.LSTMStateTuple(c_in, h_in)
			lstm_outputs, lstm_state = tf.nn.dynamic_rnn(
					lstm_cell, rnn_in, initial_state=state_in, sequence_length=step_size,
					time_major=False)
			lstm_c, lstm_h = lstm_state
			self.state_out = (lstm_c[:1, :], lstm_h[:1, :])
			rnn_out = tf.reshape(lstm_outputs, [-1, 256])
			self.policy = slim.fully_connected(rnn_out, len(action_space),
											activation_fn=tf.nn.softmax,
											weights_initializer=normalized_columns_initializer(0.01),
											biases_initializer=None,
											scope='policy_fc')
			self.value = slim.fully_connected(rnn_out, 1,
											activation_fn=None,
											weights_initializer=normalized_columns_initializer(0.01),
											biases_initializer=None,
											scope='value_fc')
			if scope != 'global':
				self.actions = tf.placeholder(shape=[None], dtype=tf.int32)
				self.actions_onehot = tf.one_hot(self.actions, len(action_space), dtype=tf.float32, name='actions_hot')
				self.target_v = tf.placeholder(shape=[None], dtype=tf.float32, name='target_v')
				self.advantages = tf.placeholder(shape=[None], dtype=tf.float32, name='advantages')
				self.responsible_outputs = tf.reduce_sum(self.policy * self.actions_onehot, [1])
				self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.target_v - tf.reshape(self.value, [-1])),
											name='value_loss')
				self.entropy = - tf.reduce_sum(self.policy * tf.log(self.policy), name='entropy_loss')
				self.policy_loss = tf.abs(tf.reduce_sum(tf.log(self.responsible_outputs) * self.advantages, name='policy_loss'))
				self.loss = 0.5 * self.value_loss + self.policy_loss - self.entropy * 0.01

				# Get gradients from local network using local losses
				local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope)
				self.gradients = tf.gradients(self.loss,local_vars)
				self.var_norms = tf.global_norm(local_vars)
				grads,self.grad_norms = tf.clip_by_global_norm(self.gradients,40.0)

				# Apply local gradients to global network
				global_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'global')
				self.apply_grads = trainer.apply_gradients(zip(grads,global_vars))

class Tester():
	def __init__(self, arena, name, model_path, global_episodes, agent_host, recordingsDirectory, trainer, gamma=0.99):
		self.name = "worker_" + str(name)
		self.number = name
		self.agent_host = agent_host
		self.trainer = trainer
		self.global_episodes = global_episodes
		self.increment = self.global_episodes.assign_add(1)
		self.episode_rewards = []
		self.episode_lengths = []
		self.episode_mean_values = []
		self.obs = []
		self.summary_writer = tf.summary.FileWriter("train_"+str(self.number))

		# Create the local copy of the network and the tensorflow op to copy global paramters to local network
		self.local_AC = AC_Network(self.name, trainer)
		self.update_local_ops = update_target_graph('global', self.name)
		self.model_path = model_path
		self.gamma = gamma
		# self.saver = tf.train.Saver()
		self.recordingsDirectory = recordingsDirectory
		# TODO continue tweaking rewards
		self.rewards = {"health": -1, "kills": 8.0, "ontarget": 1, "inrange": .5, "movement": -.01, "miss": -.1}
		self.reward_printout = {"health": 0, "kills": 0, "ontarget": 1, "inrange": .5, "movement": 0, "miss": 0, "world": 0}
		self.currentHealth = 20
		self.kills = 0
		self.prior_kills = 0
		# Update this if we are facing a bigger mob
		self.opponents = 1
		self.arena = arena

		# Set up a recording
		self.my_mission_record = MalmoPython.MissionRecordSpec()
		self.my_mission_record.recordRewards()
		self.my_mission_record.recordObservations()


	# def train(self, rollout, sess,gamma, bootstrap_value):
	# 	rollout = np.array(rollout)
	# 	observations = rollout[:, 0]
	# 	actions = rollout[:, 1]
	# 	rewards = rollout[:, 2]
	# 	values = rollout[:, 5]
	#
	# 	# Here we take the rewards and values from the rollout, and use them to
	# 	# generate the advantage and discounted returns.
	# 	# The advantage function uses \"Generalized Advantage Estimation\"
	# 	self.rewards_plus = np.asarray(rewards.tolist() + [bootstrap_value])
	# 	discounted_rewards = discount(self.rewards_plus, gamma)[:-1]
	# 	self.value_plus = np.asarray(values.tolist() + [bootstrap_value])
	# 	advantages = rewards + gamma * self.value_plus[1:] - self.value_plus[:-1]
	# 	advantages = discount(advantages, gamma)
	#
	# 	# Update the global network using gradients from loss
	# 	# Generate network statistics to periodically save
	# 	feed_dict = {self.local_AC.target_v: discounted_rewards,
	# 		self.local_AC.inputs: np.vstack(observations),
	# 		self.local_AC.actions: actions,
	# 		self.local_AC.advantages: advantages,
	# 		self.local_AC.state_in[0]: self.batch_rnn_state[0],
	# 		self.local_AC.state_in[1]: self.batch_rnn_state[1]}
	# 	v_l, p_l, e_l, g_n, v_n, self.batch_rnn_state,_ = sess.run([self.local_AC.value_loss,
	# 		self.local_AC.policy_loss,
	# 		self.local_AC.entropy,
	# 		self.local_AC.grad_norms,
	# 		self.local_AC.var_norms,
	# 		self.local_AC.state_out,
	# 		self.local_AC.apply_grads],
	# 		feed_dict=feed_dict)
	# 	return v_l / len(rollout), p_l / len(rollout), e_l / len(rollout), g_n, v_n

	def get_rewards(self, ob, possiblemiss, consecutive_hits):
		reward = 0
		inrange = False
		if ('MobsKilled' not in ob) or ('LineOfSight' not in ob):
			return 0
		reward += (ob[u'MobsKilled'] - self.kills) * self.rewards['kills']
		reward += (self.currentHealth - ob[u'Life']) * self.rewards["health"]

		self.reward_printout["kills"] += (ob[u'MobsKilled'] - self.kills) * self.rewards['kills']
		self.reward_printout["health"] += (self.currentHealth - ob[u'Life']) * self.rewards["health"]

		if ob[u'LineOfSight'][u'hitType'] == 'entity':
			# print("Agent on target\n")
			reward += self.rewards["ontarget"]
			self.reward_printout["ontarget"] += self.rewards["ontarget"]

			if ob[u'LineOfSight'][u'inRange'] == True:
				reward += self.rewards["inrange"]
				self.reward_printout["inrange"] += self.rewards["inrange"]
				inrange = True
		elif possiblemiss and not inrange:
			reward += self.rewards["miss"]
			self.reward_printout["miss"] += self.rewards["miss"]
			consecutive_hits = False
		self.currentHealth = ob[u'Life']
		self.kills = ob[u'MobsKilled']
		# print("Agent kills: ", ob[u'MobsKilled'])
		return reward

	def run(self, max_episode_length, gamma, sess, coord, saver):
		episode_count = sess.run(self.global_episodes)
		total_steps = 0

		# print("Starting worker " + str(self.number))
		with sess.as_default(), sess.graph.as_default():
			while not coord.should_stop():
				sess.run(self.update_local_ops)
				episode_buffer = []
				episode_values = []
				episode_frames = []
				cnn_frames = []
				episode_reward = 0
				episode_step_count = 0
				running = False
				consecutive_hits = True
				# Initiate a new enironment
				xml = self.arena.getXml()
				my_mission = MalmoPython.MissionSpec(xml, True)
				self.my_mission_record.setDestination(self.recordingsDirectory + "//" + "Mission_" + str(episode_count) + "-" + str(self.number) + ".tgz")
				max_retries = 3
				for retry in range(max_retries):
					try:
						experimentID = str(uuid.uuid4())
						self.agent_host.startMission(my_mission, self.my_mission_record)
						break
					except RuntimeError as e:
						if retry == max_retries - 1:
							print("Error starting mission:", e)
							exit(1)
						else:
							time.sleep(2)
				# print("Waiting for the mission to start", end=' ')
				world_state = self.agent_host.getWorldState()
				while not world_state.has_mission_begun:
					# print(".", end="")
					time.sleep(0.3)
					world_state = self.agent_host.getWorldState()
				# print("\nMisson start\n")
				self.agent_host.sendCommand("chat /gamerule naturalRegeneration false")
				self.agent_host.sendCommand("chat /difficulty easy")

				# Wait for everything to load

				self.arena.afterMissionStart()
				rnn_state = self.local_AC.state_init
				self.batch_rnn_state = rnn_state

				while (len(world_state.video_frames) == 0):
					time.sleep(0.1)
					world_state = self.agent_host.getWorldState()

				frame = world_state.video_frames[0]

				# Repurposed process pixels to handle both the data for the neural network and GIF
				s, s2, s3 = process_pixels(frame, video_height, video_width)

				while (world_state.is_mission_running):
					a_dist, v, rnn_state = sess.run([self.local_AC.policy, self.local_AC.value, self.local_AC.state_out],
															feed_dict={self.local_AC.inputs: [s],
															self.local_AC.state_in[0]: rnn_state[0],
															self.local_AC.state_in[1]: rnn_state[1]})
					a = np.random.choice(a_dist[0], p=a_dist[0])
					a = np.argmax(a_dist == a)
					r = 0
					possiblemiss = False
					self.agent_host.sendCommand(action_space[a])
					# First 8 actions are movement
					if a < 9:
						r += self.rewards["movement"]
						self.reward_printout["movement"] += self.rewards["movement"]
					else:
						possiblemiss = True
					time.sleep(0.05)

					if world_state.number_of_rewards_since_last_state > 0:
						# A reward signal has come in - see what it is:
						delta = world_state.rewards[0].getValue()
						if delta != 0:
							# The total reward has changed - use this to determine our turn.
							r += delta
							self.reward_printout["world"] += delta

					if world_state.is_mission_running and len(world_state.observations) > 0 and not \
							world_state.observations[-1].text == "{}":
						ob = json.loads(world_state.observations[-1].text)
						r_obs = self.get_rewards(ob, possiblemiss, consecutive_hits)
						r += r_obs
						# Regenerate mob if we killed all of them
						if (self.kills - self.prior_kills) == self.opponents:
							self.prior_kills = self.kills
							self.arena.afterMissionStart()

					episode_reward += r

					running = world_state.is_mission_running
					if running:
						try:
							world_state = self.agent_host.getWorldState()
							frame = world_state.video_frames[0]
							s1, s2, s3 = process_pixels(frame, video_height, video_width)
							img = Image.fromarray(s2, "RGB")
							episode_frames.append(img)
							img = Image.fromarray(s3)
							cnn_frames.append(img)
						except:
							s1 = s
					else:
						s1 = s

					episode_buffer.append([s, a, r, s1, running, v[0, 0]])
					episode_values.append(v[0, 0])

					#print("Episode reward: ", episode_reward)
					s = s1
					total_steps += 1
					episode_step_count += 1
					# If the episode hasn't ended, but the experience buffer is full, then we
					# make an update step using that experience rollout.
					# if len(episode_buffer) == 30 and running and episode_step_count != max_episode_length - 1:
					# 	# Since we don't know what the true final return is, we \"bootstrap\" from our current
					# 	# value estimation.
					# 	v1 = sess.run(self.local_AC.value,
					# 					feed_dict={self.local_AC.inputs: [s],
					# 					self.local_AC.state_in[0]: rnn_state[0],
					# 					self.local_AC.state_in[1]: rnn_state[1]})[0, 0]
					# 	v_l, p_l, e_l, g_n, v_n = self.train(episode_buffer, sess, gamma, v1)
					# 	episode_buffer = []
					# 	sess.run(self.update_local_ops)
					if not running:
						# print("Mission has stopped.")
						time.sleep(0.5)  # Give mod a little time to get back to dormant state.
						break
				self.currentHealth = 20
				self.kills = 0
				self.prior_kills = 0
				clear()
				print("-" * 10)
				print("Rewards for episode: ", str(episode_count))
				print("-" * 10)
				total = 0
				for k, v in self.reward_printout.items():
					print(k, ": ", v)
					total += v
				self.reward_printout = self.reward_printout.fromkeys(self.reward_printout, 0)
				print("Total tracked: ", total)
				time.sleep(2)

				self.episode_rewards.append(episode_reward)
				self.episode_lengths.append(episode_step_count)
				self.episode_mean_values.append(np.mean(episode_values))
				# # Update the network using the episode buffer at the end of the episode.
				# if len(episode_buffer) != 0:
				# 	v_l, p_l, e_l, g_n, v_n = self.train(episode_buffer, sess, gamma, 0.0)
				episode_count += 1
				# Periodically save gifs of episodes, model parameters, and summary statistics.
				if episode_count % 1 == 0 and episode_count != 0:
					if self.name == 'worker_0' and episode_count % 1 == 0:
						# self.saver.save(sess, 'fighter_models/fight_ep_{0}.cpkt'.format(episode_count))
						time_per_step = 0.05
						# print(len(episode_frames))
						episode_frames[0].save('./frames/testing'+str(episode_count)+'.gif', format='GIF', append_images=episode_frames[1:], save_all=True, duration=len(episode_frames)*time_per_step, loop=0)
						cnn_frames[0].save('./frames/cnn'+str(episode_count)+'.gif', format='GIF', append_images=cnn_frames[1:], save_all=True, duration=len(cnn_frames)*time_per_step, loop=0)
					# if episode_count % 100 == 0 and self.name == 'worker_0':
					# 	# saver.save(sess, self.model_path+'/model-'+str(episode_count)+'.cptk')
					# 	print("Saved Model")

					# mean_reward = np.mean(self.episode_rewards[-5:])
					# mean_length = np.mean(self.episode_lengths[-5:])
					# mean_value = np.mean(self.episode_mean_values[-5:])
					# summary = tf.Summary()
					# summary.value.add(tag='Perf/Reward', simple_value=float(mean_reward))
					# summary.value.add(tag='Perf/Length', simple_value=float(mean_length))
					# summary.value.add(tag='Perf/Value', simple_value=float(mean_value))
					# summary.value.add(tag='Losses/Value Loss', simple_value=float(v_l))
					# summary.value.add(tag='Losses/Policy Loss', simple_value=float(p_l))
					# summary.value.add(tag='Losses/Entropy', simple_value=float(e_l))
					# summary.value.add(tag='Losses/Grad Norm', simple_value=float(g_n))
					# summary.value.add(tag='Losses/Var Norm', simple_value=float(v_n))
					# self.summary_writer.add_summary(summary, episode_count)
					# fig = plotille.Figure()
					# fig.width = 60
					# fig.height = 30
					# #fig.set_x_limits(min_=-3, max_=3)
					# #fig.set_y_limits(min_=-1, max_=1)
					# fig.color_mode = 'byte'
					# episodes = np.arange(len(self.episode_rewards[-5:]))
					# fig.scatter(episodes, self.episode_rewards[-5:], lc=100, label='Rewards')
					# fig.scatter(episodes, self.episode_lengths[-5:], lc=150, label='Lengths')
					# fig.scatter(episodes, self.episode_mean_values[-5:], lc=200, label='Mean Values')
					# fig.scatter(episode_count, v_l, lc=400, label='Value Loss')
					# fig.scatter(episode_count, p_l, lc=500, label='Policy Loss')
					# fig.scatter(episode_count, e_l, lc=600, label='Entropy')
					# fig.scatter(episode_count, g_n, lc=700, label='Gradient Norm')
					# fig.scatter(episode_count, v_n, lc=800, label='Variance Norm')
					#print(fig.show(legend=True))

					self.summary_writer.flush()
				if self.name == 'tester_0':
					sess.run(self.increment)
				print('episode reward = {0}'.format(episode_reward))
				print('enemies killed = {0}'.format(self.kills))
				# print('episode {0}, value loss = {1} | policy = {2} | entropy = {3}'.format(episode_count, v_l, p_l, e_l))
