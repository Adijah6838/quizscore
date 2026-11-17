import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from .models import Assessment, Question, Choice, Attempt

@pytest.mark.django_db
class TestAssessmentScoring:
    
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def setup_assessment(self):
        # Create a 3-question assessment
        assessment = Assessment.objects.create(
            title='Test Assessment',
            time_limit_minutes=10
        )
        
        q1 = Question.objects.create(assessment=assessment, text='Q1', points=1)
        Choice.objects.create(question=q1, text='Correct', is_correct=True)
        Choice.objects.create(question=q1, text='Wrong', is_correct=False)
        
        q2 = Question.objects.create(assessment=assessment, text='Q2', points=2)
        Choice.objects.create(question=q2, text='Correct', is_correct=True)
        Choice.objects.create(question=q2, text='Wrong', is_correct=False)
        
        q3 = Question.objects.create(assessment=assessment, text='Q3', points=3)
        Choice.objects.create(question=q3, text='Correct', is_correct=True)
        Choice.objects.create(question=q3, text='Wrong', is_correct=False)
        
        return assessment

    def test_scoring_accuracy(self, client, setup_assessment):
        assessment = setup_assessment
        url = reverse('assessment-start', args=[assessment.id])
        response = client.post(url, {'session_id': 'user1'})
        attempt_id = response.data['attempt_id']
        
        q1_correct = Question.objects.get(id=assessment.questions.all()[0].id).choices.get(is_correct=True).id
        q2_correct = Question.objects.get(id=assessment.questions.all()[1].id).choices.get(is_correct=True).id
        q3_wrong = Question.objects.get(id=assessment.questions.all()[2].id).choices.get(is_correct=False).id
        
        url = reverse('assessment-submit', args=[assessment.id, attempt_id])
        payload = {
            'session_id': 'user1',
            'answers': [
                {'question_id': assessment.questions.all()[0].id, 'choice_id': q1_correct},
                {'question_id': assessment.questions.all()[1].id, 'choice_id': q2_correct},
                {'question_id': assessment.questions.all()[2].id, 'choice_id': q3_wrong},
            ]
        }
        response = client.post(url, payload, format='json')
        
        assert response.status_code == 200
        assert response.data['score'] == 50.0
        assert response.data['status'] == 'completed'

    def test_prevent_duplicate_submission(self, client, setup_assessment):
        assessment = setup_assessment
        url = reverse('assessment-start', args=[assessment.id])
        attempt_id = client.post(url, {'session_id': 'user1'}).data['attempt_id']
        
        submit_url = reverse('assessment-submit', args=[assessment.id, attempt_id])
        payload = {'session_id': 'user1', 'answers': []}
        
        client.post(submit_url, payload, format='json')
        
        response = client.post(submit_url, payload, format='json')
        assert response.status_code == 400
        assert 'already been finalized' in response.data['error']

    def test_expired_assessment(self, client, setup_assessment):
        assessment = setup_assessment
        
        # Create the attempt normally (auto_now_add sets started_at to now)
        attempt = Attempt.objects.create(
            assessment=assessment, 
            user_session='user1'
        )
        
        # Bypass auto_now_add by using .update() to backdate started_at
        past_time = timezone.now() - timedelta(minutes=15)
        Attempt.objects.filter(id=attempt.id).update(started_at=past_time)
        
        # Refresh from DB
        attempt.refresh_from_db()
        
        url = reverse('assessment-submit', args=[assessment.id, attempt.id])
        response = client.post(url, {'session_id': 'user1', 'answers': []}, format='json')
        
        assert response.status_code == 400
        assert 'Time limit exceeded' in response.data['error']
