

from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

class PDF(FPDF):
    def __init__(self, image1, data1, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.img_path = image1
        self.data = data1
        self.set_auto_page_break(auto=True, margin=15)
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
        self.set_font('Times', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(95, 10, 'Point Number', 1, 0, 'C', 1)
        self.cell(95, 10, 'Stop Time (s)', 1, 1, 'C', 1)
        
        # Table data
        self.set_font('Times', 'B', 12)
        self.set_fill_color(255, 255, 255)
        for i, stop_time in enumerate(self.data, start=1):
            self.cell(95, 10, str(i), 1, 0, 'C', 1)
            self.cell(95, 10, f"{stop_time:.2f}", 1, 1, 'C', 1)
        
        self.ln(10)

                

    def make_stop_chart(self):
        stop_times = self.data
        points = list(range(1, len(stop_times) + 1))
        average_stop_time = np.mean(stop_times)
        min_stop_time = np.min(stop_times)
        max_stop_time = np.max(stop_times)
        
        # plt.style.use('_classic_test_patch')
        # plt.style.use('dark_background')
        plt.figure(figsize=(10, 6))
        
        # Plotting the bars
        bar_width = 0.3
        plt.bar(points, stop_times, width=bar_width, color='#4472C4', label='Stop Time')
        
        # Plotting horizontal lines for average, min, max
        plt.axhline(average_stop_time, color='#ED7D31', linestyle='--', linewidth=2, label='Average Stop Time')
        plt.axhline(min_stop_time, color='#70AD47', linestyle='--', linewidth=2, label='Min Stop Time')
        plt.axhline(max_stop_time, color='#FF0000', linestyle='--', linewidth=2, label='Max Stop Time')
        
        plt.text(len(points) + 1, average_stop_time, f'Average: {average_stop_time:.2f}', 
                 color='#ED7D31', fontsize=12, verticalalignment='bottom', horizontalalignment='left')
        plt.text(len(points) + 1, min_stop_time, f'Min: {min_stop_time:.2f}', 
                 color='#70AD47', fontsize=12, verticalalignment='top', horizontalalignment='left')
        plt.text(len(points) + 1, max_stop_time, f'Max: {max_stop_time:.2f}', 
                 color='#FF0000', fontsize=12, verticalalignment='bottom', horizontalalignment='left')
        
        plt.title('Stop Times Analysis', fontsize=18, fontweight='bold')
        plt.xlabel('Points', fontsize=14)
        plt.ylabel('Stop Time', fontsize=14)
        plt.legend(fontsize=12)
        plt.xticks(points, fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        
        chart_img_path = 'images/stop_chart.png'
        plt.savefig(chart_img_path, bbox_inches='tight', dpi=300)
        self.chart_img_path = chart_img_path
        plt.close()

    def make_pdf(self):
        self.add_page()
        self.chapter_title('Stop Timing Analysis Report')
        self.chapter_body(self.img_path)
        
        self.add_page()
        self.chapter_title('Stop Timing Table')
        # self.make_table()
        self.create_table()
        # self.chapter_body(self.table_image)
        self.ln(15)
        # self.add_page()
        self.chapter_title('Stop Times Analysis')
        self.make_stop_chart()
        self.chapter_body(self.chart_img_path)
        
        self.output('pdf_s/output_stop.pdf')

        return 'output_stop.pdf'
