import React from 'react'

function DataTable({ visualisation }) {
  if (!visualisation || visualisation.type !== 'table') return null
  if (!visualisation.rows || visualisation.rows.length === 0) return null

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      overflowX: 'auto'
    }}>
      <h3 style={{
        fontSize: '15px',
        fontWeight: '600',
        marginBottom: '16px',
        color: '#2d3748'
      }}>
        {visualisation.title}
      </h3>

      <table style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: '13px'
      }}>
        <thead>
          <tr style={{ background: '#f7fafc' }}>
            {visualisation.columns.map((col, i) => (
              <th key={i} style={{
                padding: '10px 14px',
                textAlign: 'left',
                fontWeight: '600',
                color: '#4a5568',
                borderBottom: '2px solid #e2e8f0',
                whiteSpace: 'nowrap'
              }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {visualisation.rows.map((row, i) => (
            <tr key={i} style={{
              background: i % 2 === 0 ? 'white' : '#f7fafc'
            }}>
              {row.map((cell, j) => (
                <td key={j} style={{
                  padding: '10px 14px',
                  borderBottom: '1px solid #e2e8f0',
                  color: '#2d3748'
                }}>
                  {typeof cell === 'number' ? cell.toFixed(2) : cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable