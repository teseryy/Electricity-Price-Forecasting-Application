import { type NextRequest, NextResponse } from "next/server"

// API-маршрут для проксирования запросов к серверу прогнозирования
export async function GET(request: NextRequest) {
  try {
    // Получаем параметры запроса
    const url = request.nextUrl.searchParams.get("url") || ""

    // В продакшн используем внутреннее имя Docker-сети, в разработке - localhost
    const API_URL =
      process.env.API_URL || (process.env.NODE_ENV === "production" ? "http://fastapi:8010" : "http://localhost:8000")

    // Получаем все остальные параметры запроса
    const params = new URLSearchParams()
    for (const [key, value] of request.nextUrl.searchParams.entries()) {
      if (key !== "url") {
        params.append(key, value)
      }
    }

    // Формируем URL для запроса к серверу
    // Убедимся, что URL начинается с /forecast
    const endpoint = url.startsWith("/forecast") ? url : `/forecast${url}`
    const fullUrl = `${API_URL}${endpoint}${params.toString() ? `?${params.toString()}` : ""}`

    console.log(`[API] Proxying GET request to: ${fullUrl}`)

    // Отправляем запрос к серверу
    const response = await fetch(fullUrl)

    console.log(`[API] Server response status: ${response.status}`)

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`[API] Server error: ${response.status}`, errorText)
      return NextResponse.json(
        { error: `Server responded with status: ${response.status}` },
        { status: response.status },
      )
    }

    const data = await response.json()
    console.log(`[API] Server response data length: ${data.length || 0}`)

    return NextResponse.json(data)
  } catch (error) {
    console.error("[API] Error processing request:", error)
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}
