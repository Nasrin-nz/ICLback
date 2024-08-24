from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connections
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Questionnaire, Answer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Questionnaire, Answer, Question, Option
from django.contrib.auth.models import User  # Import the User model


@method_decorator(csrf_exempt, name='dispatch')  # CSRF exemption added
class GetRandomChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with connections['sql_server_db'].cursor() as cursor:
            # Corrected SQL syntax for SQL Server
            cursor.execute("SELECT TOP 1 chat_id FROM dbo.chats ORDER BY NEWID()")
            chat_id_record = cursor.fetchone()

            if chat_id_record:
                chat_id = chat_id_record[0]

                # Fetch all messages for the selected chat_id
                cursor.execute("SELECT id, chat_id, name, time, cc_date, text FROM dbo.chats WHERE chat_id = %s ORDER BY id ASC", [chat_id])
                chat_messages = cursor.fetchall()

                data = [
                    {
                        'id': msg[0],
                        'chat_id': msg[1],
                        'name': msg[2],
                        'time': msg[3],
                        'cc_date': msg[4],
                        'text': msg[5],
                    } for msg in chat_messages
                ]
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No chat available"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class StoreResponseView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            chat_id = data.get('conversation_id')
            answers = data.get('answers', [])
            volunteer = User.objects.get(id=request.user.id)
            # Step 1: Create a new entry in the questionnaire table using the 'sql_server_db' database
            questionnaire = Questionnaire.objects.using('sql_server_db').create(
                volunteer_id=volunteer.id,
                chat_id=chat_id,
                time=timezone.now(),  # Automatically capture the current timestamp
            )

            # Step 2: Process each answer entry and store the lists
            for answer in answers:
                question_id = answer.get('question_id')
                answer_ids = answer.get('answer_ids', [])
                message_ids = answer.get('message_ids', [])

                question = Question.objects.using('sql_server_db').get(id=question_id)  # Fetch the Question instance

                # Ensure every answer_id is associated with every message_id
                for answer_id in answer_ids:
                    option = Option.objects.using('sql_server_db').get(id=answer_id)  # Fetch the Option instance
                    for message_id in message_ids:
                        Answer.objects.using('sql_server_db').create(
                            questionnaire=questionnaire,
                            question=question,
                            answer=option,
                            chat_id=message_id,  # Store each message_id
                        )

            # Return a success response with the ID of the created questionnaire
            return JsonResponse({'status': 'success', 'questionnaire_id': questionnaire.id})

        except Exception as e:
            # Handle errors with basic error messages
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
