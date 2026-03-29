import React from 'react'
import ReactMarkdown from 'react-markdown'

function AnswerCard({ answer, sqlGenerated, rowsReturned }) {
  const [showSql, setShowSql] = React.useState(false)

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <div style={{
        fontSize: '13px',
        color: '#718096',
        marginBottom: '12px'
      }}>
        {rowsReturned} rows analysed
      </div>

      <div style={{ fontSize: '15px', lineHeight: '1.7' }}>
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>

      <div style={{ marginTop: '16px' }}>
        <button
          onClick={() => setShowSql(!showSql)}
          style={{
            background: 'none',
            border: '1px solid #e2e8f0',
            borderRadius: '6px',
            padding: '4px 12px',
            fontSize: '12px',
            color: '#718096',
            cursor: 'pointer'
          }}
        >
          {showSql ? 'Hide SQL' : 'Show SQL'}
        </button>

        {showSql && (
          <pre style={{
            marginTop: '10px',
            padding: '12px',
            background: '#f7fafc',
            borderRadius: '8px',
            fontSize: '12px',
            overflowX: 'auto',
            color: '#2d3748'
          }}>
            {sqlGenerated}
          </pre>
        )}
      </div>
    </div>
  )
}

export default AnswerCard