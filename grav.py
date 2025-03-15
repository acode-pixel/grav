import math, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy.ndimage import shift

class obj:
  
  def __init__(self, coords=[0.0, 0.0], mass=1, speed=[0.0, 0.0], lockPos=False):
    self.mass = mass
    self.coords = np.array(coords, dtype=float)
    self.speed = np.array(speed, dtype=float) #sq units/s
    self.lockPos = lockPos
    self.points = []
    self.speedArray = np.zeros((100), dtype=float)
    self.points.append([self.coords[0], self.coords[1]])
    self.i = 0
  
  def push(self,x,y):
    self.speed += np.array([x, y], dtype=float)
  
  def update(self, otherObjs):
    if self.lockPos:
      self.points.append([self.coords[0], self.coords[1]])
      return
    
    if len(otherObjs) != 0:
      for i in otherObjs:
        inflence = self.getInfluencefromObj(i)
        self.push(inflence[0],inflence[1])
    
    self.coords += self.speed
    
    if self.i < 100:
      self.speedArray[self.i] = np.sqrt((self.speed**2).sum())
      self.i += 1
    else:
      self.speedArray = shift(self.speedArray, -1)
      self.speedArray[self.i-1] = np.sqrt((self.speed**2).sum())
      
    self.points.append([self.coords[0], self.coords[1]])
    
  def getInfluencefromObj(self, otherObj):
    if self == otherObj:
      return [0,0]
    localCoords = self.coords - otherObj.coords
    influence = np.array([0, 0], dtype=float)
    axis_distances = np.array([0, 0], dtype=float)
    axis_distances[0] = math.dist([0,0],[localCoords[0],0])
    axis_distances[1] = math.dist([0,0],[0,localCoords[1]])
    distance = math.dist([0,0],localCoords)
    
    g = (otherObj.mass**2)/((distance**2)*2*math.pi) # G = M^2 / 2pi * d^2
    influence = (g * (axis_distances/distance))/self.mass
    
    influence[0] = -influence[0] if localCoords[0] > 0 else influence[0]
    influence[1] = -influence[1] if localCoords[1] > 0 else influence[1]
    
    return influence
      
  def print(self):
    print(f"coords: {self.coords}, speed: {self.speed}")
    
class sim:
  def __init__(self, name="Sim-Test", secs=25, fps=60, liveSim=False):
    self.name = name
    self.objs = []
    self.frames = fps*secs
    self.fps = fps
    self.liveSim = liveSim
    
    self.fig, self.axs = plt.subplots(2, 1)
    self.dt_array = np.zeros(self.frames, dtype=float)
    self.prog_dt = 0
  
  def start(self):
    if self.liveSim == False:
      self.calculate()
      self.render()
      return
    
    self.frames = 1
    self.axs[0].set_xlim([-350, 350])
    self.axs[0].set_ylim([-350, 350])
    plot = []
    i = 0
    
    while i < len(self.objs):
      plot.append(self.axs[0].plot([], [], marker="o"))
      i += 1
      
    def frames():
      while True:
        yield self.calculate()
        
    def animate(objs):
      i = 0
      self.axs[1].clear()
      while i < len(objs):
        point = self.objs[i].coords
        plot[i][0].set_data([point[0]], [point[1]])
        self.axs[1].plot(np.arange(self.objs[i].i), self.objs[i].speedArray[:self.objs[i].i])
        i += 1
      return self.axs
      
    ani = animation.FuncAnimation(self.fig, animate, frames=frames, save_count=120, interval=0)
    plt.show()
  
  def create_obj(self, pos=[0, 0], mass=1, speed=[0, 0], lockPos=False):
    self.objs.append(obj(pos, mass, speed, lockPos))
  
  def calculate(self):
    if self.liveSim:
      frames_count = 0
      while frames_count < self.frames:
        i = 0
        past_dt = time.perf_counter_ns()
        while i < len(self.objs):
          self.objs[i].update(self.objs)
          i += 1
        dt = time.perf_counter_ns() - past_dt
        frames_count += 1
        self.axs[0].set_xlabel(f"Calculation time: {round((dt/1000), 2)}μs")
      return self.objs
    else:
      self.prog_dt = time.time()
      dt_i = 0
      frames_count = 0
      while frames_count < self.frames:
        i = 0
        past_dt = time.perf_counter_ns()
        while i < len(self.objs):
          self.objs[i].update(self.objs)
          i += 1
      
        dt = time.perf_counter_ns() - past_dt
        self.dt_array[dt_i] = dt
        dt_i += 1
        frames_count += 1
      print(f"[Calculations] delta time mean: {round((self.dt_array.mean()/1000), 2)}μs")
  
  def render(self):
    self.dt_array.fill(0)
    dots = []
    
    def update(num):
      i = 0
      past_dt = time.perf_counter_ns()
      while i < len(self.objs):
        point = self.objs[i].points[num]
        #print(f"points: {point}, i: {i}, frame: {num}")
        dots[i].set_data([point[0]], [point[1]])
        i += 1
      dt = time.perf_counter_ns() - past_dt
      self.dt_array[num-1] = dt
      return dots
    
    def init():
      self.axs[0].set_xlim([-100, 100])
      self.axs[0].set_ylim([-100, 100])
      
      i = 0
      while i < len(self.objs):
        dot, = self.axs[0].plot([], [], marker="o")
        dots.append(dot)
        i += 1
      return dots
    
    ani = animation.FuncAnimation(self.fig, update, self.frames, init_func=init, blit=True)
    ani.save('animation_drawing.mp4', writer=animation.FFMpegWriter(fps=self.fps, bitrate=5000, codec='h264'))
    dt = time.time() - self.prog_dt
    print(f"[Animation rendering] delta time mean: {round((self.dt_array.mean()/1000), 2)}μs")
    print(f"[Total processing] total time: {round(dt, 2)}s")
    
if __name__ == "__main__":
  sim1 = sim(secs=60, liveSim=True)
  sim1.create_obj([0, 0],30, lockPos=True)
  sim1.create_obj([50, 20], 5, speed=[-0.05, -0.55])
  sim1.create_obj([75, 0], 5, speed=[-0.155, -0.65])
  sim1.start()
