---
layout: default
title:  Proposal
---

## Project Summary
  We want to make an agent that will eliminate enemies as swiftly as possible while taking the least amount of damage. To facilitate this there will be obstacles between the enemy and agent. Enemies will have a high enough health such that the agent will need to learn how to enchant their weapons, use potions, or use obstacles in order avoid death. Our learning algorithm will take in the enemy type, positions and dimensions of obstacles, and time. Then, the algorithm will output the agent’s path, velocity, enchanted weapons, potions, timing of weapon attacks, and when to switch weapons.  
  
  
## AI/ML Algorithms
  We will be using reinforcment learning and Markov decision process to help train our agent in our project.

## Evaluation Plan
  For a baseline, the agent will need to kill a  skeleton with a large enough health such that the agent will need to deploy a health potion, otherwise they will be killed by the skeleton’s arrow. This will give a baseline of the enchantments without worrying about path around the obstacles. We will even track health events (increase/decrease, time), fighting events (weapon, time), potion deployment (potion, time), and enchantment (weapon/human, enchantment).
	The metrics used to measure the performance of our project will be how much health the agent loses during the fight and how fast the agent kills the enemy. As our agent learns and improves, the agent should be able to kill the enemy faster while at the same time, losing less health than they did before. The use of potions, enchantments, and equipments will help our agent achieve a better result. Our moonshot case is for our agent to optimally maneuver around map and obstacles, and instantly knowing and executing how to kill whatever enemy is presented to them.
  
## Appointment with the Instructor
  Our meeting with the instructor will be on Monday the 22th at 10:45.

