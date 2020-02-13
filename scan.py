#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import pyinotify
import json  # 引用json模块
import time
import hashlib 



WATCH_PATH = '/www/wwwroot/'  # 监控目录 web目录
WATCH_FILES = ('.php','.phtml','.inc','.php3','.php4','.php5','.war','.jsp','.jspx','.asp','.aspx','.cer','.cdx','.asa','.ashx','.asmx','.cfm','.rar','.zip','.tar','.xz','.tbz','.tgz','.tbz2','.bz2','.gz')	#检查文件
INDEX_FILES = "/www/wwwroot/http/"	#此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行
index_md5 = "f5932a7f8cd0ec4ff62c8f18be5cb5f3" #此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行


if not WATCH_PATH:
	print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "The WATCH_PATH setting MUST be set.")
	sys.exit()
else:
	if os.path.exists(WATCH_PATH):
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + 'Found watch path: path=%s.' % (WATCH_PATH))
	else:
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + 'The watch path NOT exists, watching stop now: path=%s.' %
			  (WATCH_PATH))
		sys.exit()


# 事件回调函数
class OnIOHandler(pyinotify.ProcessEvent):
	# 重写文件写入完成函数
	def process_IN_CLOSE_WRITE(self, event):
		# logging.info("create file: %s " % os.path.join(event.path, event.name))
		# 处理成小图片，然后发送给grpc服务器或者发给kafka
		file_path = os.path.join(event.path, event.name)
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + '文件完成写入', file_path)
		check_file(file_path)	# 检查是否进行查毒

	# 重写文件删除函数

	def process_IN_DELETE(self, event):
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件删除: %s " % os.path.join(event.path, event.name))
	# 重写文件改变函数

	def process_IN_MODIFY(self, event):
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件改变: %s " % os.path.join(event.path, event.name))
	# 重写文件创建函数

	def process_IN_CREATE(self, event):
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件创建: %s " % os.path.join(event.path, event.name))
	# 重写移动创建函数

	def process_IN_MOVED_TO(self, event):
		file_path = os.path.join(event.path, event.name)
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件移动至:" , file_path)
		check_file(file_path)	# 检查是否进行查毒

	def process_IN_MOVED_FROM(self, event):
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件被移动: %s " % os.path.join(event.path, event.name))
	

def auto_compile(path='.'):
	wm = pyinotify.WatchManager()
	# mask = pyinotify.EventsCodes.ALL_FLAGS.get('IN_CREATE', 0)
	mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_TO  | pyinotify.IN_MOVED_FROM   # 只监控文件完成写入 重命名
	# mask = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']               # 监控内容，只监听文件被完成写入
	#mask = pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE | pyinotify.IN_MODIFY |pyinotify.IN_MOVED_TO  | pyinotify.IN_MOVED_FROM  #监控所有状态
	notifier = pyinotify.ThreadedNotifier(wm, OnIOHandler())  # 回调函数
	notifier.start()
	fs = wm.add_watch(path, mask, rec=True, auto_add=True)
	print(time.strftime('%Y-%m-%d %H:%M:%S  ') + 'Start monitoring and scan Anti-Virus  %s' % path)
	while True:
		try:
			notifier.process_events()
			if notifier.check_events():
				notifier.read_events()
		except KeyboardInterrupt:
			notifier.stop()
			break

#检查文件是否需要上传杀查毒
def check_file(self):
	if self == INDEX_FILES + "index.php" : #此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行
		if file_md5(INDEX_FILES + "index.php") != index_md5 : #此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行
			os.popen("tar -xvf " + INDEX_FILES + "index.php.tar.gz" + " -C " + INDEX_FILES).readlines() #此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行
			print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件" + self + "主页文件被修改,已还原!") #此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行
		#else: 
		return #此处为了防止web目录下的index.php被修改而设置，不需要此功能可注释掉此行
	if self.endswith(WATCH_FILES) :
		if os.path.getsize(self) < 49.99*1024*1024 : 
			scan_file(self)
		else:
			print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件" + self + "大于50M,最大支持50M" )
	else : 
		if self.endswith('.txt') :   #此处为禁止上传txt文件，不用此功能，请注释掉
			os.remove(self)  #此处为禁止上传txt文件，不用此功能，请注释掉
			print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件" + self + "不允许创建txt文件,已删除" ) #此处为禁止上传txt文件，不用此功能，请注释掉
		else:			
			print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件" + self + "无需检测!" )


#计算文件的md5
def file_md5(file_path):
    with open(file_path, 'rb') as fp:
        data = fp.read()
    file_md5= hashlib.md5(data).hexdigest()
    return file_md5   



# 扫描文件
def scan_file(file_path):
	tmpres = os.popen(
		'curl https://scanner.baidu.com/enqueue -F archive=@'+file_path).readlines() # 返回一个list
	scan_url = json.loads(tmpres[0])["url"]  # 读取字典url字段
	time.sleep(3)  # 等待扫描结果
	sf = curl_scan(scan_url)  # 检查查杀结果,返回字典类型
	i = 0
	while sf['status'] != "done":
		sf = curl_scan(scan_url)  # 检查查杀结果,返回字典类型
		time.sleep(3)
		i += 1  # 最大循环10次
		if i == 10:
			break  # 防止死循环,最大等待10个循环就退出
	if sf['data'][0]['descr'] != None or sf['detected'] != 0:
		os.remove(file_path)
		print(time.strftime('%Y-%m-%d %H:%M:%S  ') + "文件"  + file_path + "报毒" + sf['data'][0]['descr'] + ", 已删除!")
	else:
		print(time.strftime('%Y-%m-%d %H:%M:%S  ')  + "文件" + file_path + "安全")

# 查询扫描结果
def curl_scan(url):
	scan = os.popen('curl '+ url).readlines()  # crul结果文件返回json
	list_scan = json.loads(scan[0])  # json转为list
	doct_scan = list_scan[0]  # list转为doct
	return doct_scan


if __name__ == "__main__":
	auto_compile(WATCH_PATH)
	print('monitor close')
