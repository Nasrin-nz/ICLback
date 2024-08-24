

from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question = models.TextField()

    class Meta:
        db_table = 'questions'


class Option(models.Model):
    Answers = models.TextField()

    class Meta:
        db_table = 'options'


class Questionnaire(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_id = models.IntegerField()  # The ID of the conversation
    time = models.DateTimeField(auto_now_add=True)  # Automatically set the time when the record is created

    class Meta:
        db_table = 'questionnaire'  # Use the name of the table you created in SSMS

    def save(self, *args, **kwargs):
        # Ensure that saving uses the SQL Server database
        if not kwargs.get('using'):
            kwargs['using'] = 'sql_server_db'
        super(Questionnaire, self).save(*args, **kwargs)


class Answer(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
<<<<<<< HEAD
    question = models.TextField()
    answer = models.TextField()  # Stores the list of answer IDs as a comma-separated string
    msg = models.TextField()     # Stores the list of message IDs as a comma-separated string
=======
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_column='question_id')  # Foreign key to the Question model
    answer = models.ForeignKey(Option, on_delete=models.CASCADE, db_column='answer_id')  # Foreign key to the Option model
    chat_id = models.TextField()  # This remains as it stores the list of message IDs as a comma-separated string
>>>>>>> 8106b27

    class Meta:
        db_table = 'answers'  # Use the name of the table you created in SSMS

    def save(self, *args, **kwargs):
        # Ensure that saving uses the SQL Server database
        if not kwargs.get('using'):
            kwargs['using'] = 'sql_server_db'
        super(Answer, self).save(*args, **kwargs)


class Chats(models.Model):
    text = models.TextField()
    class Meta:
        db_table = 'chats'


class Option(models.Model):
    Answers = models.TextField()  # Only the 'Answers' column is defined
    class Meta:
        db_table = 'options'  # Specify the table name in your SQL Server database



class Questions(models.Model):
    question = models.TextField()

    class Meta:
        db_table = 'questions'
