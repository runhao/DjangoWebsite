import json
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from users.models import User


# Create your views here.

@csrf_exempt
def register(request, **kwargs):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # 获取参数
        username = data.get('username', '')
        password = data.get('password', '')
        email = data.get('email', '')
        mobile = data.get('phone', '')
        if not (password and email and mobile):
            return JsonResponse({
                'code': 201,
                'data': {'success': False},
                'msg': '请填写完整信息！'
            })
        # 用户已存在
        if User.objects.filter(Q(email=email) | Q(mobile=mobile)):
            return JsonResponse({
                'code': 200,
                'data': {'success': False},
                'msg': '用户信息重复'
            })
        # 用户不存在
        else:
            # 使用User内置方法创建用户
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                is_staff=1,
                is_active=1,
                is_superuser=0
            )

            return JsonResponse({
                'code': 200,
                'data': {'success': True, 'username': user.username},
                'msg': '用户注册成功'
            })

    else:
        return JsonResponse({
            'code': 403,
            'data': {'success': False},
            'msg': '被禁止的请求'
        })


@csrf_exempt
def login(request, **kwargs):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # 获取参数
        name = data.get('name', '')
        password = data.get('password', '')

        # 用户已存在
        user = User.objects.filter(Q(email=name) | Q(mobile=name))
        if user:
            # 使用内置方法验证
            username = list(user.values("username"))[0]["username"]
            user = authenticate(username=username, password=password)
            # 验证通过
            if user:
                # 用户已激活
                if user.is_active:
                    return JsonResponse({
                        'code': 200,
                        'data': {'success': True},
                        'msg': '登录成功'
                    })
                # 未激活
                else:
                    return JsonResponse({
                        'code': 200,
                        'data': {'success': False},
                        'msg': '用户未激活'
                    })

            # 验证失败
            else:
                return JsonResponse({
                    'code': 403,
                    'data': {'success': False},
                    'msg': '用户认证失败'
                })

        # 用户不存在
        else:
            return JsonResponse({
                'code': 200,
                'data': {'success': False},
                'msg': '用户不存在'
            })
    else:
        return JsonResponse({
            'code': 403,
            'data': {'success': False},
            'msg': '被禁止的请求'
        })
