"use client"

import { useState } from "react"
import { format } from "date-fns"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface PriceTableProps {
  data: any[]
  timeframe: "hourly" | "daily"
  isLoading: boolean
  showIntervals?: boolean
}

export function PriceTable({ data, timeframe, isLoading, showIntervals = false }: PriceTableProps) {
  // Состояние для пагинации
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 50

  // Вычисляем общее количество страниц
  const totalPages = Math.max(1, Math.ceil(data.length / itemsPerPage))

  // Вычисляем индексы для текущей страницы
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = Math.min(startIndex + itemsPerPage, data.length)

  // Получаем данные для текущей страницы
  const currentPageData = data.slice(startIndex, endIndex)

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (!data.length) {
    return <p className="text-center py-4">No data to display</p>
  }

  // Date formatting based on timeframe
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    return timeframe === "hourly" ? format(date, "dd/MM/yyyy HH:mm") : format(date, "dd/MM/yyyy")
  }

  // Функция для перехода на предыдущую страницу
  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  // Функция для перехода на следующую страницу
  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  return (
    <div className="space-y-4">
      <Table>
        <TableCaption>Electricity price forecast for the selected period</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Date{timeframe === "hourly" ? " & Time" : ""}</TableHead>
            <TableHead>Price (CZK/MWh)</TableHead>
            {showIntervals && (
              <>
                <TableHead>Lower Bound</TableHead>
                <TableHead>Upper Bound</TableHead>
              </>
            )}
            <TableHead>Temperature (°C)</TableHead>
            <TableHead>Change</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {currentPageData.map((item, index) => {
            // Calculate price change compared to previous period
            const prevPrice = index > 0 ? currentPageData[index - 1].price : null
            const priceChange = prevPrice !== null ? ((item.price - prevPrice) / prevPrice) * 100 : 0

            return (
              <TableRow key={item.timestamp}>
                <TableCell>{formatDate(item.timestamp)}</TableCell>
                <TableCell>{Number(item.price).toFixed(2)}</TableCell>
                {showIntervals && (
                  <>
                    <TableCell>{Number(item.lowerInterval).toFixed(2)}</TableCell>
                    <TableCell>{Number(item.upperInterval).toFixed(2)}</TableCell>
                  </>
                )}
                <TableCell>{item.temperature}°C</TableCell>
                <TableCell className={priceChange > 0 ? "text-green-600" : priceChange < 0 ? "text-red-600" : ""}>
                  {priceChange !== 0 && (
                    <>
                      {priceChange > 0 ? "+" : ""}
                      {priceChange.toFixed(2)}%
                    </>
                  )}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>

      {/* Простая пагинация */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t pt-4">
          <div className="text-sm text-muted-foreground">
            Showing {startIndex + 1} to {endIndex} of {data.length} entries
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={goToPreviousPage} disabled={currentPage === 1} size="sm">
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <span className="text-sm font-medium">
              Page {currentPage} of {totalPages}
            </span>
            <Button variant="outline" onClick={goToNextPage} disabled={currentPage === totalPages} size="sm">
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
