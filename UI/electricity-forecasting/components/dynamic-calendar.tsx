"use client"

import { useEffect, useState } from "react"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface DynamicCalendarProps {
  selected: Date | undefined
  onSelect: (date: Date | undefined) => void
  disabled?: { before?: Date; after?: Date }
  title: string
}

export function DynamicCalendar({ selected, onSelect, disabled, title }: DynamicCalendarProps) {
  // Используем состояние для отслеживания, находимся ли мы на клиенте
  const [isClient, setIsClient] = useState(false)

  // Эффект выполнится только на клиенте
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Если мы не на клиенте, возвращаем заглушку с тем же размером
  if (!isClient) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="h-[300px] flex items-center justify-center">Loading calendar...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex justify-center">
          <Calendar
            mode="single"
            selected={selected}
            onSelect={onSelect}
            disabled={disabled}
            initialFocus
            className="mx-auto"
          />
        </div>
        <div className="mt-2 text-sm text-center">Selected: {selected ? format(selected, "d MMMM yyyy") : "None"}</div>
      </CardContent>
    </Card>
  )
}
