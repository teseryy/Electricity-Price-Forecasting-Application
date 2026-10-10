// Функции для работы с API сервера прогнозирования

// Базовый URL API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.example.com"

// Получение исторических данных
export async function fetchHistoricalData(
  fromDate: string,
  toDate: string,
  timeframe: "hourly" | "daily",
): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/historical?from=${fromDate}&to=${toDate}&timeframe=${timeframe}`)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()

    // Добавляем флаг, что это исторические данные
    return data.map((item: any) => ({
      ...item,
      isForecast: false,
    }))
  } catch (error) {
    console.error("Error fetching historical data:", error)
    throw error
  }
}

// Получение прогнозных данных
export async function fetchForecastData(
  fromDate: string,
  toDate: string,
  timeframe: "hourly" | "daily",
): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/forecast?from=${fromDate}&to=${toDate}&timeframe=${timeframe}`)

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    const data = await response.json()

    // Добавляем флаг, что это прогнозные данные
    return data.map((item: any) => ({
      ...item,
      isForecast: true,
    }))
  } catch (error) {
    console.error("Error fetching forecast data:", error)
    throw error
  }
}
