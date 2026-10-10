// Генерация моковых данных для демонстрации

// Функция для генерации случайного числа в диапазоне
function randomInRange(min: number, max: number): number {
  return Math.random() * (max - min) + min
}

// Генерация моковых данных для графика и таблицы
export function generateMockData(timeframe: "hourly" | "daily"): any[] {
  const result = []
  const now = new Date()

  // Количество точек данных
  const historicalPoints = timeframe === "hourly" ? 168 : 30 // 7 дней или 30 дней
  const forecastPoints = timeframe === "hourly" ? 72 : 30 // 3 дня или 30 дней

  // Базовая цена
  const basePrice = 1250 // CZK/MWh

  // Генерация исторических данных
  for (let i = historicalPoints; i > 0; i--) {
    const date = new Date(now)
    if (timeframe === "hourly") {
      date.setHours(date.getHours() - i)
    } else {
      date.setDate(date.getDate() - i)
    }

    // Добавляем случайные колебания к базовой цене
    const price = basePrice + randomInRange(-200, 200)

    result.push({
      timestamp: date.toISOString(),
      price: price,
      isForecast: false,
    })
  }

  // Генерация прогнозных данных
  for (let i = 0; i < forecastPoints; i++) {
    const date = new Date(now)
    if (timeframe === "hourly") {
      date.setHours(date.getHours() + i)
    } else {
      date.setDate(date.getDate() + i)
    }

    // Последняя историческая цена
    const lastHistoricalPrice = result[result.length - 1].price

    // Добавляем тренд и случайные колебания
    const trend = 0.02 // Небольшой восходящий тренд
    const price = lastHistoricalPrice * (1 + trend) + randomInRange(-100, 100)

    result.push({
      timestamp: date.toISOString(),
      price: price,
      isForecast: true,
    })
  }

  return result
}

// Генерация моковых данных с доверительными интервалами
export function generateMockDataWithIntervals(timeframe: "hourly" | "daily"): any[] {
  const result = []
  const now = new Date()

  // Количество точек данных
  const historicalPoints = timeframe === "hourly" ? 168 : 30 // 7 дней или 30 дней
  const forecastPoints = timeframe === "hourly" ? 72 : 30 // 3 дня или 30 дней

  // Базовая цена
  const basePrice = 1250 // CZK/MWh

  // Генерация исторических данных
  for (let i = historicalPoints; i > 0; i--) {
    const date = new Date(now)
    if (timeframe === "hourly") {
      date.setHours(date.getHours() - i)
    } else {
      date.setDate(date.getDate() - i)
    }

    // Добавляем случайные колебания к базовой цене
    const price = basePrice + randomInRange(-200, 200)

    result.push({
      timestamp: date.toISOString(),
      price: price,
      isForecast: false,
      // Для исторических данных интервалы не нужны, но добавим их для совместимости
      lowerInterval: price,
      upperInterval: price,
    })
  }

  // Генерация прогнозных данных
  for (let i = 0; i < forecastPoints; i++) {
    const date = new Date(now)
    if (timeframe === "hourly") {
      date.setHours(date.getHours() + i)
    } else {
      date.setDate(date.getDate() + i)
    }

    // Последняя историческая цена
    const lastHistoricalPrice = result[result.length - 1].price

    // Добавляем тренд и случайные колебания
    const trend = 0.02 // Небольшой восходящий тренд
    const price = lastHistoricalPrice * (1 + trend) + randomInRange(-100, 100)

    // Увеличиваем неопределенность с увеличением горизонта прогноза
    const uncertaintyFactor = (0.05 * (i + 1)) / 10
    const lowerInterval = price * (1 - uncertaintyFactor)
    const upperInterval = price * (1 + uncertaintyFactor)

    result.push({
      timestamp: date.toISOString(),
      price: price,
      lowerInterval: lowerInterval,
      upperInterval: upperInterval,
      isForecast: true,
    })
  }

  return result
}
