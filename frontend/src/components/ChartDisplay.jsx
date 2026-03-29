import React from 'react'
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts'

function ChartDisplay({ visualisation }) {
  if (!visualisation || visualisation.type === 'narrative') return null
  if (!visualisation.data || visualisation.data.length === 0) return null

  const data = visualisation.data

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <h3 style={{
        fontSize: '15px',
        fontWeight: '600',
        marginBottom: '20px',
        color: '#2d3748'
      }}>
        {visualisation.title}
      </h3>

      <ResponsiveContainer width="100%" height={350}>
        {visualisation.type === 'bar_chart' ? (
          <BarChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11 }}
              angle={-35}
              textAnchor="end"
              interval={0}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={{
                value: visualisation.y_label,
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 11 }
              }}
            />
            <Tooltip formatter={(val) => [val.toFixed(2), visualisation.y_label]} />
            <Bar dataKey="value" fill="#3182ce" radius={[4, 4, 0, 0]} />
          </BarChart>
        ) : visualisation.type === 'line_chart' ? (
          <LineChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11 }}
              angle={-25}
              textAnchor="end"
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={{
                value: visualisation.y_label,
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 11 }
              }}
            />
            <Tooltip formatter={(val) => [val.toFixed(2), visualisation.y_label]} />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#3182ce"
              strokeWidth={2}
              dot={{ fill: '#3182ce', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        ) : null}
      </ResponsiveContainer>
    </div>
  )
}

export default ChartDisplay