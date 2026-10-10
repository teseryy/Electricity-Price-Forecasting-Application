"use client"

import { useState, useEffect } from "react"
import { PriceChartWithIntervals } from "@/components/price-chart-with-intervals"
import { TemperatureChart } from "@/components/temperature-chart"
import { PriceTable } from "@/components/price-table"
import { fetchAllData } from "@/lib/api-client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { LoadingSpinner } from "@/components/loading-spinner"

interface ForecastResultsProps {
  from: string
  to: string
  timeframe: "hourly" | "daily"
}

export function ForecastResults({ from, to, timeframe }: ForecastResultsProps) {
  const [data, setData] = useState<any[]>([])
  const [forecastData, setForecastData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadData = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Пытаемся получить реальные данные
      console.log("[UI] Fetching real data")
      const allData = await fetchAllData(from, to, timeframe)
      console.log(`[UI] Real data received: ${allData.length} items`)

      if (allData.length === 0) {
        setError("No data received from the server")
      } else {
        // Получаем завтрашнюю дату (начало дня)
        const tomorrow = new Date()
        tomorrow.setDate(tomorrow.getDate() + 1)
        tomorrow.setHours(0, 0, 0, 0)

        // Фильтруем только прогнозные данные для таблицы
        const forecast = allData.filter((item) => item.isForecast)

        console.log(`[UI] Forecast data: ${forecast.length} items`)
        if (forecast.length > 0) {
          console.log(`[UI] First forecast date: ${new Date(forecast[0].timestamp).toISOString()}`)
          console.log(`[UI] Last forecast date: ${new Date(forecast[forecast.length - 1].timestamp).toISOString()}`)
        }

        setData(allData)
        setForecastData(forecast)
      }
    } catch (err: any) {
      console.error("[UI] Error loading data:", err)
      setError(err.message || "An error occurred while loading data. Please try again later.")
    } finally {
      setIsLoading(false)
      console.log("[UI] Loading completed")
    }
  }

  useEffect(() => {
    loadData()
  }, [from, to, timeframe])

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-8">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <Button variant="outline" size="sm" onClick={loadData} className="ml-4">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {data.length === 0 && !isLoading && !error ? (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No Data</AlertTitle>
          <AlertDescription>
            No data available for the selected period. Please try a different date range.
          </AlertDescription>
        </Alert>
      ) : (
        <>
          <PriceChartWithIntervals data={data} timeframe={timeframe} isLoading={isLoading} />

          <TemperatureChart data={data} timeframe={timeframe} isLoading={isLoading} />

          <div>
            <h2 className="text-xl font-semibold mb-4">Electricity Price Forecast</h2>
            <PriceTable data={forecastData} timeframe={timeframe} isLoading={isLoading} showIntervals={true} />
          </div>
        </>
      )}
    </div>
  )
}
