"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { format, subYears, addDays } from "date-fns"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SimpleCalendar } from "@/components/simple-calendar"
// Добавьте импорт LoadingSpinner
import { LoadingSpinner } from "@/components/loading-spinner"

interface ForecastModalProps {
  children: React.ReactNode
}

export function ForecastModal({ children }: ForecastModalProps) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

  // Эффект для отслеживания монтирования компонента
  useEffect(() => {
    setMounted(true)
  }, [])

  // Default values - инициализируем только на клиенте
  const [startDate, setStartDate] = useState<Date | undefined>(undefined)
  const [endDate, setEndDate] = useState<Date | undefined>(undefined)
  const [timeframe, setTimeframe] = useState<string>("hourly")

  // Инициализируем даты только после монтирования компонента
  useEffect(() => {
    if (mounted) {
      const today = new Date()
      const tomorrow = addDays(today, 1)
      const oneYearAgo = subYears(today, 1)

      setStartDate(oneYearAgo)
      setEndDate(tomorrow)
    }
  }, [mounted])

  // Date selection constraints - вычисляем только на клиенте
  const startDateDisabledDays = mounted
    ? {
        before: subYears(new Date(), 1),
        after: new Date(),
      }
    : {}

  const endDateDisabledDays = mounted
    ? {
        before: new Date(), // Изменено с addDays(new Date(), 1) на new Date()
        after: addDays(new Date(), 30),
      }
    : {}

  // Добавьте состояние isSubmitting
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Измените функцию handleSubmit, чтобы показывать анимацию загрузки
  const handleSubmit = () => {
    if (!startDate || !endDate) return

    setIsSubmitting(true) // Устанавливаем состояние загрузки

    const params = new URLSearchParams()
    params.set("from", format(startDate, "yyyy-MM-dd"))
    params.set("to", format(endDate, "yyyy-MM-dd"))
    params.set("timeframe", timeframe)

    // Не закрываем модальное окно сразу, чтобы показать анимацию
    // setOpen(false)
    router.push(`/forecast?${params.toString()}`)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      {/* Измените DialogContent, добавив условный рендеринг для состояния загрузки */}
      {/* Найдите DialogContent и замените его содержимое на следующее: */}
      <DialogContent className="sm:max-w-[600px]">
        {isSubmitting ? (
          <LoadingSpinner />
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>Forecast Parameters</DialogTitle>
              <DialogDescription>Select the period and timeframe to get electricity price forecasts</DialogDescription>
            </DialogHeader>

            <div className="grid gap-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Start Date Calendar */}
                <Card className="border shadow-sm">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Start Date</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0 flex justify-center">
                    {mounted ? (
                      <div className="flex flex-col items-center">
                        <SimpleCalendar selected={startDate} onSelect={setStartDate} disabled={startDateDisabledDays} />
                        <div className="mt-2 text-sm text-center">
                          Selected: {startDate ? format(startDate, "d MMMM yyyy") : "None"}
                        </div>
                      </div>
                    ) : (
                      <div className="h-[300px] flex items-center justify-center">Loading calendar...</div>
                    )}
                  </CardContent>
                </Card>

                {/* End Date Calendar */}
                <Card className="border shadow-sm">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">End Date</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0 flex justify-center">
                    {mounted ? (
                      <div className="flex flex-col items-center">
                        <SimpleCalendar selected={endDate} onSelect={setEndDate} disabled={endDateDisabledDays} />
                        <div className="mt-2 text-sm text-center">
                          Selected: {endDate ? format(endDate, "d MMMM yyyy") : "None"}
                        </div>
                      </div>
                    ) : (
                      <div className="h-[300px] flex items-center justify-center">Loading calendar...</div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Timeframe Selection */}
              <div className="flex items-center gap-4 px-4">
                <div className="w-1/4 text-right">
                  <label htmlFor="timeframe" className="text-sm font-medium">
                    Timeframe
                  </label>
                </div>
                <div className="w-3/4">
                  <Select value={timeframe} onValueChange={setTimeframe}>
                    <SelectTrigger id="timeframe">
                      <SelectValue placeholder="Select timeframe" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hourly">Hourly</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button type="submit" onClick={handleSubmit} disabled={!startDate || !endDate}>
                Get Forecast
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
