// FormattedText.jsx — Renders bot response text with basic formatting
// Handles paragraphs, bold text, numbered lists, and bullet points
// to make long responses scannable and professional-looking.

export default function FormattedText({ text }) {
  if (!text) return null

  // Split into paragraphs by double newlines
  const paragraphs = text.split(/\n\n+/)

  return (
    <div className="space-y-3">
      {paragraphs.map((paragraph, pIdx) => {
        const trimmed = paragraph.trim()
        if (!trimmed) return null

        // Check if this paragraph is a list (lines starting with - or numbers)
        const lines = trimmed.split('\n')
        const isBulletList = lines.every(l => /^\s*[-•]\s/.test(l) || !l.trim())
        const isNumberedList = lines.every(l => /^\s*\d+[.)]\s/.test(l) || !l.trim())

        if (isBulletList) {
          return (
            <ul key={pIdx} className="space-y-1.5 ml-1">
              {lines.filter(l => l.trim()).map((line, lIdx) => (
                <li key={lIdx} className="flex gap-2 items-start">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 flex-shrink-0" />
                  <span>{renderInlineFormatting(line.replace(/^\s*[-•]\s*/, ''))}</span>
                </li>
              ))}
            </ul>
          )
        }

        if (isNumberedList) {
          return (
            <ol key={pIdx} className="space-y-1.5 ml-1">
              {lines.filter(l => l.trim()).map((line, lIdx) => {
                const match = line.match(/^\s*(\d+)[.)]\s*(.*)/)
                return (
                  <li key={lIdx} className="flex gap-2.5 items-start">
                    <span className="text-emerald-600 font-semibold text-xs mt-0.5 w-5 flex-shrink-0 text-right">
                      {match ? match[1] : lIdx + 1}.
                    </span>
                    <span>{renderInlineFormatting(match ? match[2] : line)}</span>
                  </li>
                )
              })}
            </ol>
          )
        }

        // Regular paragraph — preserve single newlines within it
        return (
          <p key={pIdx} className="whitespace-pre-wrap">
            {renderInlineFormatting(trimmed)}
          </p>
        )
      })}
    </div>
  )
}

// Render **bold** and *italic* inline formatting
function renderInlineFormatting(text) {
  if (!text) return text

  const parts = []
  let remaining = text
  let key = 0

  while (remaining.length > 0) {
    // Match **bold**
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/)
    if (boldMatch) {
      const beforeBold = remaining.slice(0, boldMatch.index)
      if (beforeBold) parts.push(beforeBold)
      parts.push(
        <strong key={key++} className="font-semibold text-slate-900">
          {boldMatch[1]}
        </strong>
      )
      remaining = remaining.slice(boldMatch.index + boldMatch[0].length)
      continue
    }

    // No more formatting found
    parts.push(remaining)
    break
  }

  return parts.length === 1 && typeof parts[0] === 'string' ? parts[0] : parts
}
