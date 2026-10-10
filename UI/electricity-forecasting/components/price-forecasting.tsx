"use client"

import { useState, useEffect } from "react"
import { PriceChart } from "@/components/price-chart"
import { PriceTable } from "@/components/price-table"
import { generateMockData } from "@/lib/mock-data"

interface PriceForecastingProps {
  timeframe: "hourly" | "daily"
}

export function PriceForecasting({ timeframe }: PriceForecastingProps) {
  const [data, setData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Имитация загрузки данных
    setIsLoading(true)

    // Задержка для имитации загрузки
    const timer = setTimeout(() => {
      // Генерируем моковые данные
      const mockData = generateMockData(timeframe)
      setData(mockData)
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [timeframe])

  return (
    <div className="space-y-8">
      <PriceChart data={data} timeframe={timeframe} isLoading={isLoading} />

      <div>
        <h2 className="text-xl font-semibold mb-4">Прогноз цен на электричество</h2>
        <PriceTable data={data.filter((item) => item.isForecast)} timeframe={timeframe} isLoading={isLoading} />
      </div>
    </div>
  )
}
