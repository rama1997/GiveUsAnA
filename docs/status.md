---
layout: default
title:  Status
---

<iframe width="560" height="315" src="https://www.youtube.com/embed/MmB9b5njVbA" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Project Summary
In our initial project proposal, we wanted to make an agent that will eliminate enemies as swiftly as possible while taking the least amount of damage. Our original idea was to put obstacles in between the agent and the enemy and have our agent successfully maneuver toward the enemy as the enemy is shooting at the agent. While maneuvering toward the enemy, our agent will also have to learn how to enchant their weapons, use potions, or use obstacles in order avoid death. Although still our goal for this project, we first want to focus on getting our agent to move toward the enemy while taking the least damage without account for extra factors like weapons and potion first. For this status report, we are only working around getting an agent to move toward the enemy while taking the least amount of damage.

## Approach
For our project, we will be using the Asynchronous Advantage Actor-Critic (A3C) algorithm in Tensorflow to create our agent. In A3C, there are multple agent workers who each have their own copy of the environment. These agents will each interact and train within their own environment at the same time, independent of each other. The agents will then relay informations gained back to the global network where the "critic" will adjust the global values based on information recieved. This method is beneficial because more work is getting done at the same time as well as the agent being independent from each other.

<img src="https://cdn-images-1.medium.com/max/1000/1*Hzql_1t0-wwDxiz0C97AcQ.png" width="50%"> 

[Picture Source](https://cdn-images-1.medium.com/max/1000/1*Hzql_1t0-wwDxiz0C97AcQ.png)


At the global network, we determine how good a state is via the value function $$V(s)$$. There will also be a policy $$π(s)$$ that represent the set of action probability outputs. The agent uses the value estimate set by the the critic to update the policy so that the agent can more intelligently obtain better results.

$$Discounted Reward: R = γ(r)$$

$$Advantage: A = Q(s,a) - V(s)$$

$$Advantage Estimate: A = R - V(s)$$

## Evaluation

## Remaining Goals and Challenges
Our ultimate goal for our project is to get the agent to swiftly move toward the enemy while taking the least amount of damage with the help and use of weapons, potions, and enchantment. At the time of this status report, we are only working on getting our agent to reach the enemy while not getting hit by the enemy. Our plans for the next few weeks is that If we can get our agent to get this baseline scenario down, we would hope to include the other aspects of weapons and potions. 

## Resources Used
Resources that were used in our project includes a technique called Asynchronous Advantage Actor Critic (A3C) algorithm in Tensorflow. Originally used in an environment for the game DOOM, we are trying to implement it into our Malmo environment. 
