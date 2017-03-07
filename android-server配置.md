第一次用github，写点之前android server 端配置遇到的一些问题

# Android server 端配置问题汇总

# Flask+Gunicorn+Supervisor+Nginx

## 用 AWS 的 ubuntu 虚拟机作服务器 具体步骤见

http://iems5722.albertauyeung.com/files/references/aws_tutorial.pdf

### SSH 连接

用console新建aws_connect.sh文件，将下面的ssh命令输入

```
ssh -i "leoymr-key-pair.pem" ubuntu@ec2-13-113-129-249.ap-northeast-1.compute.amazonaws.com
```

```
chmod +x aws_connect.sh
```

接着cd直接进入存放该文件的文件夹，可以直接连接aws

```
./aws_coonect.sh
```

flask编写的python文件为getAPI.py，MyDatabase.py文件为连接MySQL数据库的代码

将写好的flask的python文件上传至ubuntu下新建的文件夹中。

可以用以下的命令直接运行写好的api，并从浏览器端查看

（ 要把aws上的security改成all traffic，代码里host设为0.0.0.0，为了让别的ip地址可以访问该端口 ）

```
$ python getAPI.py
```

### Supervisor 的配置

安装nginx，gunicorn，supervisor

生成默认配置文件

```
echo_supervisord_conf > supervisord.conf
```

创建遇到permission denied

```
sudo su - root -c "echo_supervisord_conf > /etc/supervisord.conf"
```

有两种方法加载新的配置：

我的配置文件

```
[program:iems5722]
command = gunicorn getAPI:app -b 0.0.0.0:8000 
directory = /home/ubuntu/appFlask
user = ubuntu
autostart = true
autorestart = true
stdout_logfile = /home/ubuntu/appFlask/app.log 
redirect_stderr = true
```

1、直接在supervisord.conf最后加上上述配置信息

```
sudo vim /etc/supervisord.conf
```

2、在 `/etc/supervisor/conf.d` 路径下面创建 `app.conf` 文件包含上述配置信息，因为一旦管理的进程过多，就很麻烦。

所以一般都会 新建一个目录来专门放置进程的配置文件，然后通过 include 的方式来获取这些配置信息

接着用配置好的.conf文件重新启动supervisor，并加载配置文件

```
$ supervisord -c /etc/supervisord.conf 	# 启动supervisor
$ superviosrctl reload      # 重新加载配置文件
$ superviosrctl update
```

如果配置正确将会看到

```
$ sudo supervisorctl
Iems5722 	RUNNING 	pid 24000, uptime 0:00:20 
supervisor>
```

几个常用的supervisor命令：

```
$ superviosrctl start xxx
$ superviosrctl stop xxx
$ superviosrctl status xxx
$ superviosrctl help        # 查看更多命令
```

`supervisord` 似乎默认是启动的，可以 `ps -aux | grep supervisord` 检测一下。

## Nginx 的配置

配置文件在 `/etc/nginx/sites-available/` 下面，配置完了之后软链接一份到 `/etc/nginx/sites-enabled/ghost.conf` 下面。记得把默认的 `default.conf` 删掉以免冲突。

我的配置文件：

```
server {
    listen 80;
    listen [::]:80;

	root /home/ubuntu/appFlask;
	index index.php index.html index.htm;

	server_name 0.0.0.0;
	location /api/asgn3/ {
		proxy_pass http://0.0.0.0:8000;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header Host $http_host; 
		proxy_http_version 1.1; 
		proxy_redirect off; 
		proxy_buffering off;
	} 
}
```

做软链接：

```
$ sudo ln -s /etc/nginx/sites-available/iems5722.conf /etc/nginx/sites-enabled/iems5722.conf
```

接着重启nginx服务：

1. `$ sudo service nginx restart`
2. `$ sudo /etc/init.d/nginx restart`

若发现api显示404 not found，可能是配置出错，或者端口已被占用，用下面的命令查看并kill掉占用的进程

```
sudo netstat -nlp | grep :80
sudo kill xxxx
```

参考：

- supervisor 的配置教程 [Basic nginx config](http://liuzxc.github.io/blog/supervisor/)
- [Deploying Gunicorn](http://docs.gunicorn.org/en/19.3/deploy.html#nginx-configuration)，比较复杂的 Gunicorn 文档中的 Nginx 的配置方法
- 使用 `nginx -t` 来检测配置文件是否正确：[nginx configtest vs nginx -t - DEVGET.NET](http://devget.net/nginxapache/nginx-configtest-vs-nginx-t/)

