from flask import Flask, Response, redirect
import socket
import cv2
import multiprocessing

app = Flask(__name__)

# Control camera state
is_camera_active = False

# Function to get camera feed
def get_camera_feed():
    global is_camera_active
    cap = cv2.VideoCapture(0)  # Open default camera
    
    while is_camera_active:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Return the video stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    cap.release()

# Route to provide video feed
@app.route('/video_feed')
def video_feed():
    return Response(get_camera_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Redirect root URL to /video_feed
@app.route('/')
def index():
    return redirect('/video_feed')

# Function to activate camera stream
def activate_camera():
    global is_camera_active
    is_camera_active = True
    process = multiprocessing.Process(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False))
    process.start()

# Function to get the IP address of the machine
def get_ip_address():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # Google Public DNS
        ip_address = sock.getsockname()[0]
    finally:
        sock.close()
    return ip_address

# Function to handle authentication success
def on_auth_success():
    print("Authentication successful, starting camera.")
    IP1 = get_ip_address()
    print(f'Please connect to: http://{IP1}:5001/video_feed')
    activate_camera()

# Main function to start the camera after authentication
def main():
    on_auth_success()

if __name__ == "__main__":
    main()
