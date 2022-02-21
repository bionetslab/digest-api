import io
import os
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.encoding import smart_str
from django.http import StreamingHttpResponse

from digest_backend import preparation

import digest_backend.digest_executor as executor
from digest_backend import digest_files
from wsgiref.util import FileWrapper


@api_view(['POST'])
def set(request) -> Response:
    data = request.data
    preparation.prepare_set(data)
    result = executor.run_set(data)
    return Response(result)


@api_view(['POST'])
def cluster(request) -> Response:
    data = request.data
    preparation.prepare_cluster(data)
    result = executor.run_cluster(data)
    return Response(result)


@api_view(['POST'])
def set_set(request) -> Response:
    data = request.data
    preparation.prepare_set_set(data)
    result = executor.run_set_set(data)
    return Response(result)


@api_view(['POST'])
def id_set(request) -> Response:
    data = request.data
    preparation.prepare_id_set(data)
    result = executor.run_id_set(data)
    return Response(result)


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
        response = StreamingHttpResponse(FileWrapper(io.BytesIO(file)))
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=' + smart_str(file_name)
        return response
    raise Http404

def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
