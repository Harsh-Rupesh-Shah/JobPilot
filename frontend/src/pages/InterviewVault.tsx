import { useEffect, useState } from 'react'
import { applicationsApi, type VaultRecord } from '../api/client'

export default function InterviewVault() {
  const [records, setRecords] = useState<VaultRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    applicationsApi.getVault().then(setRecords).finally(() => setIsLoading(false))
  }, [])

  if (isLoading) {
    return (
      <div className="flex justify-center p-12">
        <span className="material-symbols-outlined animate-spin-slow text-4xl text-secondary">progress_activity</span>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto w-full animate-fade-in pb-12">
      <div className="mb-8">
        <h1 className="font-display-lg text-primary mb-2">Interview Vault</h1>
        <p className="font-interface-md text-on-surface-variant">Your personalized, aggregated study guide compiled from every application you've submitted.</p>
      </div>

      {records.length === 0 ? (
        <div className="card p-12 text-center text-on-surface-variant font-interface-md">
          <span className="material-symbols-outlined text-4xl mb-4 block text-outline">menu_book</span>
          No interview prep generated yet.<br/>
          Complete a Co-Pilot run to start building your vault!
        </div>
      ) : (
        <div className="flex flex-col gap-8">
          {records.map((record) => (
            <div key={record._id} className="card overflow-hidden">
              <div className="p-6 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
                <div>
                  <h3 className="font-headline-sm text-primary mb-1">{record.company}</h3>
                  <p className="font-interface-sm text-on-surface-variant font-medium">{record.role}</p>
                </div>
                <div className="text-xs font-label-caps tracking-wider text-on-surface-variant">
                  {new Date(record.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                </div>
              </div>
              <div className="p-8 font-mono text-[13.5px] leading-relaxed text-on-surface whitespace-pre-wrap bg-surface-container-lowest">
                {record.interview_qa}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
