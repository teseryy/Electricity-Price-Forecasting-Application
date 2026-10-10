import type React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ForecastModal } from "@/components/forecast-modal"

export default function Home() {
  return (
    <main className="container mx-auto min-h-screen flex flex-col items-center justify-center py-8 px-4">
      <Card className="w-full max-w-3xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-900 dark:to-slate-800">
        <CardContent className="pt-10 pb-12 px-8 text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">Electricity Price Forecasting</h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Get accurate electricity price forecasts with confidence intervals based on historical data
            </p>
          </div>

          <div className="flex justify-center pt-4">
            <ForecastModal>
              <Button size="lg" className="text-lg px-8 py-6">
                Get Forecast
              </Button>
            </ForecastModal>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
            <FeatureCard
              title="Historical Data"
              description="Analysis of prices over the past year for accurate forecasting"
              icon={<HistoryIcon className="h-10 w-10" />}
            />
            <FeatureCard
              title="Confidence Intervals"
              description="Ranges of possible price fluctuations accounting for uncertainty"
              icon={<ChartIcon className="h-10 w-10" />}
            />
            <FeatureCard
              title="Multiple Timeframes"
              description="Hourly and daily forecasts for detailed planning"
              icon={<ClockIcon className="h-10 w-10" />}
            />
          </div>
        </CardContent>
      </Card>
    </main>
  )
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center text-center p-4 space-y-2">
      <div className="mb-2 text-primary">{icon}</div>
      <h3 className="font-medium text-lg">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  )
}

function HistoryIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M12 7v5l4 2" />
    </svg>
  )
}

function ChartIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 3v18h18" />
      <path d="M18 12V8" />
      <path d="M18 3v3" />
      <rect x="11" y="8" width="4" height="12" />
      <rect x="4" y="13" width="4" height="7" />
    </svg>
  )
}

function ClockIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  )
}
