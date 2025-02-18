from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from openai.models import OpenAiToken
from .tasks import refresh_token


def run_refresh_token(request):
    result = refresh_token.apply_async()
    return JsonResponse({
            'code': 200,
            'data': {
                'success': True,
                'value': result.task_id + ' : ' + result.status,
            },
            'msg': ''
        })


class AiTokenView(APIView):
    @staticmethod
    def post(request):
        records = OpenAiToken.objects.filter(active=True)
        if records:
            return JsonResponse({
                'code': 200,
                'data': {
                    'success': True,
                    'key': records[0].code,
                    'type': records[0].api_type,
                },
                'msg': ''
            })
        return JsonResponse({
                'code': 202,
                'data': {
                    'success': False,
                },
                'msg': 'TOKEN值已消耗完毕，请联系管理员补充'
            })
