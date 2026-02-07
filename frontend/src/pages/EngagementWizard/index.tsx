import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getEngagement, createEngagement } from '../../api/engagements';
import ContextStep from './ContextStep';
import FailureModesStep from './FailureModesStep';
import LossMappingStep from './LossMappingStep';
import MitigationsStep from './MitigationsStep';
import ReviewStep from './ReviewStep';

const STEPS = ['Context', 'Failure Modes', 'Loss Mapping', 'Mitigations', 'Review & Run'];

export default function EngagementWizard() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [engagementId, setEngagementId] = useState<number | null>(id && id !== 'new' ? parseInt(id) : null);

  const { data: engagement, refetch } = useQuery({
    queryKey: ['engagement', engagementId],
    queryFn: () => getEngagement(engagementId!),
    enabled: !!engagementId,
  });

  useEffect(() => {
    if (id && id !== 'new') {
      setEngagementId(parseInt(id));
    }
  }, [id]);

  const handleCreate = async (data: Record<string, unknown>) => {
    const eng = await createEngagement(data as Partial<import('../../types').Engagement>);
    setEngagementId(eng.id);
    navigate(`/engagement/${eng.id}/wizard`, { replace: true });
    setStep(1);
  };

  const renderStep = () => {
    if (step === 0) {
      return <ContextStep engagement={engagement ?? null} engagementId={engagementId} onCreate={handleCreate} onSaved={() => { refetch(); setStep(1); }} />;
    }
    if (!engagementId) return <div>Please complete the context step first.</div>;
    switch (step) {
      case 1: return <FailureModesStep engagementId={engagementId} />;
      case 2: return <LossMappingStep engagementId={engagementId} />;
      case 3: return <MitigationsStep engagementId={engagementId} />;
      case 4: return <ReviewStep engagementId={engagementId} />;
      default: return null;
    }
  };

  return (
    <div>
      <div className="mb-8">
        <nav className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {STEPS.map((label, i) => (
            <button
              key={label}
              onClick={() => engagementId && setStep(i)}
              className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                i === step
                  ? 'bg-white text-blue-700 shadow'
                  : engagementId
                  ? 'text-gray-600 hover:text-gray-900'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
              disabled={!engagementId && i > 0}
            >
              {i + 1}. {label}
            </button>
          ))}
        </nav>
      </div>

      {renderStep()}

      <div className="mt-8 flex justify-between">
        <button
          onClick={() => setStep(Math.max(0, step - 1))}
          disabled={step === 0}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md disabled:opacity-50"
        >
          Previous
        </button>
        <button
          onClick={() => {
            if (step < STEPS.length - 1) setStep(step + 1);
            else if (engagementId) navigate(`/engagement/${engagementId}/dashboard`);
          }}
          disabled={!engagementId && step === 0}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {step === STEPS.length - 1 ? 'Go to Dashboard' : 'Next'}
        </button>
      </div>
    </div>
  );
}
