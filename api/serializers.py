from rest_framework import serializers
from .models import Assessment, Question, Choice, Attempt, Answer

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text'] # Intentionally omitting 'is_correct' to prevent cheating via API

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'points', 'choices']

class AssessmentSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source='questions.count', read_only=True)
    
    class Meta:
        model = Assessment
        fields = ['id', 'title', 'description', 'time_limit_minutes', 'question_count']

class AssessmentDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Assessment
        fields = ['id', 'title', 'description', 'time_limit_minutes', 'questions']

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()
