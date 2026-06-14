import { useEffect, useRef } from 'react'
import { type AgentTokens } from '../hooks/useSSE'

interface StreamOutputProps {
  tokens: AgentTokens
  currentAgent: string | undefined
}

function AgentBox({ agent, isActive, content, hasStarted }: { agent: any, isActive: boolean, content: string, hasStarted: boolean }) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [content])

  return (
    <div
      className={`card flex flex-col h-64 overflow-hidden transition-all duration-300 ${
        isActive ? 'ring-2 ring-secondary shadow-focus' : ''
      } ${!hasStarted && !isActive ? 'opacity-60' : ''}`}
    >
      <div className="p-3 border-b border-outline-variant bg-surface-container-low flex items-center gap-2">
        <span className={`material-symbols-outlined text-[18px] ${isActive ? 'text-secondary animate-pulse' : 'text-on-surface-variant'}`}>
          {agent.icon}
        </span>
        <span className="font-label-caps text-on-surface-variant">{agent.label}</span>
      </div>
      <div 
        ref={scrollRef}
        className="p-3 flex-1 overflow-y-auto bg-surface-container-lowest font-mono text-[11px] leading-relaxed text-on-surface-variant whitespace-pre-wrap"
      >
        {content}
        {isActive && <span className="streaming-cursor"></span>}
        {!hasStarted && !isActive && <span className="italic opacity-50">Waiting...</span>}
      </div>
    </div>
  )
}

export default function StreamOutput({ tokens, currentAgent }: StreamOutputProps) {
  const agents = [
    { id: 'supervisor', label: 'JD Analysis', icon: 'analytics' },
    { id: 'research', label: 'Company Research', icon: 'travel_explore' },
    { id: 'resume', label: 'Resume Tailoring', icon: 'edit_document' },
    { id: 'cover_letter', label: 'Cover Letter', icon: 'mail' },
    { id: 'interview_prep', label: 'Interview Prep', icon: 'record_voice_over' },
    { id: 'outreach', label: 'Outreach Strategy', icon: 'connect_without_contact' },
  ] as const

  return (
    <div className="w-full max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 animate-fade-in">
      {agents.map((agent) => {
        const isActive = currentAgent === agent.id
        const content = tokens[agent.id]
        const hasStarted = content.length > 0

        return (
          <AgentBox 
            key={agent.id} 
            agent={agent} 
            isActive={isActive} 
            content={content} 
            hasStarted={hasStarted} 
          />
        )
      })}
    </div>
  )
}
