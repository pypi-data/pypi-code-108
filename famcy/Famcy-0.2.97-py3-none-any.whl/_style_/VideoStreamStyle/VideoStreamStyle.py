import Famcy
from flask import request, Response
import time

class VideoCamera(object):
	def __init__(self, rtsp_address, timeout=15, delay=0.5):
		# 通過opencv獲取實時視頻流
		import cv2
		self.cv_module = cv2
		self.video = self.cv_module.VideoCapture(rtsp_address) 
		self.start_time = time.time()
		self.stop_time  = self.start_time + int(timeout)
		self.is_decoded = False
		self.timeout = int(timeout)
		self.delay = delay
	
	def __del__(self):
		self.video.release()

	@classmethod
	def create_camera_response(cls, rtsp_address, timeout, delay):
		return cls.gen(cls(rtsp_address, timeout, delay), timeout, delay)

	@classmethod
	def gen(cls, camera, timeout, delay):
		camera.start_time = time.time()
		camera.stop_time = camera.start_time + int(timeout)

		while True:
			time.sleep(delay)
			frame, is_decoded = camera.get_frame()
			# 使用generator函式輸出視頻流， 每次請求輸出的content型別是image/jpeg
			if is_decoded:
				break
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
	
	def get_frame(self):
		success, image = self.video.read()
		# 因為opencv讀取的圖片并非jpeg格式，因此要用motion JPEG模式需要先將圖片轉碼成jpg格式圖片
		ret, jpeg = self.cv_module.imencode('.jpg', image)

		is_decoded = (time.time() >= self.stop_time)

		return jpeg.tobytes(), (self.is_decoded or is_decoded)

class VideoStreamStyle(Famcy.FamcyStyle):
	def __init__(self, path, delay=0.5):
		self.path = path
		self.video_camera = VideoCamera
		self.is_decoded = False
		self.delay = delay
		super(VideoStreamStyle, self).__init__()

	def render(self, _script, _html, background_flag=False, **kwargs):
		address = request.args.get('address')
		timeout = request.args.get('timeout')
		return Response(self.video_camera.create_camera_response(address, timeout, self.delay), mimetype='multipart/x-mixed-replace; boundary=frame')

