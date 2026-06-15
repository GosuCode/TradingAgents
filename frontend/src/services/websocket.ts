export function connectAnalysisWS(taskId: string, onMessage: (msg: any) => void): WebSocket {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:"
  const ws = new WebSocket(`${protocol}//${location.host}/ws/analysis/${taskId}`)

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      onMessage(msg)
    } catch {
      // ignore parse errors
    }
  }

  ws.onerror = () => {
    onMessage({ type: "error", data: "WebSocket connection error" })
  }

  return ws
}
