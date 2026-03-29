import React, { useState } from 'react'
import ChatInput from './components/ChatInput'
import AnswerCard from './components/AnswerCard'
import ChartDisplay from './components/ChartDisplay'
import DataTable from './components/DataTable'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])

  async function handleQuestion(question) {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post(`${API_BASE}/ask`, {
        question: question,
        client_id: 'client001'
      })

      const data = response.data

      setHistory(prev => [{
        question,
        result: data,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev])

      setResult(data)

    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '32px 20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px'
    }}>
      <div>
        <h1 style={{ fontSize: '24px', color: '#1a202c' }}>
          NHS Readmissions Analytics
        </h1>
        <p style={{ color: '#718096', marginTop: '4px' }}>
          Ask questions about the readmissions dataset in plain English
        </p>
      </div>

      <ChatInput onSubmit={handleQuestion} loading={loading} />

      {loading && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: '#718096',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
        }}>
          Analysing your question...
        </div>
      )}

      {error && (
        <div style={{
          padding: '16px',
          background: '#fff5f5',
          border: '1px solid #fed7d7',
          borderRadius: '12px',
          color: '#c53030'
        }}>
          {error}
        </div>
      )}

      {result && (
        <>
          <ChartDisplay visualisation={result.visualisation} />
          <DataTable visualisation={result.visualisation} />
          <AnswerCard
            answer={result.answer}
            sqlGenerated={result.sql_generated}
            rowsReturned={result.rows_returned}
          />
        </>
      )}

      {history.length > 1 && (
        <div>
          <h2 style={{
            fontSize: '14px',
            color: '#718096',
            marginBottom: '10px'
          }}>
            Previous questions
          </h2>
          {history.slice(1).map((item, i) => (
            <div
              key={i}
              onClick={() => setResult(item.result)}
              style={{
                padding: '12px 16px',
                background: 'white',
                borderRadius: '8px',
                marginBottom: '8px',
                cursor: 'pointer',
                boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <span style={{ fontSize: '14px' }}>{item.question}</span>
              <span style={{ fontSize: '12px', color: '#a0aec0' }}>
                {item.timestamp}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App