import base64
import mimetypes
import os
import json
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.encoding import smart_str
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper

from digest_backend import preparation
from django.views.decorators.cache import never_cache
import digest_backend.digest_executor as executor
from digest_backend import digest_files
from digest_backend.models import Task, Attachment
from digest_backend.task import start_task, refresh_from_redis, task_stats


def run(mode, data, params) -> Response:
    print(data)
    task = Task.objects.create(uid=data["uid"], mode=mode, parameters=data, request=params)
    start_task(task)
    task.save()
    print(task)
    return Response({'task': data["uid"]})


@api_view(['POST'])
def set(request) -> Response:
    data = request.data
    params = json.dumps(data)
    preparation.prepare_set(data)
    return run("set", data, params)


@api_view(['POST'])
def cluster(request) -> Response:
    data = request.data
    params = json.dumps(data)
    preparation.prepare_cluster(data)
    return run("cluster", data, params)


@api_view(['POST'])
def set_set(request) -> Response:
    data = request.data
    params = json.dumps(data)
    preparation.prepare_set_set(data)
    return run("set-set", data, params)


@api_view(['POST'])
def id_set(request) -> Response:
    data = request.data
    params = json.dumps(data)
    preparation.prepare_id_set(data)
    return run("id-set", data, params)


@never_cache
@api_view(['GET'])
def get_status(request) -> Response:
    uid = request.GET.get('task')
    task = Task.objects.get(uid=uid)
    if not task.done and not task.failed:
        refresh_from_redis(task)
        task.save()
    response = Response({
        'task': task.uid,
        'failed': task.failed,
        'done': task.done,
        'status': task.status,
        'stats': task_stats(task),
        'mode': task.mode,
        'type': json.loads(task.request)["type"],
        'input':json.loads(task.request)
    })
    return response


@api_view(['GET'])
def get_result_file_list(request) -> Response:
    uid = request.GET.get('task')
    files = list({'name':a.name, 'type':a.type} for a in Attachment.objects.filter(uid=uid))
    return (Response(files))

def get_result_file(request)->Response:
    name = request.GET.get('name')
    a = Attachment.objects.get(name=name)
    type=""
    if a.type == 'csv':
        type = 'text/csv'
    elif a.type =='png':
        type = 'image/png'
    response = HttpResponse(base64.b64decode(a.content), content_type=type)
    response['Content-Disposition'] =f'attachment; filename="{name}"'
    return response


@api_view(['GET'])
def get_result(request) -> Response:
    uid = request.GET.get('task')
    task = Task.objects.get(uid=uid)
    if not task.done and not task.failed:
        refresh_from_redis(task)
        task.save()
    return Response({'task': task.uid, 'result': json.loads(task.result), 'parameters': json.loads(task.request)})


@api_view(['GET'])
def get_files(request) -> Response:
    file_name = request.GET.get('name')
    measure = request.GET.get('measure')
    file = file_name
    if not file_name.endswith(".csv"):
        print("getting file " + measure + "/" + file_name)
        file = os.path.join(measure, file_name)
    else:
        print("getting file " + file_name)
    file = digest_files.getFile(file)
    if file is not None:
        response = StreamingHttpResponse(FileWrapper(open(file, 'rb'), 512), content_type=mimetypes.guess_type(file)[0])
        response['Content-Disposition'] = 'attachment; filename=' + smart_str(file_name)
        response['Content-Length'] = os.path.getsize(file)
        return response
    raise Http404
