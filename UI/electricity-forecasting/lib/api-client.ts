// Определяем, находимся ли мы в режиме разработки
const isDevelopment = process.env.NODE_ENV === "development"

// Базовый URL API - ВСЕГДА используем прокси для обхода CORS
const API_BASE_URL = "/api/forecast/proxy"

// Интерфейсы для типизации данных
export interface HistoricalDataPoint {
  timestamp: string
  price: number
  temperature: number
  isForecast: boolean
}

export interface ForecastDataPoint {
  timestamp: string
  price: number
  temperature: number
  lowerInterval: number
  upperInterval: number
  isForecast: boolean
}

// Получение исторических данных (до сегодняшнего дня включительно)
export async function fetchHistoricalData(
  from: string,
  to: string,
  timeframe: "hourly" | "daily",
): Promise<HistoricalDataPoint[]> {
  try {
    console.log(`Fetching historical data: from=${from}, to=${to}, timeframe=${timeframe}`)

    // Для исторических данных используем GET с параметрами в URL
    const endpoint = `/forecast/${timeframe === "hourly" ? "hourly" : "daily"}/oldData`

    // Формируем URL для запроса к API через прокси
    const url = `${API_BASE_URL}?url=${encodeURIComponent(endpoint)}&start_date=${from}&end_date=${to}`

    console.log(`Historical data request: ${url}`)

    const response = await fetch(url)

    console.log(`Historical data response status: ${response.status}`)

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`Historical data error: Status ${response.status}, Response:`, errorText)
      throw new Error(`HTTP error! Status: ${response.status}, Response: ${errorText}`)
    }

    const data = await response.json()
    console.log(`Historical data received: ${data.length} items`)
    if (data.length > 0) {
      console.log(`Sample historical data:`, data[0])
    }

    // Преобразуем данные в нужный формат
    return data.map((item: any) => ({
      timestamp: item.date || item.timestamp,
      price: item.price,
      temperature: item.temperature || 0,
      isForecast: false,
    }))
  } catch (error) {
    console.error("Error fetching historical data:", error)
    throw error // Пробрасываем ошибку дальше
  }
}

// Получение прогнозных данных (начиная с завтрашнего дня)
export async function fetchForecastData(timeframe: "hourly" | "daily"): Promise<ForecastDataPoint[]> {
  try {
    console.log(`Fetching forecast data: timeframe=${timeframe}`)

    const endpoint = `/forecast/${timeframe === "hourly" ? "hourly" : "daily"}`

    // Формируем URL для запроса к API через прокси
    const url = `${API_BASE_URL}?url=${encodeURIComponent(endpoint)}`

    console.log(`Forecast data request: ${url}`)

    const response = await fetch(url)

    console.log(`Forecast data response status: ${response.status}`)

    if (!response.ok) {
      const errorText = await response.text()
      console.error(`Forecast data error: Status ${response.status}, Response:`, errorText)
      throw new Error(`HTTP error! Status: ${response.status}, Response: ${errorText}`)
    }

    const data = await response.json()
    console.log(`Forecast data received: ${data.length} items`)
    if (data.length > 0) {
      console.log(`Sample forecast data:`, data[0])
    }

    // Преобразуем данные в нужный формат
    return data.map((item: any) => ({
      timestamp: item.date || item.timestamp,
      price: item.price,
      temperature: item.temperature || 0,
      lowerInterval: item.lower_bound || item.lowerInterval,
      upperInterval: item.upper_bound || item.upperInterval,
      isForecast: true,
    }))
  } catch (error) {
    console.error("Error fetching forecast data:", error)
    throw error // Пробрасываем ошибку дальше
  }
}

// Получение всех данных (исторические + прогноз)
export async function fetchAllData(from: string, to: string, timeframe: "hourly" | "daily"): Promise<any[]> {
  try {
    console.log(`Fetching all data: from=${from}, to=${to}, timeframe=${timeframe}`)

    // Разделяем запросы на исторические и прогнозные данные
    const today = new Date()
    today.setHours(23, 59, 59, 999) // Конец текущего дня

    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(0, 0, 0, 0) // Начало следующего дня

    // Форматируем даты для API
    const todayStr = today.toISOString().split("T")[0]
    console.log(`Today: ${todayStr}, Tomorrow: ${tomorrow.toISOString().split("T")[0]}`)

    // Получаем исторические данные до сегодняшнего дня включительно
    const historical = await fetchHistoricalData(from, todayStr, timeframe)
    console.log(`Historical data count: ${historical.length}`)

    // Получаем прогнозные данные
    const forecast = await fetchForecastData(timeframe)
    console.log(`Forecast data count: ${forecast.length}`)

    // Преобразуем строку даты "to" в объект Date и устанавливаем время на конец дня
    const toDate = new Date(to)
    toDate.setHours(23, 59, 59, 999) // Конец дня для даты "to"

    console.log(`To date (end of day): ${toDate.toISOString()}`)

    // Фильтруем прогнозные данные, чтобы включить только те,
    // которые находятся в запрошенном диапазоне дат и начинаются с завтрашнего дня
    const filteredForecast = forecast.filter((item) => {
      const itemDate = new Date(item.timestamp)
      const fromDate = new Date(from)

      // Проверяем, что дата прогноза не раньше завтрашнего дня
      // и находится в запрошенном диапазоне (до конца дня даты "to")
      return itemDate >= tomorrow && itemDate >= fromDate && itemDate <= toDate
    })

    console.log(`Filtered forecast data count: ${filteredForecast.length}`)
    console.log(
      `First forecast date: ${filteredForecast.length > 0 ? new Date(filteredForecast[0].timestamp).toISOString() : "none"}`,
    )
    console.log(
      `Last forecast date: ${filteredForecast.length > 0 ? new Date(filteredForecast[filteredForecast.length - 1].timestamp).toISOString() : "none"}`,
    )

    // Явно помечаем все прогнозные данные
    const markedForecast = filteredForecast.map((item) => ({
      ...item,
      isForecast: true,
    }))

    const allData = [...historical, ...markedForecast]
    console.log(`Total data count: ${allData.length}`)

    // Сортируем данные по дате и времени
    allData.sort((a, b) => {
      const dateA = new Date(a.timestamp).getTime()
      const dateB = new Date(b.timestamp).getTime()
      return dateA - dateB
    })

    return allData
  } catch (error) {
    console.error("Error fetching all data:", error)
    throw error // Пробрасываем ошибку дальше
  }
}
