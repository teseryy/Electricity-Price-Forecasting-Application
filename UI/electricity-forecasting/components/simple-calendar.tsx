"use client"

import { useState, useEffect } from "react"
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay } from "date-fns"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SimpleCalendarProps {
  selected?: Date
  onSelect: (date: Date) => void
  disabled?: { before?: Date; after?: Date }
}

export function SimpleCalendar({ selected, onSelect, disabled }: SimpleCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className="h-[300px] flex items-center justify-center">Loading calendar...</div>
  }

  const monthStart = startOfMonth(currentMonth)
  const monthEnd = endOfMonth(currentMonth)
  const monthDays = eachDayOfInterval({ start: monthStart, end: monthEnd })

  // Get day names
  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  const isDateDisabled = (date: Date) => {
    if (!disabled) return false
    if (disabled.before && date < disabled.before) return true
    if (disabled.after && date > disabled.after) return true
    return false
  }

  return (
    <div className="w-full max-w-sm">
      <div className="flex items-center justify-between mb-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
          className="h-7 w-7"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <h2 className="font-medium">{format(currentMonth, "MMMM yyyy")}</h2>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
          className="h-7 w-7"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekDays.map((day) => (
          <div key={day} className="text-center text-sm font-medium text-muted-foreground">
            {day}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {Array.from({ length: monthStart.getDay() }, (_, i) => (
          <div key={`empty-start-${i}`} className="h-8 w-8" />
        ))}

        {monthDays.map((day) => {
          const isSelected = selected ? isSameDay(day, selected) : false
          const isDisabled = isDateDisabled(day)

          return (
            <Button
              key={day.toString()}
              variant={isSelected ? "default" : "ghost"}
              size="icon"
              disabled={isDisabled}
              onClick={() => onSelect(day)}
              className={`h-8 w-8 p-0 ${isSelected ? "bg-primary text-primary-foreground" : ""} ${
                isDisabled ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {format(day, "d")}
            </Button>
          )
        })}

        {Array.from({ length: 6 - monthEnd.getDay() }, (_, i) => (
          <div key={`empty-end-${i}`} className="h-8 w-8" />
        ))}
      </div>
    </div>
  )
}
