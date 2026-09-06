import { showSuccess, showError } from '@/utils/toast'

// Fetch the file and hand it to the OS share sheet, with a download fallback.
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
