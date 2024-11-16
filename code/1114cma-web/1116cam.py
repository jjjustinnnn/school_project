from flask import Flask, Response, redirect
import socket
import cv2
import multiprocessing
import webbrowser
import threading
import time
import sys

app = Flask(__name__)

# 控制摄像头状态
is_camera_active = False

# 获取摄像头视频流
def get_camera_feed():
    global is_camera_active
    cap = cv2.VideoCapture(0)  # 打开默认摄像头
    if not cap.isOpened():
        print("错误：无法打开摄像头。")
        sys.exit(1)
    
    while is_camera_active:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 将帧编码为 JPEG 格式
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # 返回视频流
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    cap.release()

# 提供视频流的路由
@app.route('/video_feed')
def video_feed():
    return Response(get_camera_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 根路由重定向到 /video_feed
@app.route('/')
def index():
    return redirect('/video_feed')

# 启动摄像头流
def activate_camera():
    global is_camera_active
    is_camera_active = True
    app.run(host='0.0.0.0', port=5002, debug=False, use_reloader=False)

# 打开浏览器
def open_browser():
    time.sleep(1)  # 等待 Flask 服务器启动
    webbrowser.open_new('http://127.0.0.1:5002')

# 获取本机 IP 地址
def get_ip_address():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # 连接 Google 公共 DNS
        ip_address = sock.getsockname()[0]
    finally:
        sock.close()
    return ip_address

# 认证成功后的处理
def on_auth_success():
    print("认证成功，正在启动摄像头。")
    IP1 = get_ip_address()
    print(f'请连接到： http://{IP1}:5002/video_feed')
    activate_camera()

# 主函数，认证成功后启动摄像头
def main():
    on_auth_success()

if __name__ == "__main__":
    # 使用线程分别启动 Flask 应用和浏览器
    threading.Thread(target=main).start()  # 在独立线程中启动认证和摄像头
    threading.Thread(target=open_browser).start()  # 在独立线程中启动浏览器
