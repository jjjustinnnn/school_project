import time
import os
from flask import Flask, render_template, send_from_directory, redirect, jsonify, Response
import subprocess
import threading
import json
import webbrowser

# Define the directory paths
STATIC_DIR = '/home/abc/Desktop/web2.0/static'
UPLOADS_DIR = os.path.join(STATIC_DIR, 'uploads')

app = Flask(__name__, static_folder=STATIC_DIR)

# Global variable to track if the camera is active
is_camera_active = False

def start_cam_script():
    try:
        # Get the absolute path to cam.py
        cam_script_path = os.path.abspath('cam.py')
        print(f"Attempting to run cam.py, Path: {cam_script_path}")
        
        # Use subprocess.Popen to run cam.py in the background
        process = subprocess.Popen(['python', cam_script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Capture and print stdout and stderr for debugging
        stdout, stderr = process.communicate()
        print(f"cam.py execution output: {stdout.decode()}")
        if stderr:
            print(f"cam.py error output: {stderr.decode()}")

        return True
    except Exception as e:
        print(f"Error running cam.py: {str(e)}")
        return False

# Ensure the QR code file exists before returning it
def is_qrcode_ready():
    return os.path.exists(os.path.join(UPLOADS_DIR, 'qrcode.png'))

# Run the test-eepromuser2.py script and wait until the file is saved
@app.route('/run-python', methods=['POST'])
def run_python_script():
    try:
        # Run the Python script
        result = subprocess.run(['python', 'test-eepromuser2.py'], capture_output=True, text=True, check=True)
        print(f"test-eepromuser2.py output: {result.stdout}")

        # Wait for the QR code file to be created
        while not is_qrcode_ready():
            time.sleep(1)  # Check every second until the file exists

        # Return success response after the QR code file is ready
        return jsonify(success=True)

    except subprocess.CalledProcessError as e:
        print(f"test-eepromuser2.py error: {e.stderr}")
        return jsonify(success=False, error=f"执行失败: {e.stderr}")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(success=False, error=f"发生了错误: {str(e)}")

# Serve the QR code image
@app.route('/static/uploads/<filename>')
def send_image(filename):
    return send_from_directory(UPLOADS_DIR, filename)

# Obtain video feed
def get_camera_feed():
    global is_camera_active
    import cv2

    cap = cv2.VideoCapture(0)  # Open camera (0 is the first camera)

    while is_camera_active:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode the frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame to the client
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# Flask route to provide video feed
@app.route('/video_feed')
def video_feed():
    return Response(get_camera_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Activate the camera stream
def activate_camera():
    global is_camera_active
    is_camera_active = True
    # Start the Flask app in a separate thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)).start()

# Verify success after authentication
def on_auth_success():
    print("验证成功，启用视频镜头")
    IP1 = get_ip_address()
    print(f'请连接到: http://{IP1}:5001/video_feed')
    activate_camera()

# Get the current machine's IP address
def get_ip_address():
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # Connect to Google DNS
        ip_address = sock.getsockname()[0]
    finally:
        sock.close()
    return ip_address

# Run the test-indexdecrypt-cam1016.py script and return result

@app.route('/run-cam1016', methods=['POST'])
def run_cam1016_script():
    try:
        # Run the test-indexdecrypt-cam1016.py script
        result = subprocess.run(['python', 'test-indexdecrypt-cam1016.py'], capture_output=True, text=True, check=True)
        
        output = result.stdout.strip()
        print(f"test-indexdecrypt-cam1016.py output: {output}")

        if output.lower() == "true":  # If output is 'true', authentication is successful
            print("Authentication successful, starting the camera")

            # Call the function to start cam.py
            if start_cam_script():
                return jsonify(success=True, condition="True")
            else:
                return jsonify(success=False, error="Failed to start camera.")
        
        elif output.lower() == "false":
            return jsonify(success=False, condition="False", error="Verification failed, please try again.")
        else:
            return jsonify(success=False, error="Unexpected output from test-indexdecrypt-cam1016.py")

    except subprocess.CalledProcessError as e:
        print(f"test-indexdecrypt-cam1016.py failed: {e.stderr}")
        return jsonify(success=False, error=f"Execution failed: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify(success=False, error=f"An error occurred: {str(e)}")
@app.route('/')
def index():
    return render_template('index.html')


def open_browser():
    time.sleep(2)  # 等待 Flask 服务器启动
    webbrowser.open_new('http://127.0.0.1:5000')
# Start the Flask app
if __name__ == '__main__':
    threading.Thread(target=open_browser).start()  # 在另一个线程中打开浏览器
    app.run(debug=False, use_reloader=False) 
 
