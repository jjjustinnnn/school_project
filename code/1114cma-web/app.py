from flask import Flask, render_template, send_from_directory, jsonify, Response
import subprocess
import os
import threading
import logging

# 静态文件目录设置
STATIC_DIR = '/home/abc/Desktop/web2.0/static'

app = Flask(__name__, static_folder=STATIC_DIR)

# 全局变量，用来控制视频流的状态
is_camera_active = False

# 取得视频画面的函数
def get_camera_feed():
    global is_camera_active
    import cv2

    cap = cv2.VideoCapture(0)  # 打开相机（0是第一个相机）

    while is_camera_active:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 将画面编码成JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # 将图像流传递给客户端
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# Flask路由，提供视频流画面
@app.route('/video_feed')
def video_feed():
    return Response(get_camera_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 启动视频流的函数
def activate_camera():
    global is_camera_active
    is_camera_active = True
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)).start()

# 验证成功后调用此函数
def on_auth_success():
    print("验证成功，启用视频镜头")
    IP1 = get_ip_address()
    print(f'请连接到: http://{IP1}:5000/video_feed')
    activate_camera()

# 获取当前机器的IP地址
def get_ip_address():
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # 连接 Google Public DNS
        ip_address = sock.getsockname()[0]
    finally:
        sock.close()
    return ip_address

# Flask路由，提供二维码图片
@app.route('/static/uploads/<filename>')
def send_image(filename):
    return send_from_directory(os.path.join(STATIC_DIR, 'uploads'), filename)

# 首页路由，包含按钮
@app.route('/')
def index():
    return render_template('index.html')

# 执行 Python 脚本并检查是否成功的路由
@app.route('/run-python', methods=['POST'])
def run_python_script():
    try:
        # 执行 test-eepromuser2.py 脚本
        result = subprocess.run(['python', 'test-eepromuser2.py'], capture_output=True, text=True, check=True)
        print(f"test-eepromuser2.py output: {result.stdout}")
        
        # 如果脚本执行成功，返回成功的响应
        return jsonify(success=True)
    except subprocess.CalledProcessError as e:
        # 如果脚本执行失败，返回错误信息
        print(f"test-eepromuser2.py error: {e.stderr}")
        return jsonify(success=False, error=f"执行失败: {e.stderr}")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(success=False, error=f"发生了错误: {str(e)}")

# 运行 test-indexdecrypt-cam1016.py 脚本并返回结果
@app.route('/run-cam1016', methods=['POST'])
def run_cam1016_script():
    try:
        # 执行 test-indexdecrypt-cam1016.py 脚本并捕获输出
        result = subprocess.run(['python', 'test-indexdecrypt-cam1016.py'], capture_output=True, text=True, check=True)

        # 获取标准输出和标准错误
        output = result.stdout.strip()
        error_output = result.stderr.strip()

        print(f"test-indexdecrypt-cam1016.py output: {output}")
        print(f"test-indexdecrypt-cam1016.py error: {error_output}")

        if output.lower() == 'true':  # 如果输出为 'True'，验证成功
            return jsonify(success=True, condition="True")
        else:
            return jsonify(success=False, condition="False", error="验证失败，请重新验证。")
    
    except subprocess.CalledProcessError as e:
        # 如果脚本执行失败，捕获错误并返回
        print(f"test-indexdecrypt-cam1016.py 执行失败: {e.stderr}")
        return jsonify(success=False, error=f"执行失败: {e.stderr}")
    except Exception as e:
        # 捕获其他异常
        print(f"发生错误: {str(e)}")
        return jsonify(success=False, error=f"发生错误: {str(e)}")


# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True)
