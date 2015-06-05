"""
A sort of integrative test, checking that TD works properly on the random walk
environment.
"""
import numpy as np 

import matplotlib.pyplot as plt 
import matplotlib.cm as cm 

from algorithms.td import TD 
from features.features import *
from environments.gridworld import Gridworld


# Specify experiment #############
random_seed = None
num_episodes = 100
nx = 4
ny = 3


# Setup experiment
np.random.seed(random_seed)


# Setup Environment
env = Gridworld(nx, ny)


# Specify policy
def policy(s, actions):
    return np.random.choice(actions)


# Run the simulation
episodes = []
for i in range(num_episodes):
    env.reset()
    episode = []
    while not env.is_terminal():
        # Observe, take action, get next observation, and compute reward
        s  = env.observe()
        a  = policy(s, env.actions)
        r  = env.do(a)
        sp = env.observe()

        # Append step to episode trajectory
        episode.append((s, a, r, sp))

    # Append trajectory to episodes
    episodes.append(episode)


# Set feature mapping
# phi = Identity(len(env.observe()))
phi0 = Identity(len(env.observe()))
phi1 = Bias()
phi  = Combination((phi0, phi1))

# Setup agent
agent = TD(phi.length)
alpha = 0.01
gamma = 1
lmbda = 0


# Perform learning
for episode in episodes:
    # Reset agent for start of episode
    agent.reset()
    for step in episode[:-1]:
        # Unpack timestep and perform function approximation
        s, a, r, sp = step
        fvec = phi(s)
        fvec_p = phi(sp)
        agent.update(fvec, r, fvec_p, alpha, gamma, lmbda)
    # Perform final step
    s, a, r, sp = episode[-1]
    fvec = phi(s)
    fvec_p = np.zeros_like(fvec)
    agent.update(fvec, r, fvec_p, alpha, gamma, lmbda)


# Determine the values of each state
values = {}
for s in env.nonterminals:
    obs = tuple(env.observe(s))
    values[obs] = np.dot(agent.theta, phi(obs))

print("Values:")
print(values)


# As matrix for image representation
mat = np.zeros(env.shape)
theta = agent.theta
for s in env.nonterminals:
    obs = tuple(env.observe(s))
    mat[s] = np.dot(theta, phi(obs))

# Plot the matrix with a colorbar
fig, ax = plt.subplots()
cax = ax.matshow(np.flipud(mat.T), cmap=cm.Reds)
fig.colorbar(cax)
# plt.show()