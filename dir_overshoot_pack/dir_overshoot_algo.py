import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from scipy.signal import argrelmin
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from matplotlib.collections import LineCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from svgpathtools import svg2paths
from svgpath2mpl import parse_path
from PIL import Image
import math
from mpl_toolkits import mplot3d
import seaborn as sns

import mplcursors
class dir_overshooting:
    @staticmethod  
    def extractIndex(valueList, time):
        #######
        conditionIndex = lambda x: x == 1
        indices = [i for i, val in enumerate(valueList) if conditionIndex(val)]
        timeValues = time[indices]
        return indices, timeValues
    
    def __init__(self,file):
        
        #create dataframe
        # data = pd.read_csv(filepath)
        # data_read = pd.read_csv(filepath)
        # data=data_read.drop_duplicates(subset=['timeStamp'], keep='first')
        # data.to_csv('drills/check.csv', index=False)
        self.data1=file
        data=file
        # self.file_path=filepath
        #From Helios
        self.time = data["timeStamp"].values
        print(len(self.time))
        self.drill_duration = max(self.time)
        print(f"Total Drill Duration: {self.drill_duration*0.001:.2f} sec ")
        self.tap = data["tap"].values
        self.start = data["startRotating"].values
        self.end = data["endRotating"].values
        
        self.tap_index = dir_overshooting.extractIndex(self.tap, self.time)[0][1:]
        self.blink_index = dir_overshooting.extractIndex(self.tap, self.time)[0][0]
        self.start_index = dir_overshooting.extractIndex(self.start, self.time)[0]
        self.end_index = dir_overshooting.extractIndex(self.end, self.time)[0]

        print(f"Total number of Points: {len(self.tap_index)}")

        #Linear Acceleration
        self.Xla = data["Xla"].values
        self.Yla = data["Yla"].values
        self.Zla = data["Zla"].values
        self.heading=data['heading']



    def find_direction_overshoot(self):
      overshoot_points=[]
      overshoot_time=[]
      tap_points=[]
      total=0
      # threshold=self.find_heading_threshold()
      
      for taps in range(1,len(self.tap_index)):
        common_elements=[]
        ok_time=30
        start_de=self.tap_index[taps-1]+ok_time
        stop_de=self.tap_index[taps]+ok_time
        turns=[self.time_to_index(j) for j in self.detect_turns()]
        for element in range(start_de,stop_de):
          if element in turns:
              common_elements.append(element)
              # print(len(common_elements))
        if len(common_elements) > 1:
            overshoot_points.append(common_elements[0])
            tap_points.append(start_de-ok_time)
            overshoot=self.time[common_elements[0]]-self.time[self.tap_index[taps-1]]
            total+=overshoot
            overshoot_time.append(overshoot/1000)
            print(f'overshoot time for tap point {taps} : {overshoot} mili seconds')
      
      print(f'total overshoot time: {total} mili seconds')
      return self.index_to_time(overshoot_points),self.index_to_time(tap_points),overshoot_time


    def detect_turns(self,turn_threshold=100, time_window=1500):
      turns = []
      n = len(self.heading)
      i = 0
      while i < n:
          start_time = self.time[i]
          start_heading = self.heading[i]
          # Find the last heading within the time window
          j = i
          while j < n and self.time[j] - start_time <= time_window:
              j += 1
          j -= 1  # Adjust to last valid index
          
          if j > i:  # Ensure we're not comparing a heading to itself
              end_heading = self.heading[j]
              
              # Calculate the smallest angle between the two headings
              heading_change = min(
                  abs(end_heading - start_heading),
                  360 - abs(end_heading - start_heading)
              )
              
              if heading_change > turn_threshold:
                  # turns.append((self.time[i]/1000, self.time[j]/1000, heading_change))
                  # turns.append(self.time_to_index(self.time[i]))
                  turns.append(self.time[i])
                  i = j  # Skip to the index after the detected turn
              else:
                  i += 1  # Move to the next index
          else:
              i += 1  # Move to the next index
      
      return turns


    def time_to_index(self,timestamp):
      time_list=[]
      for i in self.time:
        time_list.append(abs(timestamp-i))
      return time_list.index(min(time_list))


    def mark_dir_overshoot(self):
      data = self.data1
      overshoot_time = []
      tap_over = []

      # Convert timeStamp to seconds
      data['timeStamp'] /= 1000

      # Calculate overall acceleration magnitud
      # Example plot setup
      fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size as needed
      sns.set(style="whitegrid")

      # with plt.style.context('dark_background'):
        # Plot Z acceleration
      ax.plot(data['timeStamp'][self.blink_index:self.tap_index[-1]], 
              data['Zla'][self.blink_index:self.tap_index[-1]], 
              label='Z Acceleration', linewidth=1.5, color='black')  # Adjust line width and color
      ax.plot(data['timeStamp'][self.blink_index:self.tap_index[-1]], 
              data['heading'][self.blink_index:self.tap_index[-1]], 
              label='heading', linewidth=1.5, color='gray')  # Adjust line width and color

      # Use dark background style

      # Mark tap points with vertical lines
      tap_points = data[data['tap'] == 1]
      for timestamp in tap_points['timeStamp']:
          ax.axvline(x=timestamp, color='green', linewidth=2, linestyle='-')  # Adjust line color and style

      # Get mark_tap and mark_stop from self.stop_points()
      mark_stop, mark_tap,_ = self.find_direction_overshoot()

      # Add shaded areas for stopping and overshoot times
      for l in range(len(mark_tap)):
          if mark_stop[l]>mark_tap[l]:
            ax.axvspan(mark_tap[l], mark_stop[l], facecolor='green', alpha=0.4)
            y_b = data['Zla'][self.blink_index-5:self.tap_index[-1]].min()
            ax.text((mark_tap[l] + mark_stop[l]) / 2, y_b, f"Stop Time: {abs((mark_tap[l] - mark_stop[l])):.1f} Sec",
                        fontsize=10, color="black", ha='center')  # Adjust text color and position
            overshoot_time.append(abs((mark_tap[l] - mark_stop[l])))
            tap_over.append(l)
      # Add legend
      handles = [
          plt.Line2D([0], [0], color='black', lw=2),
          plt.Line2D([0], [0], color='green', lw=2, linestyle='--'),
          plt.Rectangle((0, 0), 1, 1, fc='green', alpha=0.4),
      ]
      labels = ['Z Acceleration', 'Tap Points', 'dir Overshoot Time']

      ax.legend(handles=handles, labels=labels, loc='upper right', fontsize=10)  # Adjust legend position and font size
      # Update layout
      ax.set_title('Full Drill chart', fontsize=15, pad=20, color='black')  # Adjust title font size, padding, and color
      ax.set_xlabel('Time (seconds)', fontsize=10, color='black')  # Adjust x-axis label font size and color
      ax.set_ylabel('Acceleration', fontsize=10, color='black')  # Adjust y-axis label font size and color
      ax.grid(True, linestyle='--', alpha=0.6, color='black')  # Add grid lines with adjusted style and color
      ax.tick_params(axis='both', labelsize=8, colors='black')  # Adjust tick label size and color
      ax.xaxis.label.set_color('black')
      ax.yaxis.label.set_color('black')
      # ax.set_xlim([data['timeStamp'][self.blink_index-5:].min(), data['timeStamp'][self.blink_index:self.tap_index[-1]+5].max()])  # Set x-axis limits
      # ax.set_ylim([data['heading'][self.blink_index-5:self.tap_index[-1]].min()-15, data['heading'][self.blink_index:self.tap_index[-1]].max()+15])  # Set y-axis limits with padding
      sns.despine()
      # Save the plot as an image
      image_path = 'pakages/images/dir_overshoot_chart.png'
      plt.savefig(image_path)
      plt.close()
      total_time=(self.time[self.tap_index[-1]]-self.time[self.blink_index])/1000
      return image_path, overshoot_time,total_time,tap_over

    def index_to_time(self,data1):
      time_data=[]
      for i in data1:
        time_data.append(self.time[i]/1000)
      return time_data


if __name__ == '__main__':
  # import pandas as pd
  # df = pd.read_csv("drills/test_drills/neel_squre_overshoot.csv")
  # df = pd.read_csv("drills/test_drills/kevin_long_overshoot.csv")
  # # # df = pd.read_csv("drills/test_drills/top_view_data.csv")
  # df = pd.read_csv("drills/test_drills/ashray_studio_shapes.csv")

  orbit1 = dir_overshooting(df)
  # # # # orbit1 = stopping("drills/test_drills/neel_squre_overshoot.csv")
  # # # # # # orbit1 = stopping("drills/test_drills/ashray_studio_run.csv")
  # # # # orbit1.plot_everything(heading=False,leg_overshoot=False,mark=True) 
  orbit1.mark_dir_overshoot()
  # # print(st) 
