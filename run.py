import sys
import time
import random
import multiprocessing
import tensorflow as tf
from A3C import *
from modeltest import *
from Arena import Arena

try:
    from malmo import MalmoPython
except:
    import MalmoPython

if __name__ == '__main__':
    print("Started Fighting AI!!!")
    max_episode_length = 10000
    gamma = .99 # discount rate for advantage estimation and reward discounting
    # Warning we are loading the model now
    load_model = True
    # Spawns single agent with no training, change mspertick to 50 in arena xml
    testing = False
    model_path = './model'
    recordingsDirectory = "FightRecordings"

    tf.reset_default_graph()

    if not os.path.exists(recordingsDirectory):
        os.makedirs(recordingsDirectory)
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    if not os.path.exists('./frames'):
        os.makedirs('./frames')

    with tf.device("/device:CPU:0"):
        global_episodes = tf.Variable(0,dtype=tf.int32,name='global_episodes',trainable=False)
        trainer = tf.train.AdamOptimizer(learning_rate=1e-4)
        master_network = AC_Network('global', None) # Generate global network
        # num_workers = multiprocessing.cpu_count() # Set workers to number of available CPU threads

        num_workers = 5 # Manually setting number of workers, will not work if you exceed number of available local cores
        if testing:
            num_workers = 1
        workers = []
        # Create worker classes
        for i in range(num_workers):
            # print("\nCreated worker: " + str(i))
            # Set up a recording
            agent_host = MalmoPython.AgentHost()
            agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)
            agent_host.setVideoPolicy(MalmoPython.VideoPolicy.LATEST_FRAME_ONLY)
            my_mission_record = MalmoPython.MissionRecordSpec()
            my_mission_record.recordRewards()
            my_mission_record.recordObservations()
            arena = Arena(agent_host)
            arena.withLayer(1,'bedrock')	\
            .withLayer(2, 'dirt')			\
            .withLayer(1, 'grass')			\
            .withEntity('zombie')
            arena.build()
            if testing:
                workers.append(Tester(arena, i, model_path, global_episodes, agent_host, recordingsDirectory, trainer))
            else:
                workers.append(Worker(arena, i, model_path, global_episodes, agent_host, recordingsDirectory, trainer))
        saver = tf.train.Saver(max_to_keep=5)

    with tf.Session() as sess:
        coord = tf.train.Coordinator()
        if load_model == True:
            print ('Loading Model...')
            ckpt = tf.train.get_checkpoint_state(model_path)
            saver.restore(sess,ckpt.model_checkpoint_path)
            print ("Model Loaded\n")
        else:
            sess.run(tf.global_variables_initializer())

        # This is where the asynchronous magic happens.
        # Start the "work" process for each worker in a separate thread.
        worker_threads = []
        for worker in workers:
            worker_work = lambda: worker.run(max_episode_length,gamma,sess,coord,saver)
            t = threading.Thread(target=(worker_work))
            t.start()
            time.sleep(0.5)
            worker_threads.append(t)
        coord.join(worker_threads)
