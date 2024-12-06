import json
import requests
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from users.models import User


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = parse_json_request(request)
        return user_register(
            username=data.get('username', ''),
            password=data.get('password', ''),
            email=data.get('email', ''),
            mobile=data.get('phone', '')
        )
    return forbidden_response()


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = parse_json_request(request)
        return user_login(request, name=data.get('name', ''), password=data.get('password', ''))
    return forbidden_response()


def parse_json_request(request):
    return json.loads(request.body.decode('utf-8'))


def forbidden_response():
    return JsonResponse({
        'code': 403,
        'data': {'success': False},
        'msg': '被禁止的请求'
    })


def user_register(username, password, email, mobile):
    if not (password and email and mobile):
        return json_response(201, False, '请填写完整信息！')

    if User.objects.filter(Q(email=email) | Q(mobile=mobile)).exists():
        return json_response(200, False, '用户信息重复')

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        mobile=mobile,
        is_staff=True,
        is_active=True,
        is_superuser=False
    )

    return json_response(200, True, '用户注册成功', {'username': user.username})


def user_login(request, name, password):
    try:
        user = User.objects.get(Q(email=name) | Q(mobile=name))
    except User.DoesNotExist:
        return json_response(200, False, '用户不存在')

    user = authenticate(username=user.username, password=password)
    if user is None:
        return json_response(403, False, '用户认证失败')

    if not user.is_active:
        return json_response(200, False, '用户未激活')

    url = f"{request.scheme}://{request.get_host()}/api/token/"
    response = requests.post(url, data={"username": user.username, "password": password})
    data = response.json()

    user.last_login = timezone.now()
    user.save()

    return json_response(200, True, '登录成功', {'access': data["access"], 'refresh': data["refresh"]})


def json_response(code, success, msg, extra_data=None):
    response_data = {
        'code': code,
        'data': {'success': success}
    }
    if extra_data:
        response_data['data'].update(extra_data)
    response_data['msg'] = msg
    return JsonResponse(response_data)
