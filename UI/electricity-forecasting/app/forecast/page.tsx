import { Suspense } from "react"
import Link from "next/link"
import { ForecastResults } from "@/components/forecast-results"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import { LoadingSpinner } from "@/components/loading-spinner"

export default async function ForecastPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  // В Next.js 15 searchParams нужно получать асинхронно
  const params = await Promise.resolve(searchParams)

  const from = params.from as string
  const to = params.to as string
  const timeframe = params.timeframe as string

  if (!from || !to || !timeframe) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold mb-4">Insufficient parameters for forecast</h1>
          <p className="mb-6">Please return to the home page and select forecast parameters</p>
          <Link href="/">
            <Button>Return to Home</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <main className="container mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Link href="/">
            <Button variant="ghost" size="icon" className="mr-2">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">Forecast Results</h1>
        </div>
        <div className="text-sm text-muted-foreground">
          {from} — {to} • {timeframe === "hourly" ? "Hourly" : "Daily"} timeframe
        </div>
      </div>

      <Suspense fallback={<LoadingSpinner />}>
        <ForecastResults from={from} to={to} timeframe={timeframe as "hourly" | "daily"} />
      </Suspense>
    </main>
  )
}
