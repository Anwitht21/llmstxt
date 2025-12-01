import { NextResponse } from 'next/server'

export async function POST() {
  const backendUrl = process.env.BACKEND_URL || 'https://llmstxt-backend.leap-cc.com'
  const apiKey = process.env.API_KEY

  if (!apiKey) {
    return NextResponse.json({ error: 'Server configuration error' }, { status: 500 })
  }

  try {
    const response = await fetch(`${backendUrl}/auth/token`, {
      method: 'POST',
      headers: {
        'x-api-key': apiKey
      }
    })

    if (!response.ok) {
      return NextResponse.json({ error: 'Authentication failed' }, { status: 401 })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to get token' }, { status: 500 })
  }
}
