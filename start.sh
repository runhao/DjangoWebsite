#!/bin/bash

# 1. 启用nginx代理
nginx -c /etc/nginx/nginx.conf

# 2. 构建静态文件夹
python manage.py collectstatic --noinput&&

# 3. 根据数据库迁移文件来修改数据库
python /var/www/html/my_website/manage.py migrate&&

# 4. 用 uwsgi启动 django 服务, 不再使用python manage.py runserver
uwsgi --ini /var/www/html/my_website/uwsgi.ini

# 5. 启用Celery beat Worker
celery -A my_website beat --loglevel=INFO&
celery -A my_website worker --loglevel=INFO --logfile=worker.log

# 防止退出
#tail -f /dev/null
