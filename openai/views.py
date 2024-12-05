from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from openai.models import OpenAiKey


class ApiKeyView(APIView):

    @staticmethod
    def post(request):
        record = OpenAiKey.objects.filter(active=True)
        if record:
            return JsonResponse({
                'code': 200,
                'data': {
                    'success': True,
                    'code': record[0].code,
                },
                'msg': '测试成功'
            })
        return JsonResponse({
                'code': 202,
                'data': {
                    'success': False,
                },
                'msg': 'KEY值已消耗完毕，请联系管理员补充'
            })
