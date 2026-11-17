import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchApi } from '../api';
import { Assessment } from '../types';
import { Clock, FileQuestion } from 'lucide-react';

export function Home() {
  const { data: assessments, isLoading } = useQuery({
    queryKey: ['assessments'],
    queryFn: () => fetchApi<Assessment[]>('/assessments/'),
  });

  if (isLoading) return <div className="p-8 text-center">Loading assessments...</div>;

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Available Assessments</h1>
      <p className="text-gray-500 mb-8">Select an assessment to begin your timed attempt.</p>

      <div className="grid gap-4 md:grid-cols-2">
        {assessments?.map((assessment) => (
          <div key={assessment.id} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col">
            <h2 className="text-xl font-bold text-gray-900 mb-2">{assessment.title}</h2>
            <p className="text-gray-600 mb-4 flex-1">{assessment.description}</p>
            
            <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
              <div className="flex items-center gap-1">
                <Clock size={16} />
                {assessment.time_limit_minutes} mins
              </div>
              <div className="flex items-center gap-1">
                <FileQuestion size={16} />
                {assessment.question_count} questions
              </div>
            </div>

            <Link
              to={`/quiz/\`}
              className="block text-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors"
            >
              Start Assessment
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
