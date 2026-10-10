"use client"

import { useState } from "react"
import { format, subYears, addDays } from "date-fns"
import { enUS } from "date-fns/locale"
import { CalendarIcon } from "lucide-react"
import type { DateRange } from "react-day-picker"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"

export function DateRangePicker() {
  // Значения по умолчанию: от года назад до сегодня
  const today = new Date()
  const oneYearAgo = subYears(today, 1)
  const thirtyDaysAhead = addDays(today, 30)

  const [date, setDate] = useState<DateRange | undefined>({
    from: oneYearAgo,
    to: today,
  })

  // Ограничения для выбора дат
  const disabledDays = {
    before: subYears(new Date(), 1),
    after: addDays(new Date(), 30),
  }

  return (
    <div className="grid gap-2">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn("w-full justify-start text-left font-normal", !date && "text-muted-foreground")}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "d MMMM yyyy", { locale: enUS })} -{" "}
                  {format(date.to, "d MMMM yyyy", { locale: enUS })}
                </>
              ) : (
                format(date.from, "d MMMM yyyy", { locale: enUS })
              )
            ) : (
              <span>Выберите период</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={date?.from}
            selected={date}
            onSelect={setDate}
            numberOfMonths={2}
            disabled={disabledDays}
            locale={enUS}
          />
        </PopoverContent>
      </Popover>
    </div>
  )
}
