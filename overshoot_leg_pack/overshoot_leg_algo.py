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
import mplcursors
class leg_overshooting:
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
        
        self.tap_index = leg_overshooting.extractIndex(self.tap, self.time)[0][1:]
        self.blink_index = leg_overshooting.extractIndex(self.tap, self.time)[0][0]
        self.start_index = leg_overshooting.extractIndex(self.start, self.time)[0]
        self.end_index = leg_overshooting.extractIndex(self.end, self.time)[0]

        print(f"Total number of Points: {len(self.tap_index)}")

        #Linear Acceleration
        self.Xla = data["Xla"].values
        self.Yla = data["Yla"].values
        self.Zla = data["Zla"].values


    def find_leg_overshoot(self):
      import numpy as np
      from scipy.signal import find_peaks
      peaks, hight = find_peaks(self.Zla, height=0)  # height=0 ensures that all peaks are found, regardless of height
      ok=[]
      tap_time=[]
      stop_time=[]
      overshoot_time=[]
      # print(peaks,hight)
      total=0
      for peak in peaks:
        ok.append(self.Zla[peak])
      thresh=np.mean(ok)
      print(f't:{thresh}')
      for i in range(0,len(self.tap_index)-1):
        count=0
        if i==0:
          start_check=self.tap_index[i]-(self.tap_index[i]-self.blink_index)*0.2
        else:
          start_check=self.tap_index[i]-(self.tap_index[i]-self.tap_index[i-1])*0.2

        stop_check=self.tap_index[i]+(self.tap_index[i+1]-self.tap_index[i])*0.6
        for j in range(int(start_check),int(stop_check)):
            if self.Zla[j]<thresh:
              count+=self.time[j+1]-self.time[j]
            else:
              count=0
            tolerance=200
            red_flag=0
            if count>tolerance:
                tap_time.append(self.time[self.tap_index[i]]/1000)
                stop_time.append((self.time[j]-tolerance)/1000)
                break
      return tap_time,stop_time



    def time_to_index(self,timestamp):
      time_list=[]
      for i in self.time:
        time_list.append(abs(timestamp-i))
      return time_list.index(min(time_list))



    def mark_overshoot(self):
      # Example data setup (replace with your actual data)
      data = self.data1
      overshoot_time = []
      tap_over = []

      # Convert timeStamp to seconds
      data['timeStamp'] /= 1000

      # Calculate overall acceleration magnitud
      # Example plot setup
      fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size as needed

      with plt.style.context('dark_background'):
        # Plot Z acceleration
        ax.plot(data['timeStamp'][self.blink_index:self.tap_index[-1]], 
                data['Zla'][self.blink_index:self.tap_index[-1]], 
                label='Z Acceleration', linewidth=1.5, color='black')  # Adjust line width and color

        # Use dark background style

        # Mark tap points with vertical lines
        tap_points = data[data['tap'] == 1]
        for timestamp in tap_points['timeStamp']:
            ax.axvline(x=timestamp, color='green', linewidth=2, linestyle='-')  # Adjust line color and style

        # Get mark_tap and mark_stop from self.stop_points()
        mark_tap, mark_stop = self.find_leg_overshoot()

        # Add shaded areas for stopping and overshoot times
        for l in range(len(mark_tap)):
            if mark_stop[l]>mark_tap[l]:
              ax.axvspan(mark_tap[l], mark_stop[l], facecolor='red', alpha=0.4)
              y_b = data['Zla'][self.blink_index-5:self.tap_index[-1]].min()
              ax.text((mark_tap[l] + mark_stop[l]) / 2, y_b, f"Stop Time: {abs((mark_tap[l] - mark_stop[l])):.1f} Sec",
                          fontsize=10, color="black", ha='center')  # Adjust text color and position
              overshoot_time.append(abs((mark_tap[l] - mark_stop[l])))
              tap_over.append(l)
        # Add legend
        handles = [
            plt.Line2D([0], [0], color='white', lw=2),
            plt.Line2D([0], [0], color='green', lw=2, linestyle='--'),
            plt.Rectangle((0, 0), 1, 1, fc='blue', alpha=0.4),
            plt.Rectangle((0, 0), 1, 1, fc='red', alpha=0.4)
        ]
        labels = ['Z Acceleration', 'Tap Points', 'Stopping Time', 'Overshoot Time']
        ax.legend(handles=handles, labels=labels, loc='upper right', fontsize=10)  # Adjust legend position and font size

        # Update layout
        ax.set_title('Full Drill chart', fontsize=15, pad=20, color='white')  # Adjust title font size, padding, and color
        ax.set_xlabel('Time (seconds)', fontsize=10, color='white')  # Adjust x-axis label font size and color
        ax.set_ylabel('Acceleration', fontsize=10, color='white')  # Adjust y-axis label font size and color
        ax.grid(True, linestyle='--', alpha=0.6, color='black')  # Add grid lines with adjusted style and color
        ax.tick_params(axis='both', labelsize=8, colors='white')  # Adjust tick label size and color
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.set_xlim([data['timeStamp'][self.blink_index-5:].min(), data['timeStamp'][self.blink_index:self.tap_index[-1]+5].max()])  # Set x-axis limits
        ax.set_ylim([data['Zla'][self.blink_index-5:self.tap_index[-1]].min()-15, data['Zla'][self.blink_index:self.tap_index[-1]].max()+15])  # Set y-axis limits with padding

        # Save the plot as an image
        image_path = 'pakages/images/overshoot_chart.png'
        plt.savefig(image_path)
        plt.close()
      total_time=(self.time[self.tap_index[-1]]-self.time[self.blink_index])/1000
      return image_path, overshoot_time,total_time,tap_over

  # Call the function


    def index_to_time(self,data1):
      time_data=[]
      for i in data1:
        time_data.append(self.time[i]/1000)
      return time_data


# if __name__ == '__main__':
  # import pandas as pd
  # # df =pd.read_csv("drills/test_drills/neel_squre_overshoot.csv")
  # # df = pd.read_csv("drills/test_drills/kevin_long_overshoot.csv")
  # # df = pd.read_csv("drills/test_drills/top_view_data.csv")
  # df = pd.read_csv("drills/test_drills/ashray_studio_shapes.csv")

  # orbit1 = leg_overshooting(df)
  # # # # orbit1 = stopping("drills/test_drills/neel_squre_overshoot.csv")
  # # # # # # orbit1 = stopping("drills/test_drills/ashray_studio_run.csv")
  # # # # orbit1.plot_everything(heading=False,leg_overshoot=False,mark=True) 
  # _,st,_=orbit1.mark_overshoot()
  # # print(st) 
