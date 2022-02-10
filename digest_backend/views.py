from rest_framework.decorators import api_view
from rest_framework.response import Response

import digest_backend.digest_executor as digest_executor
#from digest_backend.models import Example
#from digest_backend.serializers import ExampleSerializer
#
#
@api_view(['GET'])
def test(request) -> Response:
    digest_executor.single_validation()
    # if request.query_params.get('nr'):
        # example = Example.objects.get(count=request.query_params.get("nr"))
        # resp = {'examples': ExampleSerializer().to_representation(example)}
    # else:
        # examples = Example.objects.all()
        # resp = {'examples': ExampleSerializer(many=True).to_representation(examples)}
    # return Response(resp)
