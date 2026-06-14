import { useEffect, useState } from 'react'
import { resumeApi, type ParsedResume } from '../api/client'
import { Link } from 'react-router-dom'

export default function MasterProfile() {
  const [profile, setProfile] = useState<ParsedResume | null>(null)
  const [editedText, setEditedText] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    resumeApi.getLatest().then((res) => {
      if (res) {
        setProfile(res)
        setEditedText(res.text)
      }
    }).finally(() => setIsLoading(false))
  }, [])

  const handleSave = async () => {
    setIsSaving(true)
    setSaveSuccess(false)
    try {
      const updated = await resumeApi.update(editedText)
      setProfile(updated)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      console.error('Failed to update profile', err)
      alert('Failed to update profile')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center p-12">
        <span className="material-symbols-outlined animate-spin-slow text-4xl text-secondary">progress_activity</span>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto w-full animate-fade-in pb-12">
        <div className="mb-8">
          <h1 className="font-display-lg text-primary mb-2">Master Profile</h1>
          <p className="font-interface-md text-on-surface-variant">Your ground-truth experience used by the AI Copilot.</p>
        </div>
        <div className="card p-12 text-center text-on-surface-variant font-interface-md">
          <span className="material-symbols-outlined text-4xl mb-4 block text-outline">person_off</span>
          No master profile found.<br/>
          <Link to="/" className="btn-primary inline-flex items-center gap-2 mt-6">
            <span className="material-symbols-outlined">upload_file</span>
            Upload a Resume
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto w-full animate-fade-in pb-12 flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-8 flex justify-between items-end flex-shrink-0">
        <div>
          <h1 className="font-display-lg text-primary mb-2">Master Profile</h1>
          <p className="font-interface-md text-on-surface-variant">
            Edit your ground-truth experience. Changes here will immediately reflect in all future Co-Pilot runs.
          </p>
        </div>
        <div className="flex items-center gap-4">
          {saveSuccess && (
            <span className="text-secondary font-interface-sm font-medium flex items-center gap-1 animate-fade-in">
              <span className="material-symbols-outlined text-[18px]">check_circle</span>
              Saved
            </span>
          )}
          <button 
            onClick={handleSave} 
            disabled={isSaving || editedText === profile.text}
            className="btn-primary flex items-center gap-2"
          >
            {isSaving ? (
              <span className="material-symbols-outlined animate-spin-slow text-[20px]">progress_activity</span>
            ) : (
              <span className="material-symbols-outlined text-[20px]">save</span>
            )}
            Save Changes
          </button>
        </div>
      </div>

      <div className="card flex-grow overflow-hidden flex flex-col">
        <div className="p-4 border-b border-outline-variant bg-surface-container-low flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-secondary">description</span>
            <span className="font-interface-sm font-medium text-primary">{profile.filename}</span>
          </div>
          <span className="text-xs font-label-caps text-on-surface-variant">Raw Text Editor</span>
        </div>
        <textarea
          className="w-full flex-grow p-6 font-mono text-[13.5px] leading-relaxed text-on-surface bg-surface-container-lowest focus:outline-none focus:ring-2 focus:ring-inset focus:ring-secondary/20 resize-none"
          value={editedText}
          onChange={(e) => setEditedText(e.target.value)}
          placeholder="Your raw resume text..."
        />
      </div>
    </div>
  )
}
