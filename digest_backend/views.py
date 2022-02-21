import os
from django.http import HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from digest_backend import preparation


import digest_backend.digest_executor as executor
from digest_backend import digest_files


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
def get_files(request)->Response:
    file_name = request.GET.get('name')
    measure = request.GET.get('measure')
    print("getting file "+measure+"/"+file_name)
    file = file_name
    if not file_name.endsWith(".csv"):
        file = os.path.join(measure,file_name)
    file = digest_files.getFile(file)
    if file is not None:
        with open(file,'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + file_name
            return response
    raise Http404