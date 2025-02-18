import requests
from django.db.models import Q
from openai.models import OpenAiToken
from celery import shared_task


def get_login_info():
    url = "https://midjourncy.com/api/user/login"
    params = {"username": "runhao", "password": "aa631216"}

    # 发起请求
    response = requests.post(url, json=params)
    # 检查响应状态码
    if response.status_code == 200:
        # 成功获取响应
        data = response.json()
        if data["success"]:
            user_id = data["data"]["id"]
            cookies = response.headers["Set-Cookie"]
            return {"user_id": user_id, "cookies": cookies}
    raise ValueError("获取登录信息失败")


def get_token_info(login_info):
    url = "https://midjourncy.com/api/token/"
    params = {"p": 0}
    headers = {"cookie": login_info["cookies"], "new-api-user": str(login_info["user_id"])}

    # 发起请求
    response = requests.get(url, params=params, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        # 成功获取响应
        data = response.json()
        if data["success"]:
            return data["data"]
    raise ValueError("获取token信息失败")


@shared_task
def refresh_token():
    # 接口地址
    login_info = get_login_info()
    token_info = get_token_info(login_info)
    for value in token_info:
        # {'id': 748, 'user_id': 228, 'key': 'f7j8f090dbEgiVXcF7m6DZrA9HWozgtoYbiRCLEk7w7NVQ8z', 'status': 1, 'name': 'runhao的初始令牌', 'created_time': 1732871503, 'accessed_time': 1735288615, 'expired_time': -1, 'remain_quota': 5000000, 'unlimited_quota': False, 'model_limits_enabled': False, 'model_limits': '', 'ip_limits': '', 'used_quota': 4190150, 'rate_limit_enabled': False, 'rate_limit_interval': 1, 'rate_limit_count': 1, 'group': 'default', 'DeletedAt': None}
        token = OpenAiToken.objects.filter(Q(code="sk-" + value["key"])).first()
        if token:
            token.quota = value["remain_quota"] + value["used_quota"]
            token.used_quota = value["used_quota"]
            token.remain_quota = value["remain_quota"]
            token.save()
        else:
            OpenAiToken.objects.create(code="sk-" + value["key"],
                                       quota=value["remain_quota"] + value["used_quota"],
                                       used_quota=value["used_quota"],
                                       remain_quota=value["remain_quota"],
                                       api_type="chatgpt,midjourney")
    return len(token_info)
