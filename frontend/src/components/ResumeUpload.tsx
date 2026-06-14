import { useState } from 'react'
import { resumeApi, type ParsedResume } from '../api/client'

interface ResumeUploadProps {
  onNext: (resumeId: string) => void
}

export default function ResumeUpload({ onNext }: ResumeUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [parsed, setParsed] = useState<ParsedResume | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return
    await handleUpload(selectedFile)
  }

  const handleUpload = async (fileToUpload: File) => {
    setIsUploading(true)
    setError(null)
    try {
      const res = await resumeApi.upload(fileToUpload)
      setParsed(res)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload resume')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 w-full max-w-container mx-auto">
      {/* Left Column: Upload & Actions */}
      <div className="lg:col-span-7 flex flex-col gap-8">
        
        {!parsed && !isUploading && (
          <div className="relative bg-surface-container-lowest p-1 upload-dashed-border rounded-xl group transition-all duration-300 hover:shadow-lg">
            <div className="flex flex-col items-center justify-center py-20 px-8 cursor-pointer relative">
              <input 
                type="file" 
                id="resumeUpload" 
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" 
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={handleFileChange}
              />
              <div className="w-16 h-16 rounded-full bg-secondary/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-secondary text-4xl">cloud_upload</span>
              </div>
              <p className="font-interface-md text-interface-md font-bold text-primary mb-2">Drop your PDF or DOCX here</p>
              <p className="font-interface-sm text-interface-sm text-on-surface-variant">
                or click to browse <span className="mx-1">·</span> Max 10 MB <span className="mx-1">·</span> PDF and DOCX only
              </p>
            </div>
          </div>
        )}

        {isUploading && (
          <div className="card p-12 flex flex-col items-center justify-center text-center animate-fade-in">
            <span className="material-symbols-outlined text-4xl text-secondary animate-spin-slow mb-4">progress_activity</span>
            <p className="font-interface-md font-medium">Parsing resume...</p>
            <p className="font-interface-sm text-on-surface-variant mt-2">Extracting your career history</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-error-container text-on-error-container rounded-lg font-interface-sm flex items-start gap-3">
             <span className="material-symbols-outlined text-error">error</span>
             <div>
                <p className="font-bold">Upload failed</p>
                <p>{error}</p>
             </div>
          </div>
        )}

        {/* File Info Row */}
        {parsed && !isUploading && (
          <div className="flex items-center justify-between p-4 bg-surface-container-lowest border border-outline-variant rounded-lg animate-fade-in">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-surface-container-high rounded flex items-center justify-center">
                <span className="material-symbols-outlined text-on-surface-variant">description</span>
              </div>
              <div>
                <p className="font-interface-md text-interface-md font-medium text-primary">{parsed.filename}</p>
                <p className="font-interface-sm text-interface-sm text-on-surface-variant">
                  <span className="text-on-tertiary-container font-medium inline-flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">check_circle</span>
                    Uploaded & Parsed
                  </span>
                </p>
              </div>
            </div>
            <button 
              onClick={() => { setParsed(null) }}
              className="text-error font-interface-sm text-interface-sm hover:underline px-2 py-1"
            >
              Remove
            </button>
          </div>
        )}

        {/* Primary CTA */}
        {parsed && (
          <button 
            onClick={() => onNext(parsed.resume_id)}
            className="btn-primary w-full h-14 text-lg"
          >
            Continue to Job Input
            <span className="material-symbols-outlined">arrow_forward</span>
          </button>
        )}
      </div>

      {/* Right Column: Preview */}
      <div className="lg:col-span-5">
        <div className="card overflow-hidden flex flex-col h-[500px]">
          <div className="p-4 border-b border-outline-variant bg-surface-container-low flex items-center justify-between">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest">
              Parsed Resume Preview
            </span>
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-outline-variant"></div>
              <div className="w-2 h-2 rounded-full bg-outline-variant"></div>
              <div className="w-2 h-2 rounded-full bg-outline-variant"></div>
            </div>
          </div>
          <div className="p-6 overflow-y-auto bg-surface-container-lowest flex-grow font-mono text-[13px] leading-relaxed text-on-surface-variant whitespace-pre-wrap">
            {parsed ? parsed.text : (
               <div className="h-full flex items-center justify-center text-outline/50 text-center italic">
                  Upload a resume to see the parsed content here.<br/>
                  We extract text for the AI to analyze.
               </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
