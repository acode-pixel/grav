import math, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class obj:
  
  def __init__(self, x, y):
    self.mass = 0
    self.coords = [x, y]
    self.speed = [0,0]#sq units/s
    self.lockPos = False
    self.points = []
    self.points.append([self.coords[0], self.coords[1]])
  
  def push(self,x,y):
    self.speed[0] += x 
    self.speed[1] += y 
  
  def update(self, otherObjs):
    if self.lockPos:
      self.points.append([self.coords[0], self.coords[1]])
      return
    
    if len(otherObjs) != 0:
      for i in otherObjs:
        inflence = self.getInfluencefromObj(i)
        self.push(inflence[0],inflence[1])
    
    self.coords[0] += self.speed[0]
    self.coords[1] += self.speed[1]
    
    self.points.append([self.coords[0], self.coords[1]])
    
  def getInfluencefromObj(self, otherObj):
    if self == otherObj:
      return [0,0]
    localCoords = [self.coords[0]-otherObj.coords[0],self.coords[1]-otherObj.coords[1]]
    influence = [0,0]  
    distanceX = math.dist([0,0],[localCoords[0],0])
    distanceY = math.dist([0,0],[0,localCoords[1]])
    distance = math.dist([0,0],localCoords)
    
    g = (otherObj.mass**2)/((distance**2)*2*math.pi) #if distance != 0 and distance <= otherObj.mass**2.0 else 0
    influence[0] = (g * (distanceX/distance))/self.mass
    influence[1] = (g * (distanceY/distance))/self.mass
    
    
    #influence[0] = 0 if distance == 0 or distance >= otherObj.mass**2.0 else (otherObj.mass**2.0)/(distanceX**2)*2*math.pi
    #influence[1] = 0 if distance == 0 or distance >= otherObj.mass**2.0 else (otherObj.mass**2.0)/(distanceY**2)*2*math.pi
    
    influence[0] = -influence[0] if localCoords[0] > 0 else influence[0]
    influence[1] = -influence[1] if localCoords[1] > 0 else influence[1]
    
    #influence[0] = influence[0] if influence[0] < otherObj.mass else otherObj.mass
    #influence[1] = influence[1] if influence[1] < otherObj.mass else otherObj.mass
    
    #print(f" local coords: {localCoords}, influence: {influence}")
    
    return influence
      
  def print(self):
    print(f"coords: {self.coords}, speed: {self.speed}")
  
if __name__ == "__main__":
  obj1 = obj(10, 10)
  obj2 = obj(0, 0)
  #obj3 = obj(-5, -10)
  objs = []
  objs.append(obj1)
  objs.append(obj2)
  #objs.append(obj3)
  obj1.mass = 5
  obj2.mass = 10
  obj2.lockPos = True
  #obj3.mass = 5
  obj1.push(-0.5, 0)
  obj2.push(0, 0)
  #obj3.push(0.7, 0)
  
  fig, ax = plt.subplots()
  
  while len(obj1.points) <= 1800:
    i = 0
    while i < len(objs):
      objs[i].update(objs)
      i += 1
    #obj1.print()
    #obj2.print()
    #input()
    #print(f"{pointsOfObj1[i]}, {i}, {dt}")
    
    
  def update(num):
    ax.clear()
    i = 0
    
    while i < len(objs):
      point = objs[i].points[num]
      print(f"points: {point}, i: {i}, frame: {num}")
      ax.plot(point[0], point[1], marker='o')
      i += 1
      
    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
      
      
    
  
  ani = animation.FuncAnimation(fig, update, len(obj1.points))
  ani.save('animation_drawing.mp4', writer=animation.FFMpegWriter(fps=60, bitrate=5000, codec='h264'))

  #plt.plot(np.array([obj1.coords[0], obj2.coords[0]]), np.array([obj1.coords[1], obj2.coords[1]]), 'o')
  #plt.show()
  

