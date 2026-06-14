/**
 * hooks/useApplication.ts
 * Manages run lifecycle: start, poll status, approve.
 * Polls GET /status/{run_id} every 2 seconds while status is 'running'.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { runApi, type RunStatusResponse } from '../api/client'

// ── Types ─────────────────────────────────────────────────────────────────

interface UseApplicationReturn {
  runId: string | null
  status: RunStatusResponse | null
  isPolling: boolean
  error: string | null
  startRun: (jobUrl: string | undefined, jobDescription: string | undefined, resumeId: string) => Promise<string>
  approve: (edited: { tailored_resume: string; cover_letter: string; outreach_draft: string }) => Promise<void>
  reset: () => void
}

const POLL_INTERVAL_MS = 2000

// ── Hook ──────────────────────────────────────────────────────────────────

export function useApplication(): UseApplicationReturn {
  const [runId, setRunId] = useState<string | null>(null)
  const [status, setStatus] = useState<RunStatusResponse | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // ── Stop polling ────────────────────────────────────────────────────────

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current)
      pollTimerRef.current = null
    }
    setIsPolling(false)
  }, [])

  // ── Polling logic ───────────────────────────────────────────────────────

  useEffect(() => {
    if (!runId || !isPolling) return

    const tick = async () => {
      try {
        const s = await runApi.status(runId)
        setStatus(s)
        // Stop polling when graph pauses (interrupt) or terminal state
        if (s.status !== 'running') {
          stopPolling()
        }
      } catch (err) {
        setError('Failed to fetch run status')
        stopPolling()
      }
    }

    // Poll immediately then repeat
    void tick()
    pollTimerRef.current = setInterval(tick, POLL_INTERVAL_MS)

    return stopPolling
  }, [runId, isPolling, stopPolling])

  // ── Actions ─────────────────────────────────────────────────────────────

  const startRun = useCallback(
    async (
      jobUrl: string | undefined,
      jobDescription: string | undefined,
      resumeId: string,
    ): Promise<string> => {
      setError(null)
      const { run_id } = await runApi.start({ job_url: jobUrl, job_description: jobDescription, resume_id: resumeId })
      setRunId(run_id)
      setStatus(null)
      setIsPolling(true)
      return run_id
    },
    [],
  )

  const approve = useCallback(
    async (edited: { tailored_resume: string; cover_letter: string; outreach_draft: string }): Promise<void> => {
      if (!runId) throw new Error('No active run')
      await runApi.approve(runId, edited)
      setIsPolling(true) // Resume polling until 'complete'
    },
    [runId],
  )

  const reset = useCallback(() => {
    stopPolling()
    setRunId(null)
    setStatus(null)
    setError(null)
  }, [stopPolling])

  return { runId, status, isPolling, error, startRun, approve, reset }
}
