# avscan-webshell
## 什么是 avscan-webshell
Anti-Virus webShell 是一个pythoon3 版本的webshell查杀工具, 是一个通过pyinotify检测web目录文件变动，通过百度的WEBDIR+ https://scanner.baidu.com/ API 上传被改动的文件，发现病毒进行直接删除的工具

## avscan-webshell 安装
+ 在 /var 下创建 avscan目录，下载 avscan.py 至 /var/avscan 目录下

```shell
mkdir /var/avscan && curl https://raw.githubusercontent.com/hillghost86/avsacn-webshell/master/scan.py -o /var/avscan/scan.py
```


+ 脚本需要python3 以及 pyinotify模块

```shell
yum install python3 -y 
pip3 install pyinotify
```

+ 关于 scan.py的修改  
    + 修改scan.py文件内的 WATCH_PATH = '/www/wwwroot/' 为你的web目录
    + 此代码内有部分关于index.php 被修改的代码，不需要此功能需自行修改 check_file 函数
+ 下载service文件到/etc/systemd/system 添加为服务
+ 添加权限644给avscan.servicn
+ 启动服务，添加自启动

```shell
curl https://raw.githubusercontent.com/hillghost86/avsacn-webshell/master/avscan.service -o /etc/systemd/system/avscan.service
chmod 644 /etc/systemd/system/avscan.service
systemctl start avscan && systemctl enable avscan
```

## avscan 的由来
+ 一个朋友说最近他的网站总是被挂马，而且网站源码是别人写的，代码写的并不是太好，首页总是被修改.看了下代码写的也不太敢恭维，网站代码我也懒得去找入侵漏洞，就写了这个程序。
+ 通过 pyinotify 模块监控web目录，发现被修改过的php文件，使用https://scanner.baidu.com 的API上传所有被修改过的文件，发现被修改过文件是webshell，则删除此文件。
+ 由于index.php总是被修改，代码中增加了自动覆盖index.php的代码，通过index.php.tar.gz去覆盖index.php。
+ 网站代码不允许上传php文件，黑客利用上传漏洞上传txt文件，然后重命名为php文件，也是临时想到了发现新修改的txt文件直接删除的方法去限制txt文件上传。
+ 第一次写python，代码写的比较简陋

