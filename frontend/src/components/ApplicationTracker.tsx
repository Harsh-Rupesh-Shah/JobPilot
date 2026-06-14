import { useEffect, useState } from 'react'
import { applicationsApi, type ApplicationRecord } from '../api/client'

export default function ApplicationTracker() {
  const [apps, setApps] = useState<ApplicationRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)

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
                  No applications tracked yet. Start a new Co-Pilot run!
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
                    {app.status === 'complete' ? (
                      <div className="flex justify-end gap-2">
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
                      </div>
                    ) : (
                      <span className="text-on-surface-variant text-xs italic">In Progress</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
