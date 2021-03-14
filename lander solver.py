# import argparse
import gym
import os
import numpy as np
from neat import nn, population, statistics, parallel


### User Params ###

# The name of the game to solve
game_name = 'LunarLander-v2'

class args:

    # max - steps = 1000 - -episodes = 10 - -generations = 50 - -render
    render = False
    checkpoint = False

    max_steps = 1000
    episodes = 10
    generations = 500
    numCores = 8

### End User Params ###




def simulate_species(net, env, episodes=1, steps=5000, render=False):
    fitnesses = []
    for runs in range(episodes):
        inputs = my_env.reset()
        cum_reward = 0.0
        for j in range(steps):
            outputs = net.serial_activate(inputs)
            action = np.argmax(outputs)
            inputs, reward, done, _ = env.step(action)
            if render:
                env.render()
            if done:
                break
            cum_reward += reward

        fitnesses.append(cum_reward)

    fitness = np.array(fitnesses).mean()
    # print("Species fitness: %s" % str(fitness))
    return fitness


def worker_evaluate_genome(g):
    net = nn.create_feed_forward_phenotype(g)
    return simulate_species(net, my_env, args.episodes, args.max_steps, render=args.render)

# found_parameters = [1, 0, 0, 0]
# found_parameters = [1, 0.44459996, 0, 0]
# found_parameters = [1, 0.15005176, 0.16474673, 0.84250724]
found_parameters = [0.48642068, 0.62694111, 0.44605399, 0.55087529]

def train_network(env):
    # found_parameters = [0.8249416, 0.83464817, 0.715702, 0.50413095]
    # found_parameters = [0.8249416, 0.83464817, 0.715702, 0.50413095]
    a = found_parameters[0]
    b = found_parameters[1]
    c = found_parameters[2]
    d = found_parameters[3]

    def evaluate_genome(g):
        net = nn.create_feed_forward_phenotype(g)
        return simulate_species(net, env, args.episodes, args.max_steps, render=args.render)

    def eval_fitness(genomes):
        for g in genomes:
            fitness = evaluate_genome(g)
            g.fitness = fitness

    # Simulation
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-lunar-lander-neat')
    pop = population.Population(config_path)

    pop.config.prob_add_conn = a
    pop.config.prob_delete_conn = b

    # # Node version of experiment:
    pop.config.prob_add_node = c
    pop.config.prob_delete_node = d

    # pop.config.prob_add_conn = 0.00000988
    # Load checkpoint
    if args.checkpoint:
        pop.load_checkpoint(args.checkpoint)
    # Start simulation
    if args.render:
        pop.run(eval_fitness, args.generations)
    else:
        pe = parallel.ParallelEvaluator(args.numCores, worker_evaluate_genome)
        pop.run(pe.evaluate, args.generations)

    pop.save_checkpoint("checkpoint")

    # Log statistics.
    # statistics.save_stats(pop.statistics)
    # statistics.save_species_count(pop.statistics)
    # statistics.save_species_fitness(pop.statistics)

    print('Number of evaluations: {0}'.format(pop.total_evaluations))

    # Show output of the most fit genome against training data.
    winner = pop.statistics.best_genome()

    # Save best network
    import pickle
    name = 'winner ' + str(len(pop.statistics.generation_statistics)) + '.pkl'
    with open(name, 'wb') as output:
       pickle.dump(winner, output, 1)

    print('\nBest genome:\n{!s}'.format(winner))
    print('\nOutput:')

    input("Press Enter to run the best genome...")
    winner_net = nn.create_feed_forward_phenotype(winner)

    for i in range(20):
        simulate_species(winner_net, env, 1, args.max_steps, render=True)


my_env = gym.make(game_name)
# print("Input Nodes: %s" % str(len(my_env.observation_space.high)))
# print("Output Nodes: %s" % str(my_env.action_space.n))



if __name__ == '__main__':

    train_network(my_env)

