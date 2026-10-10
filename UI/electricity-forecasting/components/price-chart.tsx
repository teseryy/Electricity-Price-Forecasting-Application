"use client"

import { format } from "date-fns"
import { enUS } from "date-fns/locale"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface PriceChartProps {
  data: any[]
  timeframe: "hourly" | "daily"
  isLoading: boolean
}

export function PriceChart({ data, timeframe, isLoading }: PriceChartProps) {
  if (isLoading) {
    return <Skeleton className="h-[400px] w-full" />
  }

  // Функция форматирования даты для оси X
  const formatXAxis = (timestamp: string) => {
    const date = new Date(timestamp)
    return timeframe === "hourly"
      ? format(date, "HH:mm dd.MM", { locale: enUS })
      : format(date, "dd MMM", { locale: enUS })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{timeframe === "hourly" ? "Часовые цены" : "Дневные цены"} на электричество</CardTitle>
        <CardDescription>Исторические данные и прогноз цен на выбранный период</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tickFormatter={formatXAxis} angle={-45} textAnchor="end" height={60} />
              <YAxis
                label={{
                  value: "Цена (руб/кВт⋅ч)",
                  angle: -90,
                  position: "insideLeft",
                }}
              />
              <Tooltip
                formatter={(value) => [`${Number(value).toFixed(2)} руб/кВт⋅ч`, "Цена"]}
                labelFormatter={(label) => format(new Date(label), "dd MMMM yyyy HH:mm", { locale: enUS })}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="price"
                name="Исторические данные"
                stroke="#8884d8"
                activeDot={{ r: 8 }}
                connectNulls
                hide={(d) => d.isForecast}
              />
              <Line
                type="monotone"
                dataKey="price"
                name="Прогноз"
                stroke="#82ca9d"
                strokeDasharray="5 5"
                connectNulls
                hide={(d) => !d.isForecast}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
