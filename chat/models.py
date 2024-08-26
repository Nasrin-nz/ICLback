from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    question = models.TextField(verbose_name="سوال")

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"


class Questionnaire(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="پرسشنامه")
    chat_id = models.IntegerField(verbose_name="ایدی چت")  # The ID of the conversation
    time = models.DateTimeField(auto_now_add=True, verbose_name="زمان")  # Automatically set the time when the record is created

    class Meta:
        verbose_name = "پرسش نامه"
        verbose_name_plural = "پرسش نامه ها"



class Answer(models.Model):
    questionnaire = models.ForeignKey("Questionnaire", on_delete=models.CASCADE, verbose_name="پرسشنامه")
    question = models.ForeignKey("Question", on_delete=models.CASCADE, db_column='question_id', verbose_name="سوال")  # Foreign key to the Question model
    answer = models.ForeignKey("Option", on_delete=models.CASCADE, db_column='answer_id', verbose_name="جواب")  # Foreign key to the Option model
    chat_id = models.TextField(verbose_name="ایدی چت")  # This remains as it stores the list of message IDs as a comma-separated string

    class Meta:
        verbose_name = "جواب"
        verbose_name_plural = "جواب ها"




class Option(models.Model):
    Answers = models.TextField(verbose_name="جواب ها")  # Only the 'Answers' column is defined
    class Meta:
        verbose_name = "گزینه"
        verbose_name_plural = "گزینه ها"