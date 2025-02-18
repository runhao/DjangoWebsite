# 建立 python3.12 环境
FROM registry.cn-chengdu.aliyuncs.com/runhaofu/python_docker_base

LABEL MAINTAINER=1549971272@qq.com

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1

# 设置pip源为国内源
COPY pip.conf /root/.pip/pip.conf
COPY nginx.conf /etc/nginx/nginx.conf

# 在容器内/var/www/html/下创建 文件夹
RUN mkdir -p /var/www/html/my_website

# 设置容器内工作目录
WORKDIR /var/www/html/my_website

# 将当前目录文件加入到容器工作目录中（. 表示当前宿主机目录）
ADD . /var/www/html/my_website

# 利用 pip 安装依赖
RUN pip install -r requirements.txt

# Windows环境下编写的start.sh每行命令结尾有多余的\r字符，需移除。
RUN sed -i 's/\r//' ./start.sh

# 设置start.sh文件可执行权限
RUN chmod +x ./start.sh

# 数据迁移，并使用uwsgi启动服务
ENTRYPOINT /bin/bash ./start.sh
