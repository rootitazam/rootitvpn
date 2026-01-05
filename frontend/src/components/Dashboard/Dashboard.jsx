import { useState, useEffect } from 'react'
import { usersAPI, monitoringAPI } from '../../services/api'
import { formatBytes } from '../../utils/format'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [monitoringStats, setMonitoringStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [userStats, monitorStats] = await Promise.all([
        usersAPI.getStats(),
        monitoringAPI.getStats(),
      ])
      setStats(userStats.data)
      setMonitoringStats(monitorStats.data)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">در حال بارگذاری...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">داشبورد</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">کل کاربران</p>
              <p className="text-2xl font-bold text-gray-800">
                {stats?.total_users || 0}
              </p>
            </div>
            <div className="bg-primary-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">کاربران فعال</p>
              <p className="text-2xl font-bold text-green-600">
                {stats?.active_users || 0}
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">کاربران آنلاین</p>
              <p className="text-2xl font-bold text-blue-600">
                {monitoringStats?.total_online || 0}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">ترافیک 24 ساعته</p>
              <p className="text-2xl font-bold text-purple-600">
                {formatBytes(monitoringStats?.total_traffic_24h || 0)}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Data Usage */}
      {stats && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">مصرف داده</h2>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">مصرف شده</span>
              <span className="font-medium">{formatBytes(stats.total_data_used)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">کل محدودیت</span>
              <span className="font-medium">
                {stats.total_data_limit > 0 ? formatBytes(stats.total_data_limit) : 'نامحدود'}
              </span>
            </div>
            {stats.total_data_limit > 0 && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{
                    width: `${Math.min((stats.total_data_used / stats.total_data_limit) * 100, 100)}%`
                  }}
                ></div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

