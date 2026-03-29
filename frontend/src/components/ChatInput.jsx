import React from 'react'

function ChatInput({ onSubmit, loading }) {
  const [question, setQuestion] = React.useState('')

  function handleSubmit() {
    if (!question.trim() || loading) return
    onSubmit(question)
    setQuestion('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <div style={{
      display: 'flex',
      gap: '10px',
      padding: '20px',
      background: 'white',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <input
        type="text"
        value={question}
        onChange={e => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about the readmissions data..."
        disabled={loading}
        style={{
          flex: 1,
          padding: '12px 16px',
          fontSize: '15px',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          outline: 'none',
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          padding: '12px 24px',
          background: loading ? '#a0aec0' : '#3182ce',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '15px',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: '600'
        }}
      >
        {loading ? 'Thinking...' : 'Ask'}
      </button>
    </div>
  )
}

export default ChatInput