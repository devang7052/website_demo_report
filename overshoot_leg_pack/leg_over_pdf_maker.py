

from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

class PDF_leg(FPDF):
    def __init__(self, image1, data1,time1,tap_points,file_name1 ,orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.img_path = image1
        self.data = data1
        self.total_time=time1
        self.total_overshoot_time=sum(self.data)
        self.set_auto_page_break(auto=True, margin=15)
        self.tap_points=tap_points
        self.file_name=file_name1
        # self.add_font('Times', '', 'Roboto-Regular.ttf', uni=True)
        # self.add_font('Times', 'B', 'Roboto-Bold.ttf', uni=True)
        # self.add_font('Times', 'I', 'Roboto-Italic.ttf', uni=True)

    def header(self):
        self.set_font('Times', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'IMU ANAYLYSIS', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Times', 'B', 18)
        # self.set_text_color(100, 100, 100)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(15)

    def chapter_body(self, img_path):
        self.image(img_path, x=10, w=190)
        self.ln(10)

    def create_table(self):
        if len(self.tap_points)>0:
            self.set_font('Times', 'B', 12)
            self.set_fill_color(200, 220, 255)
            self.cell(95, 10, 'Point Number', 1, 0, 'C', 1)
            self.cell(95, 10, 'Stop Time (s)', 1, 1, 'C', 1)
            
            # Table data
            self.set_font('Times', 'B', 12)
            self.set_fill_color(255, 255, 255)
            for i, stop_time in enumerate(self.data, start=0):
                self.cell(95, 10, str(self.tap_points[i]+1), 1, 0, 'C', 1)
                self.cell(95, 10, f"{stop_time:.2f}", 1, 1, 'C', 1)
            
            self.ln(10)
        else:
            self.set_font('Times', 'B', 16)
            self.set_text_color(0, 128, 0)  # Green color
            
            # Draw rectangle
            self.set_fill_color(200, 255, 200)  # Light green background
            self.rect(10, self.get_y(), 190, 20, 'DF')
            
            # Write message
            self.cell(0, 20, 'Congratulations, no overshoot!', 0, 1, 'C')
            
            # Restore font and color settings
            self.set_font('Times', '', 12)
            self.set_text_color(0, 0, 0)

                

    def make_pi_chart(self):

        sizes = [self.total_time, self.total_overshoot_time]
        labels = [f'Total Time\n({self.total_time:.1f} sec)', f'Overshoot Time\n({self.total_overshoot_time:.1f} sec)']
        colors = ['#4B79A1', '#FF416C']

        overshoot_percentage = (self.total_overshoot_time / self.total_time) * 100

        # Create the donut chart
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        startangle=90, pctdistance=0.85, wedgeprops=dict(width=0.3))

        # Add a circle at the center to create a donut chart
        center_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(center_circle)

        # Customize the chart
        # plt.title("Overshoot Time as Percentage of Total Time", fontsize=18, fontweight='bold', pad=20)
        plt.setp(autotexts, size=10, weight="bold")
        plt.setp(texts, size=12)

        # Add total time in the center
        ax.text(0, 0, f"Total overshoot Time\n{self.total_overshoot_time:.1f} sec", ha='center', va='center', fontsize=14, fontweight='bold')

        # Add a custom legend
        ax.legend(wedges, labels,
                title="Time Distribution",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1))

        # Set the background color
        fig.patch.set_facecolor('#F5F7FA')

        plt.tight_layout()
        # plt.show()
        pichart_img_path = 'pakages/images/pi_chart.png'
        plt.savefig(pichart_img_path, bbox_inches='tight')
        self.pichart_img_path = pichart_img_path
        plt.close()
 

    def make_pdf_over(self):
        self.add_page()
        self.chapter_title('Overshoot Timing Analysis Report')
        self.chapter_body(self.img_path)
        
        self.add_page()
        self.chapter_title('Overshoot Timing Table')
        self.create_table()
        self.ln(15)

        self.add_page()
        self.chapter_title("Overshoot Time as Percentage of Total Time")
        self.make_pi_chart()
        self.chapter_body(self.pichart_img_path)
        self.output(f'pakages/pdf_s/{self.file_name}.pdf')
        return f'{self.file_name}.pdf'
# Example usage:
#okmfnfnk

if __name__=='__main__':
    obj=PDF_leg(r'E:\internship\hyperlab\Hyperlab-Imu-Analytics\overlapped.png',[2.3],10,[2])
    obj.make_pi_chart()