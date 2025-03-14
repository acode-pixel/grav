import math, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class obj:
  
  def __init__(self, coords=[0.0, 0.0], mass=1, speed=[0.0, 0.0], lockPos=False):
    self.mass = mass
    self.coords = np.array(coords, dtype=float)
    self.speed = np.array(speed, dtype=float) #sq units/s
    self.lockPos = lockPos
    self.points = []
    self.points.append([self.coords[0], self.coords[1]])
  
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
    
    self.fig, self.ax = plt.subplots()
    self.dt_array = np.zeros(self.frames, dtype=float)
    self.prog_dt = 0
  
  def start(self):
    self.frames = 1
    self.ax.set_xlim([-350, 350])
    self.ax.set_ylim([-350, 350])
    plot = []
    i = 0
    
    while i < len(self.objs):
      plot.append(plt.plot([], [], marker="o"))
      i += 1
      
    def frames():
      while True:
        yield self.calculate()
    
    def animate(objs):
      i = 0
      while i < len(objs):
        point = self.objs[i].coords
        plot[i][0].set_data([point[0]], [point[1]])
        i += 1
      return plot
      
    ani = animation.FuncAnimation(self.fig, animate, frames=frames, save_count=120, interval=0)
    plt.show()
  
  def create_obj(self, pos=[0, 0], mass=1, speed=[0, 0], lockPos=False):
    self.objs.append(obj(pos, mass, speed, lockPos))
  
  def calculate(self):
    if self.liveSim:
      frames_count = 0
      while frames_count < self.frames:
        i = 0
        while i < len(self.objs):
          self.objs[i].update(self.objs)
          i += 1
        frames_count += 1
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
      print(f"[Calculations] delta time mean: {round(self.dt_array.mean(), 2)}ns")
  
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
      self.ax.set_xlim([-100, 100])
      self.ax.set_ylim([-100, 100])
      
      i = 0
      while i < len(self.objs):
        dot, = self.ax.plot([], [], marker="o")
        dots.append(dot)
        i += 1
      return dots
    
    ani = animation.FuncAnimation(self.fig, update, self.frames, init_func=init, blit=True)
    ani.save('animation_drawing.mp4', writer=animation.FFMpegWriter(fps=self.fps, bitrate=5000, codec='h264'))
    dt = time.time() - self.prog_dt
    print(f"[Animation rendering] delta time mean: {round(self.dt_array.mean(), 2)}ns")
    print(f"[Total processing] total time: {round(dt, 2)}s")
    
if __name__ == "__main__":
  sim1 = sim(secs=240, liveSim=True)
  sim1.create_obj([0, 0],30, lockPos=True)
  sim1.create_obj([50, 20], 5, speed=[-0.05, -0.55])
  sim1.create_obj([75, 0], 5, speed=[-0.15, -0.65])
  
  #sim1.calculate()
  #sim1.render()
  sim1.start()
