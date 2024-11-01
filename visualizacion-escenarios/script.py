import simpy
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import simulation.statistics as stats
from simulation.simulation import Simulation
from simulation.network_data import NetworkData

plt.style.use('ggplot')

FREQUENCY = 0.2

def main():
    """
    Main function to run simulation
    """
    env = simpy.Environment()  # use instant simulation
    #env = simpy.rt.RealtimeEnvironment(factor=1.)  # use real time simulation
    # Initialize Sioux Falls network
    networkData = NetworkData(0.0025)
    # Create simulation enviromment
    img = np.zeros((900, 800, 3), dtype=np.uint8)
    sim = Simulation(env, img)
    # Create network by enumerating across all links
    for linkid, t0 in enumerate(networkData.t0):
        # Calculate length of link with sqrt((x1 - x2)^2 + (y1 - y2)^2)
        length = np.sqrt(
            np.power(networkData.x1[linkid] - networkData.x2[linkid], 2)
          + np.power(networkData.y1[linkid] - networkData.y2[linkid], 2)) / 600.
        mu = networkData.mu[linkid]
        # Assign nodeID to each link if check pass in node list
        for i, node in enumerate(networkData.nodes):
            if linkid+1 in node:
                nodeID = i
        # Assign turn ratio to each link
        turns = {}
        for j, turn in enumerate(networkData.turns[linkid]):
            turns[j + 1] = turn
        # Assign exit probability from last item in turn list ([-1])
        turns['exit'] = turns.pop(list(turns.keys())[-1])
        # Generate coordinates of each link (for visualization)
        pt1 = (np.float32(networkData.x1[linkid] / 600.),
               np.float32(networkData.y1[linkid] / 600.))
        pt2 = (np.float32(networkData.x2[linkid] / 600.),
               np.float32(networkData.y2[linkid] / 600.))
        c = (pt1, pt2)
        # Draw link on map
        sim.networkLines.append(c)
        # Add link to sim.network
        sim.network.addLink(linkID=linkid+1, turns=turns,
                            type='link',  length=length,
                            t0=t0, MU=mu, nodeID=nodeID,
                            coordinates=c)
        # Initialize car generation
        if linkid % 3 == 0:
            env.process(sim.source(10,
                                   LAMBDA=networkData.flambda[linkid],
                                   linkid=linkid+1))
    # Draw initial network
    for i in sim.networkLines:
        start_point = (i[0][0].astype(int), i[0][1].astype(int))
        end_point = (i[1][0].astype(int), i[1][1].astype(int))
        cv2.line(sim.img, start_point, end_point, (255, 255, 255), 3)
    for linkid in sim.network.links:
        loc = (0.25 * np.asarray(sim.network.links[linkid]['coordinates'][1]) +
               0.75 * np.asarray(sim.network.links[linkid]['coordinates'][0]))
        tuple = (loc[0].astype(int), loc[1].astype(int))
        cv2.putText(sim.img, str(linkid), tuple, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    name = 'Network'
    cv2.imshow(name, sim.img)
    # Start visualization update process
    # Frequency is the visualization poll rate, smaller = faster polling
    env.process(sim.visualization(frequency=FREQUENCY, name=name))
    # Wait for keypress to start simulation
    #print('press space to start')
    #k = cv2.waitKey(0)
    #if k == 27:
    #    sys.exit()
    # run simulation
    env.run()
    ######################################
    # simulation statistics and graphing #
    ######################################
    df = pd.DataFrame(sorted(sim.data, key=lambda x: x[3]),
                      columns=['carID', 'link', 'event', 'time', 'queue', 't_queue'])
    print(df)
    # cars statistics
    totalTravelTime = (df[['carID', 'time']].groupby(['carID']).max()
                       - df[['carID', 'time']].groupby(['carID']).min())
    totalTravelTime.columns = ['totalTravelTime']
    totalSegments = df.loc[df['event'] == 'arrival'][['carID', 'link']]
    totalSegments = totalSegments.groupby(['carID']).count()
    totalSegments.columns = ['totalSegments']
    meanWaitTime = df.loc[df['event'] == 'departure'][['carID', 't_queue']]
    meanWaitTime = meanWaitTime.groupby(['carID']).mean()
    meanWaitTime.columns = ['meanWaitTime']
    carStatistics = pd.concat([totalTravelTime, totalSegments, meanWaitTime], axis=1)
    # Links statistics
    stats.meanQueueLength(plt, df)
    plt.figure(2)
    for link in sim.network.links.keys():
        df2 = df.loc[(df['link'] == link) & (df['event'] != 'entry')]
        if df2.empty is False and df2['t_queue'].sum() > 0.:
            plt.plot(df2[['time']], df2[['queue']], label='link %s' % link)
    plt.title('Queueing simulation')
    plt.ylabel('Queue length')
    plt.xlabel('Time (s.)')
    plt.legend()
    plt.show()
    print('Press any key to exit')
    cv2.waitKey(0)
    
# Standard boilerplate to call the main() function to begin the program.
if __name__ == '__main__':
  main()