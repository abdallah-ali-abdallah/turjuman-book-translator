'use client'

import { useQuery } from '@tanstack/react-query'
import { translationApi } from '@/lib/api'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { PlusCircle, BarChart, Book, Clock } from 'lucide-react'

export default function Dashboard() {
  const { data: statistics, isLoading: isLoadingStats } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => {
      const response = await translationApi.getStatistics()
      return response.data
    },
  })

  const { data: jobsData, isLoading: isLoadingJobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await translationApi.getJobs()
      return response.data
    },
  })

  const recentJobs = jobsData?.jobs?.slice(0, 5) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <Link href="/dashboard/new-translation">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Translation
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
          <div className="p-6 flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <BarChart className="h-4 w-4 text-primary" />
              <h3 className="tracking-tight text-sm font-medium">Total Jobs</h3>
            </div>
            <div className="text-2xl font-bold">
              {isLoadingStats ? (
                <div className="h-8 w-16 animate-pulse rounded bg-muted"></div>
              ) : (
                statistics?.total_jobs || 0
              )}
            </div>
          </div>
        </div>
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
          <div className="p-6 flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <Book className="h-4 w-4 text-primary" />
              <h3 className="tracking-tight text-sm font-medium">Total Words</h3>
            </div>
            <div className="text-2xl font-bold">
              {isLoadingStats ? (
                <div className="h-8 w-24 animate-pulse rounded bg-muted"></div>
              ) : (
                statistics?.total_words?.toLocaleString() || 0
              )}
            </div>
          </div>
        </div>
        <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
          <div className="p-6 flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-primary" />
              <h3 className="tracking-tight text-sm font-medium">Deep Translation %</h3>
            </div>
            <div className="text-2xl font-bold">
              {isLoadingStats ? (
                <div className="h-8 w-16 animate-pulse rounded bg-muted"></div>
              ) : (
                `${statistics?.deep_translation_percent || 0}%`
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold tracking-tight">Recent Translations</h2>
          <Link href="/dashboard/history">
            <Button variant="outline" size="sm">
              View All
            </Button>
          </Link>
        </div>
        <div className="rounded-md border">
          {isLoadingJobs ? (
            <div className="p-4">
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex flex-col space-y-2">
                    <div className="h-4 w-1/3 animate-pulse rounded bg-muted"></div>
                    <div className="h-4 w-1/2 animate-pulse rounded bg-muted"></div>
                  </div>
                ))}
              </div>
            </div>
          ) : recentJobs.length > 0 ? (
            <div className="relative w-full overflow-auto">
              <table className="w-full caption-bottom text-sm">
                <thead className="[&_tr]:border-b">
                  <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Job ID
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Languages
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Status
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Created
                    </th>
                    <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                  {recentJobs.map((job) => (
                    <tr
                      key={job.job_id}
                      className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
                    >
                      <td className="p-4 align-middle">{job.job_id.substring(0, 8)}...</td>
                      <td className="p-4 align-middle">
                        {job.source_lang} → {job.target_lang}
                      </td>
                      <td className="p-4 align-middle">
                        <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          job.status === 'completed'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                            : job.status === 'processing'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                            : job.status === 'failed'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                        }`}>
                          {job.status}
                        </div>
                      </td>
                      <td className="p-4 align-middle">
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>
                      <td className="p-4 align-middle">
                        <Link href={`/dashboard/history/${job.job_id}`}>
                          <Button variant="outline" size="sm">
                            View
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <h3 className="mb-2 text-lg font-semibold">No translations yet</h3>
              <p className="mb-4 text-sm text-muted-foreground">
                Start by creating a new translation job.
              </p>
              <Link href="/dashboard/new-translation">
                <Button>
                  <PlusCircle className="mr-2 h-4 w-4" />
                  New Translation
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>

      {statistics && statistics.top_models && statistics.top_models.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold tracking-tight">Top Models</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {statistics.top_models.slice(0, 3).map((model, index) => (
              <div key={index} className="rounded-lg border bg-card text-card-foreground shadow-sm">
                <div className="p-6 flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{model.name}</h3>
                    <p className="text-sm text-muted-foreground">{model.provider}</p>
                  </div>
                  <div className="text-2xl font-bold">{model.count}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
