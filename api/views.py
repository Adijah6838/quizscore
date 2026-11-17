from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Assessment, Attempt, Answer, Choice
from .serializers import AssessmentSerializer, AssessmentDetailSerializer

class AssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Assessment.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssessmentDetailSerializer
        return AssessmentSerializer

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        assessment = self.get_object()
        session_id = request.data.get('session_id', 'anonymous')
        
        # Check if an attempt already exists
        attempt, created = Attempt.objects.get_or_create(
            assessment=assessment,
            user_session=session_id
        )
        
        if not created and attempt.status != 'in_progress':
            return Response(
                {"error": "You have already completed this assessment."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if attempt.is_expired():
            attempt.status = 'expired'
            attempt.save()
            return Response({"error": "Assessment time limit has expired."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "attempt_id": attempt.id,
            "started_at": attempt.started_at,
            "time_limit_minutes": assessment.time_limit_minutes
        })

    @action(detail=True, methods=['post'], url_path='submit/(?P<attempt_id>[^/.]+)')
    def submit(self, request, pk=None, attempt_id=None):
        assessment = self.get_object()
        session_id = request.data.get('session_id', 'anonymous')
        
        try:
            attempt = Attempt.objects.get(id=attempt_id, assessment=assessment, user_session=session_id)
        except Attempt.DoesNotExist:
            return Response({"error": "Attempt not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent duplicate final submissions
        if attempt.status != 'in_progress':
            return Response({"error": "This attempt has already been finalized."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for expiration
        if attempt.is_expired():
            attempt.status = 'expired'
            attempt.submitted_at = timezone.now()
            attempt.save()
            return Response({"error": "Time limit exceeded. Attempt expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Process submitted answers
        answers_data = request.data.get('answers', [])
        total_score = 0
        total_possible_points = sum(q.points for q in assessment.questions.all())

        # Use a transaction to ensure consistency
        from django.db import transaction
        with transaction.atomic():
            for ans in answers_data:
                q_id = ans.get('question_id')
                c_id = ans.get('choice_id')
                
                try:
                    question = assessment.questions.get(id=q_id)
                    choice = Choice.objects.get(id=c_id, question=question)
                    
                    # Record the answer
                    Answer.objects.update_or_create(
                        attempt=attempt,
                        question=question,
                        defaults={'selected_choice': choice}
                    )
                    
                    # Score calculation (Server-authoritative)
                    if choice.is_correct:
                        total_score += question.points
                        
                except (Question.DoesNotExist, Choice.DoesNotExist):
                    continue # Skip invalid answers instead of failing the whole submission

            # Calculate percentage
            final_percentage = (total_score / total_possible_points * 100) if total_possible_points > 0 else 0
            
            attempt.status = 'completed'
            attempt.score = round(final_percentage, 2)
            attempt.submitted_at = timezone.now()
            attempt.save()

        return Response({
            "message": "Assessment submitted successfully.",
            "score": attempt.score,
            "total_points": total_possible_points,
            "earned_points": total_score,
            "status": attempt.status
        })

    @action(detail=True, methods=['get'], url_path='results/(?P<attempt_id>[^/.]+)')
    def results(self, request, pk=None, attempt_id=None):
        session_id = request.query_params.get('session_id', 'anonymous')
        
        try:
            attempt = Attempt.objects.get(id=attempt_id, assessment_id=pk, user_session=session_id)
            return Response({
                "status": attempt.status,
                "score": attempt.score,
                "started_at": attempt.started_at,
                "submitted_at": attempt.submitted_at,
            })
        except Attempt.DoesNotExist:
            return Response({"error": "Results not found."}, status=status.HTTP_404_NOT_FOUND)
