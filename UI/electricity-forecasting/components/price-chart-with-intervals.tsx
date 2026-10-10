"use client"

import { format, differenceInMonths } from "date-fns"
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  ReferenceLine,
  ReferenceArea,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface PriceChartWithIntervalsProps {
  data: any[]
  timeframe: "hourly" | "daily"
  isLoading: boolean
}

export function PriceChartWithIntervals({ data, timeframe, isLoading }: PriceChartWithIntervalsProps) {
  if (isLoading) {
    return <Skeleton className="h-[500px] w-full" />
  }

  // Проверка на пустые данные
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Data Available</CardTitle>
          <CardDescription>There is no data to display for the selected period.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[500px] flex items-center justify-center text-muted-foreground">
            Please select a different date range or timeframe.
          </div>
        </CardContent>
      </Card>
    )
  }

  // Получаем сегодняшнюю дату (конец дня)
  const today = new Date()
  today.setHours(23, 59, 59, 999)

  // Получаем завтрашнюю дату (начало дня)
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(0, 0, 0, 0)

  // Строго разделяем исторические и прогнозные данные
  const historicalData = data.filter((d) => {
    const itemDate = new Date(d.timestamp)
    return itemDate <= today // Включаем сегодняшний день в исторические данные
  })

  const forecastData = data.filter((d) => {
    const itemDate = new Date(d.timestamp)
    return itemDate >= tomorrow // Только с завтрашнего дня
  })

  console.log(`Chart data: ${data.length} total, ${historicalData.length} historical, ${forecastData.length} forecast`)

  // Находим границу между историческими данными и прогнозом
  const boundaryDate = tomorrow.toISOString()

  // Рассчитываем интервал дат для определения оптимизации
  const calculateDateInterval = () => {
    if (data.length < 2) return 0

    const firstDate = new Date(data[0].timestamp)
    const lastDate = new Date(data[data.length - 1].timestamp)

    // Рассчитываем разницу в месяцах
    return differenceInMonths(lastDate, firstDate)
  }

  // Функция для оптимизации данных в зависимости от их количества
  const optimizeDataPoints = (dataArray: any[], threshold: number, skipFactor: number) => {
    if (dataArray.length <= threshold) {
      return dataArray // Если данных меньше порогового значения, возвращаем все данные
    }

    // Иначе фильтруем данные, оставляя каждую skipFactor-ую точку
    return dataArray.filter((_, index) => index % skipFactor === 0)
  }

  // Определяем параметры оптимизации в зависимости от типа временн��го интервала и интервала дат
  const getOptimizationParams = () => {
    const dateIntervalMonths = calculateDateInterval()
    console.log(`Date interval: ${dateIntervalMonths} months`)

    if (timeframe === "hourly") {
      // Оптимизация на основе интервала дат для часовых данных
      if (dateIntervalMonths > 6) {
        return { threshold: 100, skipFactor: 12 } // 2 точки в день (каждые 12 часов)
      }
      if (dateIntervalMonths > 4) {
        return { threshold: 100, skipFactor: 8 } // Каждые 8 часов
      }
      if (dateIntervalMonths > 2) {
        return { threshold: 100, skipFactor: 6 } // Каждые 6 часов
      }

      // Стандартная оптимизация на основе количества данных
      if (data.length > 300) return { threshold: 200, skipFactor: 4 } // Каждая 4-я точка
      if (data.length > 200) return { threshold: 150, skipFactor: 3 } // Каждая 3-я точка
      if (data.length > 100) return { threshold: 100, skipFactor: 2 } // Каждая 2-я точка
    } else {
      // Для дневных данных
      if (dateIntervalMonths > 6) {
        return { threshold: 60, skipFactor: 4 } // Каждые 4 дня
      }
      if (dateIntervalMonths > 4) {
        return { threshold: 60, skipFactor: 3 } // Каждые 3 дня
      }
      if (dateIntervalMonths > 2) {
        return { threshold: 60, skipFactor: 2 } // Каждые 2 дня
      }

      // Стандартная оптимизация
      if (data.length > 100) return { threshold: 60, skipFactor: 3 } // Каждая 3-я точка
      if (data.length > 60) return { threshold: 40, skipFactor: 2 } // Каждая 2-я точка
    }
    return { threshold: Number.POSITIVE_INFINITY, skipFactor: 1 } // По умолчанию все точки
  }

  const { threshold, skipFactor } = getOptimizationParams()

  // Оптимизируем данные для отображения
  const optimizedHistoricalData = optimizeDataPoints(historicalData, threshold, skipFactor)
  const optimizedForecastData = optimizeDataPoints(forecastData, threshold, skipFactor)

  console.log(
    `Optimized data: ${optimizedHistoricalData.length} historical, ${optimizedForecastData.length} forecast (skip factor: ${skipFactor})`,
  )

  // Объединяем оптимизированные данные
  const optimizedData = [...optimizedHistoricalData, ...optimizedForecastData]

  // Определяем интервал для меток оси X в зависимости от количества данных и типа временного интервала
  const calculateXAxisInterval = () => {
    if (timeframe === "hourly") {
      if (optimizedData.length > 100) return 12 // Каждые 12 часов для большого количества данных
      if (optimizedData.length > 50) return 6 // Каждые 6 часов для среднего количества данных
      return 3 // Каждые 3 часа для небольшого количества данных
    } else {
      // Для дневных данных
      if (optimizedData.length > 30) return 5 // Каждые 5 дней для большого количества данных
      if (optimizedData.length > 14) return 2 // Каждые 2 дня для среднего количества данных
      return 1 // Каждый день для небольшого количества данных
    }
  }

  const xAxisInterval = calculateXAxisInterval()

  // Date formatting function for X axis
  const formatXAxis = (timestamp: string) => {
    const date = new Date(timestamp)
    return timeframe === "hourly" ? format(date, "HH:mm dd/MM") : format(date, "dd MMM")
  }

  // Создаем комбинированный набор данных для графика
  const combinedData = optimizedData.map((item) => {
    const itemDate = new Date(item.timestamp)
    const isForecasted = itemDate >= tomorrow

    return {
      timestamp: item.timestamp,
      historicalPrice: itemDate <= today ? item.price : null,
      forecastPrice: isForecasted ? item.price : null,
      upperInterval: isForecasted && item.upperInterval ? item.upperInterval : null,
      lowerInterval: isForecasted && item.lowerInterval ? item.lowerInterval : null,
      // Преобразуем температуру в число или 0, если она не определена
      temperature: 0, // Временно устанавливаем 0 для всех точек
    }
  })

  // Создаем массив ReferenceArea для отображения интервалов
  const referenceAreas = optimizedForecastData
    .map((item, index) => {
      // Для каждой точки прогноза создаем ReferenceArea
      // от текущей точки до следующей точки по оси X
      // и от нижнего до верхнего интервала по оси Y
      const nextItem = optimizedForecastData[index + 1]
      if (!nextItem) return null // Пропускаем последнюю точку

      // Проверяем наличие интервалов
      if (
        item.lowerInterval === undefined ||
        item.upperInterval === undefined ||
        nextItem.lowerInterval === undefined ||
        nextItem.upperInterval === undefined
      ) {
        return null
      }

      return (
        <ReferenceArea
          key={item.timestamp}
          x1={item.timestamp}
          x2={nextItem.timestamp}
          y1={item.lowerInterval}
          y2={item.upperInterval}
          fill="#82ca9d"
          fillOpacity={0.2}
          ifOverflow="visible"
        />
      )
    })
    .filter(Boolean) // Удаляем null элементы

  // Функция для форматирования описания интервала оптимизации
  const getOptimizationDescription = () => {
    if (timeframe === "hourly") {
      if (skipFactor === 12) return "showing 2 points per day"
      if (skipFactor > 1) return `showing points every ${skipFactor} hours`
    } else {
      if (skipFactor > 1) return `showing points every ${skipFactor} days`
    }
    return ""
  }

  const optimizationDescription = getOptimizationDescription()

  return (
    <Card>
      <CardHeader>
        <CardTitle>{timeframe === "hourly" ? "Hourly" : "Daily"} Electricity Prices</CardTitle>
        <CardDescription>
          Historical data and price forecast with confidence intervals
          {optimizationDescription && ` (${optimizationDescription})`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={combinedData}
              margin={{ top: 5, right: 30, left: 30, bottom: 70 }} // Увеличиваем нижний отступ для легенды
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatXAxis}
                angle={-45}
                textAnchor="end"
                height={60}
                interval={xAxisInterval}
              />
              {/* Основная ось Y для цен */}
              <YAxis
                yAxisId="price"
                label={{
                  value: "Price (CZK/MWh)",
                  angle: -90,
                  position: "insideLeft", // Позиция подписи
                  offset: -15, // Смещение влево
                  dy: -30, // Смещение вниз
                  style: {
                    textAnchor: "middle", // Центрирование текста
                  },
                }}
              />
              <Tooltip
                formatter={(value, name) => {
                  if (value === null || value === undefined) return ["-", name]

                  if (name === "Upper Interval" || name === "Lower Interval") {
                    return [`${Number(value).toFixed(2)} CZK/MWh`, name]
                  }
                  if (name === "Historical Data") {
                    return [`${Number(value).toFixed(2)} CZK/MWh`, name]
                  }
                  if (name === "Forecast") {
                    return [`${Number(value).toFixed(2)} CZK/MWh`, name]
                  }
                  return [`${Number(value).toFixed(2)} CZK/MWh`, name]
                }}
                labelFormatter={(label) => format(new Date(label), "dd MMMM yyyy HH:mm")}
              />
              <Legend
                verticalAlign="bottom" // Размещаем легенду внизу
                height={36} // Высота области легенды
                wrapperStyle={{
                  bottom: -10, // Смещаем легенду вниз
                  paddingTop: 20, // Добавляем отступ сверху
                }}
              />

              {/* Вертикальная линия, разделяющая исторические данные и прогноз */}
              <ReferenceLine
                x={boundaryDate}
                stroke="#666"
                strokeDasharray="3 3"
                label={{ value: "Forecast Start", position: "top", fill: "#666" }}
              />

              {/* Области между верхним и нижним интервалами */}
              {referenceAreas}

              {/* Нижний интервал - отображаем только линию */}
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="lowerInterval"
                name="Lower Interval"
                stroke="#82ca9d"
                strokeWidth={1}
                strokeDasharray="3 3"
                dot={false}
                connectNulls
              />

              {/* Верхний интервал - отображаем только линию */}
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="upperInterval"
                name="Upper Interval"
                stroke="#82ca9d"
                strokeWidth={1}
                strokeDasharray="3 3"
                dot={false}
                connectNulls
              />

              {/* Исторические данные */}
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="historicalPrice"
                name="Historical Data"
                stroke="#8884d8"
                strokeWidth={2}
                dot={{ r: 1 }}
                activeDot={{ r: 6 }}
                connectNulls
              />

              {/* Прогноз - теперь без выколотых точек, как и исторические данные */}
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="forecastPrice"
                name="Forecast"
                stroke="#82ca9d"
                strokeWidth={2}
                dot={{ r: 1 }} // Маленькие точки, как у исторических данных
                activeDot={{ r: 6 }} // Активные точки при наведении
                connectNulls
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
