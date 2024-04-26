from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from utils.enums import Enums
from utils.error import Error, APIError
from utils.util import response_data_formating
from accounts.permissions import IsAdminOrCRTSupervisor

from accounts.serializers import ErrorResponseSerializer
from accounts.models import CustomUser
from awards.models import AwardAssignment, AwardQuestionAnswer
from nominations.models import AwardNomination
from criteria.models import Criteria, CriteriaCategory
from evaluations.models import Evaluation

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SystemResetView(APIView):
    """
    API view to reset/delete (Only for CRT/Admin) data i.e Nomination, Criteria, Evaluation, Award Assignments, Answers
    """

    permission_classes = [IsAdminOrCRTSupervisor]

    @swagger_auto_schema(
        responses={
            204: openapi.Response("Successful Deletion"),
            403: openapi.Response("Forbidden")
        }
    )
    @transaction.atomic
    def delete(self, request):
        AwardNomination.objects.all().delete()
        Criteria.objects.all().delete()
        CriteriaCategory.objects.all().delete()
        Evaluation.objects.all().delete()
        AwardAssignment.objects.all().delete()
        AwardQuestionAnswer.objects.all().delete()

        return Response(response_data_formating(
            generalMessage='success',
            data=None),
            status=status.HTTP_204_NO_CONTENT
        )


class UserDataResetView(APIView):
    """
    API view for deleting evaluator/applicant related data by user id (Only for CRT/Admin)
    """

    permission_classes = [IsAdminOrCRTSupervisor]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='user_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='User Id'
            )
        ],
        responses={
            204: openapi.Response("Successful Deletion"),
            400: openapi.Response("Error response", ErrorResponseSerializer)
        }
    )
    @transaction.atomic
    def delete(self, request):
        user_id = request.query_params.get('user_id', None)
        if not user_id or not user_id.isdigit():
            raise APIError(Error.DEFAULT_ERROR, extra=[
                           'User id missing or incorrect'])
        try:
            user = CustomUser.objects.get(id=user_id)
        except:
            raise APIError(Error.DEFAULT_ERROR, extra=[
                           'User not found with given user id'])

        if user.user_type in [Enums.FILTERER.value, Enums.EVALUATOR.value, Enums.JUDGE.value]:
            AwardAssignment.objects.filter(evaluator=user).delete()
            Evaluation.objects.filter(evaluated_by=user).delete()
        elif user.user_type == Enums.APPLICANT.value:
            AwardNomination.objects.filter(user=user).delete()
            AwardQuestionAnswer.objects.filter(user_id=user).delete()

        return Response(response_data_formating(
            generalMessage='success',
            data=None),
            status=status.HTTP_204_NO_CONTENT
        )
