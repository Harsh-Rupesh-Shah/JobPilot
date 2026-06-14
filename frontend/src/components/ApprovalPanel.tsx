import { useState } from 'react'

interface ApprovalPanelProps {
  outputs: {
    tailored_resume: string
    cover_letter: string
    outreach_draft: string
    interview_qa: string
  }
  onApprove: (edited: { tailored_resume: string; cover_letter: string; outreach_draft: string; interview_qa: string }) => Promise<void>
}

export default function ApprovalPanel({ outputs, onApprove }: ApprovalPanelProps) {
  const [editedResume, setEditedResume] = useState(outputs.tailored_resume)
  const [editedLetter, setEditedLetter] = useState(outputs.cover_letter)
  const [editedOutreach, setEditedOutreach] = useState(outputs.outreach_draft)
  const [editedQa, setEditedQa] = useState(outputs.interview_qa)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState<'resume' | 'cover_letter' | 'outreach' | 'qa'>('resume')

  const handleApprove = async () => {
    setIsSubmitting(true)
    try {
      await onApprove({
        tailored_resume: editedResume,
        cover_letter: editedLetter,
        outreach_draft: editedOutreach,
        interview_qa: editedQa,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col h-[80vh] max-h-[800px] w-full max-w-6xl mx-auto card overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="p-6 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
        <div>
          <h2 className="font-headline-lg-mobile text-primary mb-1">Review & Approve</h2>
          <p className="font-interface-sm text-on-surface-variant">
            Edit the AI-generated drafts below. Click approve to finalize.
          </p>
        </div>
        <button
          onClick={handleApprove}
          disabled={isSubmitting}
          className="btn-primary"
        >
          {isSubmitting ? (
            <>
               <span className="material-symbols-outlined animate-spin-slow">progress_activity</span>
               Approving...
            </>
          ) : (
             <>
               Approve All Drafts
               <span className="material-symbols-outlined">check_circle</span>
             </>
          )}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-outline-variant bg-surface-container-lowest px-6">
        {[
          { id: 'resume', label: 'Tailored Resume' },
          { id: 'cover_letter', label: 'Cover Letter' },
          { id: 'outreach', label: 'Outreach Email' },
          { id: 'qa', label: 'Interview Q&A' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-6 py-4 font-interface-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-secondary text-secondary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Editor Area */}
      <div className="flex-1 bg-surface-container-lowest p-6 overflow-hidden flex">
        <textarea
          className="w-full h-full p-4 font-mono text-[13px] leading-relaxed text-on-surface border border-outline-variant rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary/20 resize-none"
          value={
            activeTab === 'resume'
              ? editedResume
              : activeTab === 'cover_letter'
              ? editedLetter
              : activeTab === 'outreach'
              ? editedOutreach
              : editedQa
          }
          onChange={(e) => {
            if (activeTab === 'resume') setEditedResume(e.target.value)
            if (activeTab === 'cover_letter') setEditedLetter(e.target.value)
            if (activeTab === 'outreach') setEditedOutreach(e.target.value)
            if (activeTab === 'qa') setEditedQa(e.target.value)
          }}
        />
      </div>
    </div>
  )
}
