import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ResumeUpload from './components/ResumeUpload'
import JobInput from './components/JobInput'
import StreamOutput from './components/StreamOutput'
import ApprovalPanel from './components/ApprovalPanel'
import ApplicationTracker from './components/ApplicationTracker'
import { useApplication } from './hooks/useApplication'
import { useSSE } from './hooks/useSSE'
import { useState } from 'react'

// ── Protected Route Wrapper ────────────────────────────────────────────────
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><span className="material-symbols-outlined animate-spin-slow text-4xl text-secondary">progress_activity</span></div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

// ── Main Layout ────────────────────────────────────────────────────────────
const MainLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, logout } = useAuth()

  return (
    <div className="bg-surface text-on-surface antialiased min-h-screen">
      {/* SideNavBar */}
      <nav className="fixed left-0 top-0 h-full flex flex-col py-8 px-4 bg-surface w-64 border-r border-outline-variant z-50">
        <div className="mb-12 px-4">
          <h1 className="font-headline-lg text-headline-lg font-bold text-primary tracking-tight">JobPilot</h1>
          <p className="font-interface-sm text-interface-sm text-on-surface-variant mt-1">AI Career Advisor</p>
        </div>
        
        <Link to="/" className="mb-8 mx-4 bg-primary text-on-primary py-3 px-4 rounded-lg font-interface-md text-interface-md flex items-center justify-center gap-2 hover:opacity-80 transition-opacity">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>add</span>
          New Application
        </Link>
        
        <ul className="flex flex-col gap-2 flex-grow">
          <li>
            <Link to="/" className="flex items-center gap-3 px-4 py-3 text-primary font-bold border-r-2 border-primary bg-surface-container-low transition-colors">
              <span className="material-symbols-outlined">clinical_notes</span>
              <span className="font-interface-md text-interface-md">Workspace</span>
            </Link>
          </li>
          <li>
            <Link to="/tracker" className="flex items-center gap-3 px-4 py-3 text-on-surface-variant font-medium hover:bg-surface-container-high transition-colors">
              <span className="material-symbols-outlined">dashboard_customize</span>
              <span className="font-interface-md text-interface-md">Applications</span>
            </Link>
          </li>
        </ul>
        
        <div className="mt-auto pt-4 border-t border-outline-variant">
          <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-3 text-on-surface-variant font-medium hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-interface-md text-interface-md">Log Out</span>
          </button>
        </div>
      </nav>

      {/* TopAppBar */}
      <header className="sticky top-0 z-40 w-full flex justify-between items-center px-8 h-16 ml-64 max-w-[calc(100%-16rem)] bg-surface/80 backdrop-blur-md border-b border-outline-variant/30 shadow-sm">
        <div className="flex items-center gap-6">
          <nav className="hidden md:flex gap-6">
            <span className="font-interface-md text-interface-md text-on-surface-variant py-5">{user?.email}</span>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-on-surface-variant hover:text-primary transition-colors">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <div className="w-8 h-8 rounded-full bg-surface-container-high border border-outline-variant overflow-hidden flex items-center justify-center text-primary font-bold">
            {user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </header>

      {/* Main Content Canvas */}
      <main className="ml-64 p-8 max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  )
}

// ── Application Flow Orchestrator ──────────────────────────────────────────
const ApplicationFlow = () => {
  const [step, setStep] = useState<'upload' | 'job' | 'running' | 'approval'>('upload')
  const [resumeId, setResumeId] = useState<string | null>(null)
  
  const app = useApplication()
  const sse = useSSE(app.runId)

  // Move to approval when interrupt received
  if (sse.interruptPayload && step === 'running') {
    setStep('approval')
  }

  const handleStart = async (jobUrl: string, jobDesc: string) => {
    if (!resumeId) return
    await app.startRun(jobUrl, jobDesc, resumeId)
    setStep('running')
  }

  const handleApprove = async (edited: any) => {
    await app.approve(edited)
    // reset for next run
    app.reset()
    sse.reset()
    setStep('upload')
    setResumeId(null)
  }

  return (
    <div className="flex flex-col gap-8 w-full max-w-6xl mx-auto">
      {/* 3-Step Progress Indicator */}
      <div className="flex items-center gap-4 mb-4 pb-4 border-b border-outline-variant">
        <div className={`flex items-center gap-2 ${step === 'upload' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step === 'upload' ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>1</div>
          <span className="font-label-caps uppercase tracking-wider text-xs">Upload Context</span>
        </div>
        <div className="w-12 h-[1px] bg-outline-variant"></div>
        <div className={`flex items-center gap-2 ${step === 'job' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step === 'job' ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>2</div>
          <span className="font-label-caps uppercase tracking-wider text-xs">Target Job</span>
        </div>
        <div className="w-12 h-[1px] bg-outline-variant"></div>
        <div className={`flex items-center gap-2 ${['running', 'approval'].includes(step) ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${['running', 'approval'].includes(step) ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>3</div>
          <span className="font-label-caps uppercase tracking-wider text-xs">Co-Pilot Run</span>
        </div>
      </div>

      {step === 'upload' && (
        <div className="animate-fade-in">
          <div className="mb-8">
            <h1 className="font-display-lg text-primary mb-2">Upload your Context</h1>
            <p className="font-interface-md text-on-surface-variant">Provide your current resume to act as the ground truth for your experience.</p>
          </div>
          <ResumeUpload onNext={(id) => { setResumeId(id); setStep('job') }} />
        </div>
      )}
      
      {step === 'job' && (
        <JobInput onStart={handleStart} isStarting={app.isPolling && step === 'job'} />
      )}
      
      {step === 'running' && (
        <div className="flex flex-col gap-8 w-full animate-fade-in">
          <div className="text-center">
            <h2 className="font-display-lg text-primary mb-2">Co-Pilot is Running</h2>
            <p className="font-interface-md text-on-surface-variant flex items-center justify-center gap-2">
              <span className="material-symbols-outlined animate-spin-slow text-secondary">sync</span>
              Generating institutional-grade application materials...
            </p>
          </div>
          <StreamOutput tokens={sse.agentTokens} currentAgent={app.status?.current_agent} />
        </div>
      )}

      {step === 'approval' && sse.interruptPayload?.outputs && (
        <ApprovalPanel 
          outputs={sse.interruptPayload.outputs as any} 
          onApprove={handleApprove} 
        />
      )}
    </div>
  )
}

// ── App Root ───────────────────────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout>
                <ApplicationFlow />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/tracker" element={
            <ProtectedRoute>
              <MainLayout>
                <ApplicationTracker />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
