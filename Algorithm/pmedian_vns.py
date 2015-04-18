import csv
import math
import copy
import time
import random
from random import shuffle

class VariableNeighborhoodSearch:

	def __init__(self, numOfP, file_name, out_file, cost_output):
		self.numOfP = numOfP
		self.file_name = file_name
		self.coordinates=[]
		self.sumkey = dict()
		self.out_file = out_file
		self.cost_output = cost_output
		self.best_solution = dict()
		
		

	def readFile(self):
		coordinates = self.coordinates
		with open(self.file_name,'r') as f:
			next(f) # skip headings
			reader=csv.reader(f,delimiter=' ')
			for row in reader:
				if len(row) == 3: row = row[1:3]
				coordinates.append(row)
		f.close()		

	def calculateDistance(self, x1, x2, y1, y2):
		distance = math.sqrt(pow((x1 -x2),2) + pow((y1 - y2),2))
		return distance


	def distanceCalculation (self):

		coordinates = self.coordinates
		self.distances = [[0 for i in range(len(coordinates))] for j in range(len(coordinates))]
		distances = self.distances
		
		# calculation of the euclidean distance of every node with each other
		# producing a 2 dimansional symmetric matrix with 0 in the main diagonial
		for i in range(len(coordinates)):
			for k in range(i):
				distances[i][k] = distances[k][i]
			for j in range(i, len(coordinates)):
				distances[i][j] = self.calculateDistance(float(coordinates[i][0]),
					float(coordinates[j][0]), float(coordinates[i][1]), float(coordinates[j][1]))

		# making a copy of the distances matrix for keeping the initial
		# without any changes and using the new one for our calculations
		#self.neighborhood_distances = copy.deepcopy(distances)	
		return distances

	
	def assignNodes(self):
		pmedian = self.pmedian
		node_assign = self.node_assign
		distances = self.distances

		# create empty dictionary with key every pmedian node
		# and values the list of the nodes getting assigned
		# to the pmedian node
		for i in range(len(pmedian)):
			node_assign[pmedian[i]] = []

		# write to temp list the distances of each node from the
		# ones selected as pmedians and assign the current node
		# to the pmedian node with the minimum distance
		for i in range(len(distances)):
			temp=[]
			for j in range(len(pmedian)):
				temp.append(distances[pmedian[j]][i])
			node_assign[pmedian[temp.index(min(temp))]].append(i)

	

	def shaking(self, shake_list):
		shuffle( shake_list )
		while shake_list:
  			yield shake_list.pop()


	def localSearch(self, key):
		distances = self.distances
		sumkey = self.sumkey
		node_assign = self.node_assign
				
		rand_key = self.shaking(self.neigh_list)
		rand_key = rand_key.next()
		while rand_key == key:
			if (len(self.neigh_list) <= 0): break
			rand_key = self.shaking(self.neigh_list)
			rand_key = rand_key.next()
				
		sumkey[rand_key] = 0

		for i in range(len(node_assign[key])):
			sumkey[rand_key] = sumkey[rand_key] + distances[rand_key][node_assign[key][i]]
			
		return (rand_key, len(self.neigh_list))

	def output(self, best_solution):

		outfile = open(self.out_file, 'a')
		#best_solution = self.best_solution
		for key in best_solution.iterkeys():
			outfile.write(str(key) +": "+ str(best_solution[key]))
			outfile.write("\n")
			outfile.write("\n")

		outfile.write("\n")

		outfile.close()
		

	def findPMedian(self, times2run):
		sumkey = self.sumkey
		best_solution = self.best_solution		
		
		# read the input data
		self.readFile()
				
		# calculate nodes distances from their coordinates
		distances = self.distanceCalculation() 
		
		cost_plot = open(self.cost_output, 'a')
		
		for run in range(times2run):
			self.time_start = time.time()

			self.node_assign = dict()
			node_assign = self.node_assign
			self.pmedian = []
			
			# calculate the minimum distances as many times as
			# the number of the pmedian nodes need to be found
			self.nodes = range(len(self.coordinates))
			for facility in range(self.numOfP):
				self.pmedian.append(self.shaking(self.nodes).next())
							
			# assign each node to a pmedian node
			self.assignNodes()

			for key in node_assign.iterkeys():
				sumkey[key] = 0
				for i in range(len(node_assign[key])):
					sumkey[key] = sumkey[key] + distances[key][node_assign[key][i]]

		    				
			for key in node_assign.iterkeys():
                            
				self.neigh_list = copy.deepcopy(node_assign[key])
				if (len(self.neigh_list) > 0) :(rand_key, nodes_left) = self.localSearch(key)
				
				if sumkey[rand_key] < sumkey[key]:
					node_assign[rand_key] = node_assign.pop(key)
					if ((nodes_left) > 0): (rand_key, nodes_left) = self.localSearch(rand_key)
			

			cost = 0
			for key, value in node_assign.iteritems():
				cost = cost + sumkey[key]
			if run == 0 : 
				best_solution['cost'] = cost
				best_solution['repetition'] = run
				best_solution['time'] = time.time()-self.time_start
				best_solution['pmedian'] = dict()
				for key in node_assign.iterkeys():
					best_solution['pmedian'][key] = node_assign[key]
			else:
				if cost < best_solution['cost']:
					best_solution = dict()
					best_solution['pmedian'] = dict()
					best_solution['cost'] = cost
					best_solution['repetition'] = run
					best_solution['time'] = time.time()-self.time_start
					for key in node_assign.iterkeys():
						best_solution['pmedian'][key] = node_assign[key]

			cost_plot.write(str(cost))
			cost_plot.write("\n")
	
		cost_plot.close()	
		self.output(best_solution)

		
out_file = 'fl1400_50'
cost_output = out_file +'cost.dat'
total_time = time.clock()
times2run = 5000
pmedian = VariableNeighborhoodSearch (50, 'fl1400.tsp', out_file, cost_output)
pmedian.findPMedian(times2run)

total_elapsed = time.clock() - total_time
outfile = open(out_file, 'a')
outfile.write('Total run time: '+str(total_elapsed)+' sec')
outfile.write("\n")
outfile.write("\n")
outfile.close()
