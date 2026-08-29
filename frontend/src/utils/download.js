import { showSuccess, showError } from '@/utils/toast'

// window.open() relies on the browser's own download UI (progress bar, downloads
// tray, etc). That UI doesn't exist in an installed, standalone-mode PWA, so a
// PDF export can succeed with zero visible feedback to the user. This fetches
// the file ourselves and hands it to the OS share sheet (visible, works well on
// mobile) or falls back to a blob link click, always confirming with a toast.
export async function downloadFile(url, filename, mimeType = 'application/pdf') {
  let response
  try {
    response = await fetch(url, { credentials: 'same-origin' })
  } catch (error) {
    showError('Could not reach the server to generate the file')
    throw error
  }

  if (!response.ok) {
    let message = `Download failed (${response.status})`
    try {
      const data = await response.json()
      message = data?.exception || data?._server_messages || message
    } catch {
      // response wasn't JSON, keep the generic message
    }
    showError(message)
    throw new Error(message)
  }

  const blob = await response.blob()
  const file = new File([blob], filename, { type: mimeType })

  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title: filename })
      showSuccess('Ready to save or share')
      return
    } catch (error) {
      // User cancelled the share sheet - not an error, don't fall through to
      // the download link (that would fire a second, unwanted action).
      if (error?.name === 'AbortError') return
    }
  }

  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(objectUrl), 10000)
  showSuccess('Downloaded to your device')
}
