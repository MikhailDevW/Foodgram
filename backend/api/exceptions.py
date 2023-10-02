from rest_framework.exceptions import APIException, status


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request - smth went wrong.'
    default_code = 'error'
