# Minecraft AI Program built using A3C in Python/Malmo

Uses Project Malmo from Microsoft: https://www.microsoft.com/en-us/research/project/project-malmo/

The agent focuses on simple movement and pathfinding so that the agent can move around the obstacles toward the enemy and kill the enemy. Our agent tries to move toward the enemy while taking the least amount of damage and then proceeding to kill the enemy. 

For the machine learning aspect of our project, we used a technique called the Asynchronous Advantage Actor-Critic (A3C) algorithm in order to implement our agent and AI learning. Originally used in an environment for the game DOOM, we have implemented it into our Malmo environment. Although A3C is the overall main technique, it uses aspects of Q-Learning to implement.

For more info: https://rama1997.github.io/GiveUsAnA
