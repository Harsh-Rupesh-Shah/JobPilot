import { useState } from 'react'

interface JobInputProps {
  onStart: (jobUrl: string, jobDescription: string) => Promise<void>
  isStarting: boolean
}

export default function JobInput({ onStart, isStarting }: JobInputProps) {
  const [jobUrl, setJobUrl] = useState('')
  const [jobDescription, setJobDescription] = useState('')

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-8 animate-fade-in">
      <div className="text-center mb-4">
        <h2 className="font-display-lg text-primary mb-2">Target Job</h2>
        <p className="font-interface-md text-on-surface-variant">Provide the job listing URL or paste the description manually.</p>
      </div>

      <div className="card p-8 flex flex-col gap-6">
        <div className="space-y-2">
          <label htmlFor="jobUrl" className="input-label !mb-0">Job URL (Optional)</label>
          <input
            id="jobUrl"
            type="url"
            placeholder="https://linkedin.com/jobs/..."
            className="input-field"
            value={jobUrl}
            onChange={(e) => setJobUrl(e.target.value)}
          />
          <p className="text-xs text-on-surface-variant mt-1">If provided, we will attempt to scrape the job details automatically.</p>
        </div>

        <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-outline-variant"></span>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-3 bg-surface-container-lowest font-label-caps text-label-caps text-outline uppercase">
                AND / OR
              </span>
            </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="jobDesc" className="input-label !mb-0">Job Description</label>
          <textarea
            id="jobDesc"
            rows={8}
            placeholder="Paste the full job description here..."
            className="input-field resize-y font-interface-sm"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>

        <button
          onClick={() => onStart(jobUrl, jobDescription)}
          disabled={isStarting || (!jobUrl && !jobDescription)}
          className="btn-primary mt-4"
        >
          {isStarting ? (
            <>
              <span className="material-symbols-outlined animate-spin-slow">progress_activity</span>
              Starting Co-Pilot...
            </>
          ) : (
            <>
              Generate Tailored Application
              <span className="material-symbols-outlined">magic_button</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
