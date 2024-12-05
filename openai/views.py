from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from openai.models import OpenAiKey


class ApiKeyView(APIView):

    @staticmethod
    def post(request):
        records = OpenAiKey.objects.filter(active=True)
        if records:
            return JsonResponse({
                'code': 200,
                'data': {
                    'success': True,
                    'code': records[0].code,
                },
                'msg': ''
            })
        return JsonResponse({
                'code': 202,
                'data': {
                    'success': False,
                },
                'msg': 'KEY值已消耗完毕，请联系管理员补充'
            })
