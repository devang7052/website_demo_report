from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import time
from stop_pack.stop_algo import stopping
from overshoot_leg_pack.overshoot_leg_algo import leg_overshooting
from overshoot_leg_pack.leg_over_pdf_maker import PDF_leg
from stop_pack.stop_pdf_maker import PDF
from dir_overshoot_pack.dir_overshoot_algo import dir_overshooting

import os
app = Flask(__name__)
generation_status={}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        data = pd.read_csv(file)
        option = request.form['option']
        csv_file=extract_between_file(str(file))
        task_id = str(time.time())
        generation_status[task_id] = 'processing'
        file_name=process_data(data, option,csv_file)
        pdf_file_path= f'E:/internship/hyperlab/Hyperlab-Imu-Analytics/pakages/pdf_s/{file_name}'
        generation_status[task_id] = 'completed'
        return jsonify({'task_id': task_id, 'file_path': pdf_file_path})

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    status = generation_status.get(task_id, 'not_found')
    return jsonify({'status': status})

@app.route('/download/<path:pdf_file_path>', methods=['GET'])
def download_file(pdf_file_path):
    return send_file(pdf_file_path, as_attachment=True)


def process_data(df, option,file_name):
    if option=='stop_time':
        obj=stopping(df)
        img,stop_time=obj.mark_stops()
        obj1=PDF(img,stop_time)
        pdf_path1=obj1.make_pdf()
        return pdf_path1

    elif option=='leg_overshoot':
        obj2=leg_overshooting(df)
        img,over_time,Total_Time,tap_point=obj2.mark_overshoot()
        obj3=PDF_leg(img,over_time,Total_Time,tap_point,file_name)
        pdf_path2=obj3.make_pdf_over()
        return pdf_path2

    elif option=='dir_overshoot':
        obj4=dir_overshooting(df)
        img,over_time,Total_Time,tap_point=obj4.mark_dir_overshoot()
        obj3=PDF_leg(img,over_time,Total_Time,tap_point,file_name)
        pdf_path2=obj3.make_pdf_over()
        return pdf_path2

def extract_between_file(input_string):
    import re
    # Use regex to find the content between the first pair of quotes
    match = re.search(r"'([^']*)'", input_string)
    print(match)
    if match:
        return match.group(1)
    else:
        return None

# if __name__ == '__main__':
#     app.run(debug=True)
