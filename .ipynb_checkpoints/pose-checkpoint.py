# class RobotPose:
#     def __init__(self, dof, links, joints):
#         self.cspace = np.zeros((dof,1))
        
        
        
        
import numpy as np
import quaternion

class Transform3D:
    def __init__(self, x, y, z, r, p, w):
        self.translation = np.array([x, y, z])
        self.quaternion = quaternion.from_euler_angles([r, p, w])
        
    def as_dcm(self):
        return quaternion.as_rotation_matrix(self.quaternion)
    
    def transform(self, v):
        dcm = self.as_dcm()
        return (dcm @ v) + self.translation

class Joint:
    def __init__(self, name, x, y, z, r, p, w):
        self.name = name
        self.tf = Transform3D(x, y, z, r, p, w)
        self.children = []

class JointTree:
    def __init__(self):
        self.head = Joint(0, 0, 0, 0, 0, 0)

    def add_joint(self, x, y, z, r, p, w)