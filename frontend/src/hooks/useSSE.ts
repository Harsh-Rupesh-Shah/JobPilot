/**
 * hooks/useSSE.ts
 * Manages a Server-Sent Events connection to /stream/{runId}.
 * Demultiplexes events by agent name into per-agent token streams.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { openSSEStream } from '../api/client'

// ── Types ─────────────────────────────────────────────────────────────────

export interface AgentTokens {
  research: string
  resume: string
  cover_letter: string
  interview_prep: string
  outreach: string
}

export type AgentName = keyof AgentTokens

interface SSEEvent {
  agent?: AgentName
  token?: string
  event?: 'interrupt' | 'complete' | 'error'
  message?: string
  outputs?: Record<string, string>
}

interface UseSSEReturn {
  agentTokens: AgentTokens
  interruptPayload: SSEEvent | null
  isConnected: boolean
  isComplete: boolean
  error: string | null
  reset: () => void
}

const INITIAL_TOKENS: AgentTokens = {
  research:      '',
  resume:        '',
  cover_letter:  '',
  interview_prep:'',
  outreach:      '',
}

// ── Hook ──────────────────────────────────────────────────────────────────

/**
 * Opens an SSE connection to /stream/{runId}.
 * Pass null to skip connecting (e.g. no active run).
 */
export function useSSE(runId: string | null): UseSSEReturn {
  const [agentTokens, setAgentTokens] = useState<AgentTokens>(INITIAL_TOKENS)
  const [interruptPayload, setInterruptPayload] = useState<SSEEvent | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const esRef = useRef<EventSource | null>(null)

  const reset = useCallback(() => {
    setAgentTokens(INITIAL_TOKENS)
    setInterruptPayload(null)
    setIsConnected(false)
    setIsComplete(false)
    setError(null)
  }, [])

  useEffect(() => {
    if (!runId) return

    const es = openSSEStream(runId)
    esRef.current = es

    es.onopen = () => setIsConnected(true)

    es.onmessage = (event: MessageEvent<string>) => {
      try {
        const data = JSON.parse(event.data) as SSEEvent

        if (data.event === 'interrupt') {
          setInterruptPayload(data)
          setIsComplete(false)
          es.close()
          setIsConnected(false)
          return
        }

        if (data.event === 'complete') {
          setIsComplete(true)
          es.close()
          setIsConnected(false)
          return
        }

        if (data.event === 'error') {
          setError(data.message ?? 'An unknown error occurred')
          es.close()
          setIsConnected(false)
          return
        }

        // Normal token event
        if (data.agent && data.token) {
          setAgentTokens((prev) => ({
            ...prev,
            [data.agent as AgentName]: prev[data.agent as AgentName] + data.token,
          }))
        }
      } catch {
        // Ignore malformed events
      }
    }

    es.onerror = () => {
      setError('Connection to server lost. Please refresh.')
      setIsConnected(false)
      es.close()
    }

    return () => {
      es.close()
      esRef.current = null
    }
  }, [runId])

  return { agentTokens, interruptPayload, isConnected, isComplete, error, reset }
}
