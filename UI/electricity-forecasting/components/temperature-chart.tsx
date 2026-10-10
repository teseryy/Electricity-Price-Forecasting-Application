"use client"

import { format } from "date-fns"
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface TemperatureChartProps {
  data: any[]
  timeframe: "hourly" | "daily"
  isLoading: boolean
}

export function TemperatureChart({ data, timeframe, isLoading }: TemperatureChartProps) {
  if (isLoading) {
    return <Skeleton className="h-[300px] w-full" />
  }

  // Проверка на пустые данные
  if (!data || data.length === 0) {
    return null
  }

  // Проверяем наличие данных о температуре
  const hasTemperatureData = data.some(
    (item) => item.temperature !== undefined && item.temperature !== null && item.temperature !== 0,
  )

  if (!hasTemperatureData) {
    return null
  }

  // Функция для оптимизации данных в зависимости от их количества
  const optimizeDataPoints = (dataArray: any[], threshold: number, skipFactor: number) => {
    if (dataArray.length <= threshold) {
      return dataArray // Если данных меньше порогового значения, возвращаем все данные
    }

    // Иначе фильтруем данные, оставляя каждую skipFactor-ую точку
    return dataArray.filter((_, index) => index % skipFactor === 0)
  }

  // Определяем параметры оптимизации
  const getOptimizationParams = () => {
    if (timeframe === "hourly") {
      if (data.length > 300) return { threshold: 200, skipFactor: 4 }
      if (data.length > 200) return { threshold: 150, skipFactor: 3 }
      if (data.length > 100) return { threshold: 100, skipFactor: 2 }
    } else {
      if (data.length > 100) return { threshold: 60, skipFactor: 3 }
      if (data.length > 60) return { threshold: 40, skipFactor: 2 }
    }
    return { threshold: Number.POSITIVE_INFINITY, skipFactor: 1 }
  }

  const { threshold, skipFactor } = getOptimizationParams()

  // Оптимизируем данные для отображения
  const optimizedData = optimizeDataPoints(data, threshold, skipFactor)

  // Создаем набор данных для графика
  const chartData = optimizedData.map((item) => ({
    timestamp: item.timestamp,
    temperature: typeof item.temperature === "number" ? item.temperature : null,
  }))

  // Определяем интервал для меток оси X
  const calculateXAxisInterval = () => {
    if (timeframe === "hourly") {
      if (optimizedData.length > 100) return 12
      if (optimizedData.length > 50) return 6
      return 3
    } else {
      if (optimizedData.length > 30) return 5
      if (optimizedData.length > 14) return 2
      return 1
    }
  }

  const xAxisInterval = calculateXAxisInterval()

  // Форматирование даты для оси X
  const formatXAxis = (timestamp: string) => {
    const date = new Date(timestamp)
    return timeframe === "hourly" ? format(date, "HH:mm dd/MM") : format(date, "dd MMM")
  }

  // Находим минимальное и максимальное значение температуры
  const temperatures = chartData
    .map((item) => item.temperature)
    .filter((temp): temp is number => temp !== null && typeof temp === "number")

  let minTemperature = 0
  let maxTemperature = 30

  if (temperatures.length > 0) {
    minTemperature = Math.min(...temperatures)
    maxTemperature = Math.max(...temperatures)

    // Защита от одинаковых значений
    if (minTemperature === maxTemperature) {
      minTemperature -= 5
      maxTemperature += 5
    }
  }

  // Округляем значения для более красивого отображения шкалы
  const yAxisMinTemperature = Math.floor(minTemperature - 2)
  const yAxisMaxTemperature = Math.ceil(maxTemperature + 2)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Temperature</CardTitle>
        <CardDescription>Temperature data for the selected period</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatXAxis}
                angle={-45}
                textAnchor="end"
                height={60}
                interval={xAxisInterval}
              />
              <YAxis
                domain={[yAxisMinTemperature, yAxisMaxTemperature]}
                label={{
                  value: "Temperature (°C)",
                  angle: -90,
                  position: "insideLeft",
                  style: {
                    textAnchor: "middle",
                  },
                }}
              />
              <Tooltip
                formatter={(value) => [`${Number(value).toFixed(1)} °C`, "Temperature"]}
                labelFormatter={(label) => format(new Date(label), "dd MMMM yyyy HH:mm")}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="temperature"
                name="Temperature"
                stroke="#ff5252"
                strokeWidth={2}
                dot={{ r: 1 }}
                activeDot={{ r: 6 }}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
