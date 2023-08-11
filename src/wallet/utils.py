from rest_framework.response import Response


def jsend_response(code, data, status):
    response_data = {
        "data": data,
        "status": status
    }
    return Response(data=response_data, status=code)
