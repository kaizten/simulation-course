import cv2
import numpy as np
from numpy.random import multinomial
from simulation.distribution import uniform, exponential
from simulation.road_network import RoadNetwork

class Simulation(object):
    def __init__(self, env, img):
        self.env = env
        self.data = []
        self.network = RoadNetwork(env)
        self.carCounter = 0
        self.carsInSystem = 0
        self.t_max = 0
        self.img = img
        self.networkLines = []
        self.cars = {}

    def visualization(self, frequency, name):
        """ Visualization env process """
        while self.env.now < self.t_max or self.carsInSystem > 0:
            # redraw entire network
            for i in self.networkLines:
                start_point = (i[0][0].astype(int), i[0][1].astype(int))
                end_point = (i[1][0].astype(int), i[1][1].astype(int))
                #cv2.line(self.img, i[0], i[1], (255,255,255), 3)
                cv2.line(self.img, start_point, end_point, (255,255,255), 3)
            for _linkid in self.network.links:
                if 'queueLines' in self.network.links[_linkid]:
                    line = self.network.links[_linkid]['queueLines']
                    cap = self.network.links[_linkid]['capacity']
                    start_point = (line[0][0].astype(int), line[0][1].astype(int))
                    end_point = (line[1][0].astype(int), line[1][1].astype(int))
                    cv2.line(self.img, start_point, end_point, (0,0,255), 3)
            cv2.imshow(name, self.img)
            k = cv2.waitKey(1)
            yield self.env.timeout(frequency)

    def updateQueue(self, queue, linkid, carLength=3.):
        # Draw queue lines
        length = self.network.links[linkid]['length']
        pt1 = self.network.links[linkid]['coordinates'][0]
        pt2 = self.network.links[linkid]['coordinates'][1]
        # Coordinate math
        dk = np.min((1, queue.level * carLength/length))
        x2 = pt2[0] + dk * (pt1[0] - pt2[0])
        y2 = pt2[1] + dk * (pt1[1] - pt2[1])
        pt1 = (np.float32(x2), np.float32(y2))
        line = (pt2, pt1)
        # Add to data dictionary
        self.network.links[linkid]['queueLines'] = line
        self.network.links[linkid]['capacity'] = dk

    def car(self, carID, t_arrival, node, turn_ratio, linkid):
        """ Car generator """
        # Prepare variables
        t_entry, t_travel = t_arrival
        queue = self.network.links[linkid]['queue']
        # En-route
        yield self.env.timeout(t_travel)
        # Put 1 car in link queue
        yield queue.put(1)
        # Update queue length for visualization
        self.updateQueue(queue, linkid)
        # Query queue length
        with node.request() as req:
            q_length = queue.level
            # Data logging
            print('car %d arrived on link %s at %.2fs (Q=%d cars) ' % (carID, linkid, sum(t_arrival), q_length))
            self.data.append((carID, linkid, 'arrival', sum(t_arrival), q_length))
            # Wait until queue is ready
            result = yield req
            t_service = exponential(self.network.links[linkid]['MU'])
            # Query traffic lights if available
            if node in self.network.trafficLights:
                tg = self.network.trafficLights[node]
                # Yield to traffic light 'stop'
                with tg.stop.request(priority=0) as stop:
                    yield stop
            # Services at junction
            yield self.env.timeout(t_service)
            # Time spent in queue
            t_depart = self.env.now
            t_queue = t_depart - sum(t_arrival)
            # Recursions (move 'car' into next link with probability prob)
            prob = list(turn_ratio.values())
            egress = list(turn_ratio.keys())[np.argmax(multinomial(1, prob))]
            if egress is not 'exit' and egress in self.network.links.keys():
                c = self.car(
                    carID=carID,
                    t_arrival=(t_depart, exponential(self.network.links[egress]['t0'])),
                    node=self.network.links[egress]['node'],
                    turn_ratio=self.network.links[egress]['turns'],
                    linkid=egress
                )
                self.cars[carID].append(egress) # keep track of history
                self.env.process(c)
            # Keep track of the number of cars in the system
            if egress is 'exit':
                self.carsInSystem -= 1
        # Release 1 car from queue
        yield queue.get(1)
        # Update queue length for visualization
        self.updateQueue(queue, linkid)
        # Update queue level
        q_length = queue.level
        # Data logging
        print('car %d departed link %s at %.2fs (Q=%d cars)' % (carID, linkid, t_depart, q_length))
        self.data.append((carID, linkid, 'departure',  t_depart, q_length, t_queue))
        # Prints car travel history
        print('car %d history: %s' % (carID, self.cars[carID]))

    def source(self, demand_duration, LAMBDA, linkid):
        """ Event generator """
        if self.t_max < demand_duration:
            self.t_max = demand_duration
        if linkid not in self.network.links.keys():
            print('Link %s not defined, exiting simulation' % linkid)
            exit()
        while self.env.now < demand_duration:
            arrival_rate = exponential(LAMBDA)
            turn_ratio = self.network.links[linkid]['turns']
            n = self.network.links[linkid]['node']
            t_entry = self.env.now
            t_travel = uniform(0, self.network.links[linkid]['t0'])
            t_arrival = (t_entry, t_travel)
            self.carCounter +=1
            self.carsInSystem +=1
            self.data.append((self.carCounter, linkid, 'entry', t_entry, None, None))
            c = self.car(
                carID=self.carCounter,
                t_arrival=t_arrival,
                node=n,
                turn_ratio=turn_ratio,
                linkid=linkid
            )
            self.cars[self.carCounter] = []
            self.cars[self.carCounter].append(linkid)
            self.env.process(c)
            yield self.env.timeout(arrival_rate)