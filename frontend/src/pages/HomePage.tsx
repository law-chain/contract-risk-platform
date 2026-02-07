import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listEngagements, deleteEngagement } from '../api/engagements';

export default function HomePage() {
  const queryClient = useQueryClient();
  const { data: engagements, isLoading } = useQuery({
    queryKey: ['engagements'],
    queryFn: listEngagements,
  });

  const deleteMut = useMutation({
    mutationFn: deleteEngagement,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['engagements'] }),
  });

  if (isLoading) return <div className="text-gray-500">Loading...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Engagements</h1>
      {!engagements?.length ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No engagements yet.</p>
          <Link
            to="/engagement/new"
            className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700"
          >
            Create your first engagement
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {engagements.map((e) => (
            <div key={e.id} className="bg-white rounded-lg shadow p-6 flex justify-between items-center">
              <div>
                <Link to={`/engagement/${e.id}/wizard`} className="text-lg font-semibold text-blue-600 hover:underline">
                  {e.name}
                </Link>
                <div className="text-sm text-gray-500 mt-1">
                  {e.industry || 'No industry'} &middot; {e.currency} {e.contract_value?.toLocaleString() ?? 'N/A'} &middot;{' '}
                  <span className="capitalize">{e.status.replace('_', ' ')}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Link
                  to={`/engagement/${e.id}/dashboard`}
                  className="bg-green-600 text-white px-3 py-1.5 rounded text-sm hover:bg-green-700"
                >
                  Dashboard
                </Link>
                <Link
                  to={`/engagement/${e.id}/wizard`}
                  className="bg-blue-100 text-blue-700 px-3 py-1.5 rounded text-sm hover:bg-blue-200"
                >
                  Edit
                </Link>
                <button
                  onClick={() => { if (confirm('Delete this engagement?')) deleteMut.mutate(e.id); }}
                  className="bg-red-100 text-red-700 px-3 py-1.5 rounded text-sm hover:bg-red-200"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
