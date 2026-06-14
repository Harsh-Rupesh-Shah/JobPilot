import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { applicationsApi, type ApplicationRecord } from '../api/client'

export default function ApplicationTracker() {
  const [apps, setApps] = useState<ApplicationRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [appToDelete, setAppToDelete] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    const fetchApps = async () => {
      try {
        const data = await applicationsApi.list()
        setApps(data)
      } catch (err) {
        console.error('Failed to fetch applications', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchApps()
  }, [])

  const confirmDelete = async () => {
    if (!appToDelete) return
    setIsDeleting(true)
    try {
      await applicationsApi.delete(appToDelete)
      setApps(apps.filter(app => app._id !== appToDelete))
      setAppToDelete(null)
    } catch (err) {
      console.error('Failed to delete application', err)
      alert('Failed to delete application')
    } finally {
      setIsDeleting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center p-12">
        <span className="material-symbols-outlined animate-spin-slow text-4xl text-secondary">progress_activity</span>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto w-full animate-fade-in">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="font-display-lg text-primary mb-2">Application Tracker</h1>
          <p className="font-interface-md text-on-surface-variant">View and export all your tailored applications.</p>
        </div>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left font-interface-sm">
          <thead className="bg-surface-container-low border-b border-outline-variant text-on-surface-variant font-label-caps uppercase tracking-wider text-xs">
            <tr>
              <th className="px-6 py-4 font-semibold">Company / Role</th>
              <th className="px-6 py-4 font-semibold">Date</th>
              <th className="px-6 py-4 font-semibold">Status</th>
              <th className="px-6 py-4 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant">
            {apps.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-on-surface-variant">
                  <p className="mb-4">No applications tracked yet.</p>
                  <Link to="/" className="btn-primary inline-flex items-center gap-2">
                    <span className="material-symbols-outlined">add</span>
                    Start a new Co-Pilot run
                  </Link>
                </td>
              </tr>
            ) : (
              apps.map((app) => (
                <tr key={app._id} className="hover:bg-surface-container-lowest/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-primary">{app.company}</div>
                    <div className="text-on-surface-variant text-xs mt-1">{app.role}</div>
                  </td>
                  <td className="px-6 py-4 text-on-surface-variant">
                    {new Date(app.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`chip ${
                      app.status === 'running' ? 'chip-running' :
                      app.status === 'pending_approval' ? 'chip-pending' :
                      app.status === 'complete' ? 'chip-complete' : 'chip-failed'
                    }`}>
                      {app.status === 'running' && <span className="material-symbols-outlined text-[14px]">sync</span>}
                      {app.status === 'pending_approval' && <span className="material-symbols-outlined text-[14px]">pause_circle</span>}
                      {app.status === 'complete' && <span className="material-symbols-outlined text-[14px]">check_circle</span>}
                      {app.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {app.status === 'complete' ? (
                        <>
                          <a 
                            href={applicationsApi.exportUrl(app._id, 'pdf')}
                            target="_blank"
                            rel="noreferrer"
                            className="btn-ghost !px-3"
                            title="Download PDF"
                          >
                            <span className="material-symbols-outlined text-secondary">picture_as_pdf</span>
                          </a>
                          <a 
                            href={applicationsApi.exportUrl(app._id, 'docx')}
                            target="_blank"
                            rel="noreferrer"
                            className="btn-ghost !px-3"
                            title="Download DOCX"
                          >
                            <span className="material-symbols-outlined text-secondary">description</span>
                          </a>
                        </>
                      ) : (
                        <span className="text-on-surface-variant text-xs italic mr-2">In Progress</span>
                      )}
                      
                      <button 
                        onClick={() => setAppToDelete(app._id)}
                        className="btn-ghost !px-3 !text-error hover:bg-error-container/20"
                        title="Delete Application"
                      >
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Custom Delete Confirmation Modal */}
      {appToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-scrim/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-surface-container-low rounded-2xl p-8 max-w-md w-full shadow-lg border border-outline-variant mx-4">
            <div className="flex items-center gap-4 mb-4 text-error">
              <span className="material-symbols-outlined text-4xl">warning</span>
              <h2 className="font-headline-sm">Delete Application</h2>
            </div>
            <p className="font-interface-md text-on-surface-variant mb-8">
              Are you sure you want to permanently delete this application? This action cannot be undone and will remove the generated resume and cover letter.
            </p>
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setAppToDelete(null)}
                className="px-5 py-2.5 font-interface-md font-medium text-on-surface-variant hover:bg-surface-container-high rounded-lg transition-colors"
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button 
                onClick={confirmDelete}
                className="px-5 py-2.5 font-interface-md font-bold bg-error text-on-error rounded-lg hover:opacity-90 transition-opacity flex items-center gap-2"
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <span className="material-symbols-outlined animate-spin-slow text-[20px]">progress_activity</span>
                ) : (
                  <span className="material-symbols-outlined text-[20px]">delete</span>
                )}
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
