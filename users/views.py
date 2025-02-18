import json
import random
import requests
from users.models import User
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .tasks import send_verification_email as send_verification_email_task


class UserNameView(APIView):
    @staticmethod
    def post(request):
        name = ''
        message = '获取成功'
        data = json.loads(request.body.decode('utf-8'))
        user_id = data.get("user_id", '')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                name = user.name
            except User.DoesNotExist:
                message = '用户不存在'
        return JsonResponse({
            'code': 200,
            'data': {
                'success': True,
                'name': name,
            },
            'msg': message
        })


class RegisterView(APIView):
    authentication_classes = []  # 禁用身份验证
    permission_classes = []  # 禁用权限检查

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        return self.user_register(
            name=data.get('name', ''),
            password=data.get('password', ''),
            email=data.get('email', ''),
            mobile=data.get('phone', ''),
            verification_code=data.get('verificationCode', '')
        )

    def user_register(self, name, password, email, mobile, verification_code):
        if not (password and email and mobile and verification_code):
            return self.json_response(201, False, '请填写完整信息！')

        # 验证邮箱验证码
        if not self.verify_email_code(email, verification_code):
            return self.json_response(201, False, '邮箱验证码错误')

        if User.objects.filter(Q(email=email) | Q(mobile=mobile), is_active=True).exists():
            return self.json_response(201, False, '用户信息重复')

        user = User.objects.create_user(
            name=name,
            username=email,
            password=password,
            email=email,
            mobile=mobile,
            is_staff=True,
            is_active=True,
            is_superuser=False
        )

        return self.json_response(200, True, '用户注册成功', {'name': user.name})

    @staticmethod
    def verify_email_code(email, code):
        # 从缓存中获取验证码
        cached_code = cache.get(email)
        return cached_code == code

    @staticmethod
    def json_response(code, success, msg, extra_data=None):
        response_data = {
            'code': code,
            'data': {'success': success}
        }
        if extra_data:
            response_data['data'].update(extra_data)
        response_data['msg'] = msg
        return JsonResponse(response_data)


class LoginView(APIView):
    authentication_classes = []  # 禁用身份验证
    permission_classes = []  # 禁用权限检查

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        return self.user_login(request, name=data.get('name', ''), password=data.get('password', ''))

    def user_login(self, request, name, password):
        try:
            user = User.objects.get(Q(email=name) | Q(mobile=name), is_active=True)
        except User.DoesNotExist:
            return self.json_response(201, False, '用户不存在')

        user = authenticate(username=user.username, password=password)
        if user is None:
            return self.json_response(201, False, '用户认证失败')

        url = f"{request.scheme}://{request.get_host()}/api/token/"
        response = requests.post(url, data={"username": user.username, "password": password})
        data = response.json()

        user.last_login = timezone.now()
        user.save()

        return self.json_response(200, True, '登录成功', {'access': data["access"], 'refresh': data["refresh"]})

    @staticmethod
    def json_response(code, success, msg, extra_data=None):
        response_data = {
            'code': code,
            'data': {'success': success}
        }
        if extra_data:
            response_data['data'].update(extra_data)
        response_data['msg'] = msg
        return JsonResponse(response_data)


class SendVerificationCodeView(APIView):
    authentication_classes = []  # 禁用身份验证
    permission_classes = []  # 禁用权限检查

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '')
        action = data.get('action', '')
        if not email:
            return self.json_response(201, False, '请填写邮箱地址！')

        # 生成验证码
        verification_code = self.generate_verification_code()

        # 将验证码存储到缓存中，设置过期时间为5分钟
        cache.set(email, verification_code, timeout=300)

        # 发送验证码到邮箱
        self.send_verification_email(email, verification_code, action)

        return self.json_response(200, True, '验证码发送成功')

    @staticmethod
    def generate_verification_code():
        # 生成6位随机验证码
        return ''.join(random.choices('0123456789', k=6))

    @staticmethod
    def send_verification_email(email, code, action):
        send_verification_email_task.delay(email, code, action)

    @staticmethod
    def json_response(code, success, msg, extra_data=None):
        response_data = {
            'code': code,
            'data': {'success': success}
        }
        if extra_data:
            response_data['data'].update(extra_data)
        response_data['msg'] = msg
        return JsonResponse(response_data)


class ResetPasswordView(APIView):
    authentication_classes = []  # 禁用身份验证
    permission_classes = []  # 禁用权限检查

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '')
        verification_code = data.get('verification_code', '')
        new_password = data.get('new_password', '')

        if not (email and verification_code and new_password):
            return self.json_response(201, False, '请填写完整信息！')

        # 验证邮箱验证码
        if not self.verify_email_code(email, verification_code):
            return self.json_response(201, False, '邮箱验证码错误')

        # 查找用户
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return self.json_response(201, False, '用户不存在')

        # 更新密码
        user.password = make_password(new_password)
        user.save()

        return self.json_response(200, True, '密码重置成功')

    @staticmethod
    def verify_email_code(email, code):
        # 从缓存中获取验证码
        cached_code = cache.get(email)
        return cached_code == code

    @staticmethod
    def json_response(code, success, msg, extra_data=None):
        response_data = {
            'code': code,
            'data': {'success': success}
        }
        if extra_data:
            response_data['data'].update(extra_data)
        response_data['msg'] = msg
        return JsonResponse(response_data)
