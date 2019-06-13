---
layout: default
title:  Final Report
---


## Video

<iframe width="560" height="315" src="https://www.youtube.com/embed/4VRJAiz9n3Q" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>



## Project Summary

Our original goal of our project was to create an agent that can eliminate any enemy or enemies that appear in front of them as swiftly as possible while taking the least amount of damage. Our original idea was to put terrains and various obstacles in between the agent and the enemy and have our agent successfully maneuver toward the enemy. As our agent moved toward the enemy, the enemy would shoot weapon projectiles at the agent causing the agent to take damage. We also planned to create traps within the map that the agent could trigger and take damage. While maneuvering toward the enemy, our agent will also have to learn how to enchant their weapons, use potions, or use obstacles in order to avoid death. With all these factors coming into play, we wanted our agent to find the best path that would lead them to the enemy in which the agent also takes the least amount of damage. As time went out, we decided to tone down our project as it was too ambiguous and complex. 

We wanted to get the basics down first so we could start small and build our way up. We decided  to focus on getting our agent to move toward the enemy while taking the least amount of damage and then proceeding to kill the enemy. We planned to account for the extra external factors and commands like weapons and potion after we perfected our base case of just movement. However, we eventually decided to just focus on simple movement and pathfinding while ignoring the other external commands. Ignoring all the external factors beside an enemy and obstacles, we worked toward making an agent that can move around the obstacles toward the enemy and kill the enemy.

For the machine learning aspect of our project, we used a technique called the Asynchronous Advantage Actor-Critic (A3C) algorithm in order to implement our agent and AI learning. Originally used in an environment for the game DOOM, we have implemented it into our Malmo environment. Although A3C is the overall main technique, it uses aspects of Q-Learning to implement.


<img src="https://scontent-sjc3-1.xx.fbcdn.net/v/t1.15752-9/s2048x2048/62436412_465622304192830_4614233204616855552_n.jpg?_nc_cat=108&_nc_oc=AQmleTHlRD9T6UDtAS3w1szRdgG2J6-qnVTxvrCuODLGFXjqizg_8nz_XzEql33rXDAjrhqmL-Tw5mzjVt3G8nYd&_nc_ht=scontent-sjc3-1.xx&oh=035a3cadf65ba5d6f6b0167f3f738235&oe=5D91D637" width="70%"> 


## Approach

For our project, we will be using the Asynchronous Advantage Actor-Critic (A3C) algorithm in Tensorflow to create our agent. In A3C, there are multiple agent workers or "actors" who each have their own copy of the environment. These agents will each interact and train within their own environment at the same time, independent of each other. The agents will then relay informations gained back to the global network where the "critic" will adjust the global values based on information received. This method is beneficial because more work is getting done at the same time as well as the agent being independent from each other. The image below is a visual on how A3C is organized. There is a global network with its own policy function, value function, network, and input. This global network will send data down to many different workers with their own set of policy functions, value function, network, and input. The worker will then train within their own individual environment. The data from training in the environment will go back to the worker which will then relay it back to the global network.

<img src="https://cdn-images-1.medium.com/max/1600/1*YtnGhtSAMnnHSL8PvS7t_w.png" width="40%"> 

[Picture Source](https://cdn-images-1.medium.com/max/1600/1*YtnGhtSAMnnHSL8PvS7t_w.png)



First, the A3C algorithm constructs a global network. Then worker agents are created with their own set of parameters, environment, and network. Each worker then set it's own network parameter to match that of the global network. The workers will then interact within its own environment and collect its own data independent of the other workers. Once a worker has enough data, it will update the global network's parameter. The worker will then repeat the whole process by resetting it's own network parameter to match the global network's new parameter.The image below shows the endless cycle of A3C in progress and how the whole network affects each other and loops around.

<img src="https://cdn-images-1.medium.com/max/1000/1*Hzql_1t0-wwDxiz0C97AcQ.png" width="40%"> 

[Picture Source](https://cdn-images-1.medium.com/max/1000/1*Hzql_1t0-wwDxiz0C97AcQ.png)



At the global network, there will also be a stochastic policy $$π(s)$$ that represent the set of action probability outputs or the distribution of probablities over actions which should sum up to a total of 1.0. We determine how good a state is via the value function $$V(s)$$. The value function $$V(s)$$ is an expected discounted return. The agent uses the value estimate set by the the critic to update the policy so that the agent can more intelligently obtain better results.


$$Discounted Reward: R = γ(r)$$


$$Action Value Function: Q(s,a) = r + γV(s′)$$


The action value function is essentially the Q-value from the method Q-Learning. It determines a value obtained from taking a certain action a on a certain state s. We obtain the weighted-average of $$r + γV(s′)$$ for every possible action a that we can take on state s. The action value function is simply given the state s and action a which will result in only one next state at s'.


$$Advantage: A(s,a) = Q(s,a) - V(s)$$


The advantage function is a function that when given an input of a state s and a action a, determines how good taking the action is compared to the adverage. If taking action a at state s leads to a result that is better than average, then the advantage function will be positive. If taking action a at state s leads to a result that is worse than average, then the advantage function will be negative.


$$Advantage Estimate: A = R - V(s)$$


In our advantage function of A3C, we can replace the action value function with the discounted rewarded value as an estimate value. This results in our advantage estimate equation.


With the data that a worker obtains, the discounted return and advantage is calculated. With those value, we can calculate the value loss and the policy loss. Using these losses, the worker can obtain the gradient taking into account it's own network parameters. The gradient is then used by the worker to update the global network


$$Value Loss: L = Σ(R - V(s))²$$


$$Policy Loss: L = -log(π(s)) * A(s) - β*H(π)$$


The policy loss helps the actor determine which behavior/action taken was good and which was bad. This will help and make the agent do more beneficial and positive actions rather than negative actions. Both the losses are sent up to the global network along with other data in order to improve the whole system.



## Evaluation

Since the aim of our project is to have our agent reach the enemy while taking the least amount of damage, we will measure the performance of our agent by using the metric and statistics of  the mission completeness time,  how fast the agent kills/reaches the enemy,  and how much health the agent loses during the fight. As the agent gets better, the agent should be able to reach the enemy faster while taking less damage. 

The completion time of the mission will tell us how fast the agent has complete the mission by reaching and killing the enemy. As the agent gets better, the completion time of the mission should go down as the agent should learn the fastest path that will lead them to the enemy faster and kill them. The amount of health the agent loses during the mission is another metric that we will use to evaluate the success and result of our agent. As the agent gets better, the health lost should decrease as it should find better and safer paths to take in order to reach the enemy.



## Resources Used

Resources that were used in our project includes a technique called Asynchronous Advantage Actor Critic (A3C) algorithm in Tensorflow. Links and information can be found below.

[Our repository](https://github.com/rama1997/GiveUsAnA)

[Malmo](https://github.com/Microsoft/malmo)

[A3C Github](https://github.com/awjuliani/DeepRL-Agents)

[A3C Article](https://jaromiru.com/2017/02/16/lets-make-an-a3c-theory/)

[A3C Article](https://medium.com/emergent-future/simple-reinforcement-learning-with-tensorflow-part-8-asynchronous-actor-critic-agents-a3c-c88f72a5e9f2)

[A3C Article](https://medium.com/@shagunm1210/implementing-the-a3c-algorithm-to-train-an-agent-to-play-breakout-c0b5ce3b3405)

We would like to give a huge thanks to Professor Singh and our TA Stephen for guidance on our project throughout this quarter.
