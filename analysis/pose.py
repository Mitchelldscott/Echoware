import numpy as np

STARFISH_LEGS = 5
DRAWING_COLORS = np.array(['r', 'g', 'b', 'c', 'm', 'k', 'y'])

def rotateX(point, theta):
	R = np.array([[ 1,             0,             0],
				  [ 0, np.cos(theta), np.sin(theta)],
				  [ 0,-np.sin(theta), np.cos(theta)]])
	return R @ point

def rotateY(point, theta):
	R = np.array([[ np.cos(theta), 0,-np.sin(theta)],
				  [ 0,             1,             0],
				  [ np.sin(theta), 0, np.cos(theta)]])
	return R @ point

def rotateZ(point, theta):
	R = np.array([[ np.cos(theta), np.sin(theta), 0],
				  [-np.sin(theta), np.cos(theta), 0],
				  [ 0,             0,             1]])
	return R @ point

def starfish_ee(alpha):
	n_legs = STARFISH_LEGS
	
	if not type(alpha) is list:
		alpha = alpha*np.ones(n_legs)
		
	return np.array([rotateZ(rotateY([1,0,0], alpha[i]), 2*np.pi*i/n_legs) for i in range(n_legs)])

def starfish_pose(alpha):
	return np.vstack([np.zeros((1,3)), starfish_ee(alpha)]) # add origin as a landmark

class Pose:
	def __init__(self, links, key_points):
		self.links = np.array(links)
		self.key_points = np.array(key_points)
		self.end_effectors = []
		effectors = np.array([point for (point, _) in links])
		for link in links:
		    if not link[1] in effectors:
		        self.end_effectors.append(link[1])

	def normalize(self):
		chain_norms = [np.linalg.norm(self.key_points[i]) for i in self.end_effectors]

		norm_min = 1e50
		for chain in self.chains():
		    norm = 0
		    prev_idx = chain[0]
		    for idx in chain[1:]:
		        norm += np.linalg.norm(self.key_points[idx] - self.key_points[prev_idx])
		        prev_idx = idx
		        
		    norm_min = np.min([norm_min, norm])

		self.key_points *= 1/(norm_min)

	def end_effectors_world(self):
		return self.key_points[self.end_effectors]

	def chains(self):
		chains = [[ee] for ee in self.end_effectors]

		n = len(self.end_effectors)
		for i in range(n):
			while chains[i][-1] != 0:
				for link in self.links:
					if link[1] == chains[i][-1]:
						chains[i].append(link[0])
						break

			chains[i].reverse()
			
		return chains

	def get_matches(self, key_points):
		n = len(self.end_effectors)
		m = len(key_points)

		matches = np.zeros(n, dtype=np.int8)
		
		for i in range(n):
			curr_match = np.zeros(m)
			for j in range(m):
				curr_match[j] = np.dot(key_points[j,:], self.key_points[self.end_effectors[i],:])

			if np.max(curr_match) > 0:
				matches[i] = np.argmax(curr_match)
			else:
				matches[i] = -1
				
		return matches

	def draw_pose(self, ax, highlight_points, link_color='b', joint_color=['r'], elev=0, azim=0, base=0):
	
		for link in self.links:
			x = self.key_points[link,0]
			y = self.key_points[link,1]
			z = self.key_points[link,2]
			ax.plot(x, y, z, link_color)
	
		if len(highlight_points) != len(joint_color):
			if len(joint_color) == 0:
				joint_color = ['r']
	
			joint_color = [DRAWING_COLORS[i%len(DRAWING_COLORS)] for i in range(len(highlight_points))]

		if base:
			ax.plot(self.key_points[0,0], self.key_points[0,1], self.key_points[0,2], color='k', marker='o')
			
		ax.scatter(self.key_points[highlight_points,0], self.key_points[highlight_points,1], self.key_points[highlight_points,2], color=joint_color, marker='o')
		ax.set_xlabel('x [m]')
		ax.set_ylabel('y [m]')
		ax.set_xlim([-1,1])
		ax.set_ylim([-1,1])
		ax.set_zlim([-1,1])
		ax.view_init(elev=elev-180, azim=azim-90)
		