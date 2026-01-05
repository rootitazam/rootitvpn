import { useState, useEffect } from 'react'
import { monitoringAPI } from '../../services/api'
import { formatBytes, formatDate } from '../../utils/format'

export default function Monitoring() {
  const [onlineUsers, setOnlineUsers] = useState([])
  const [accessLogs, setAccessLogs] = useState([])
  const [topDomains, setTopDomains] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('online')

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [activeTab])

  const loadData = async () => {
    try {
      if (activeTab === 'online') {
        const response = await monitoringAPI.getOnlineUsers()
        setOnlineUsers(response.data)
      } else if (activeTab === 'logs') {
        const response = await monitoringAPI.getAccessLogs({ limit: 100 })
        setAccessLogs(response.data)
      } else if (activeTab === 'domains') {
        const response = await monitoringAPI.getTopDomains({ limit: 20 })
        setTopDomains(response.data)
      }
    } catch (error) {
      console.error('Error loading monitoring data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">مانیتورینگ</h1>

      {/* Tabs */}
      <div className="flex gap-2 border-b overflow-x-auto">
        <button
          onClick={() => setActiveTab('online')}
          className={`px-4 py-2 whitespace-nowrap ${
            activeTab === 'online'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          کاربران آنلاین
        </button>
        <button
          onClick={() => setActiveTab('logs')}
          className={`px-4 py-2 whitespace-nowrap ${
            activeTab === 'logs'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          لاگ دسترسی (SNI)
        </button>
        <button
          onClick={() => setActiveTab('domains')}
          className={`px-4 py-2 whitespace-nowrap ${
            activeTab === 'domains'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          دامنه‌های پربازدید
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="text-center py-8">در حال بارگذاری...</div>
      ) : (
        <>
          {activeTab === 'online' && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-4">کاربران آنلاین ({onlineUsers.length})</h2>
              {onlineUsers.length === 0 ? (
                <p className="text-gray-500 text-center py-8">هیچ کاربر آنلاینی وجود ندارد</p>
              ) : (
                <div className="space-y-4">
                  {onlineUsers.map((user) => (
                    <div key={user.user_id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium">{user.username}</h3>
                          <p className="text-sm text-gray-500 font-mono">{user.uuid.substring(0, 8)}...</p>
                        </div>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                          آنلاین
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
                        <div>
                          <span className="text-gray-600">مصرف داده: </span>
                          <span className="font-medium">{formatBytes(user.data_used)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">آخرین فعالیت: </span>
                          <span className="font-medium">{formatDate(user.last_seen)}</span>
                        </div>
                      </div>
                      {user.devices && user.devices.length > 0 && (
                        <div className="mt-4 pt-4 border-t">
                          <p className="text-sm font-medium mb-2">دستگاه‌ها:</p>
                          <div className="space-y-2">
                            {user.devices.map((device) => (
                              <div key={device.id} className="text-xs text-gray-600">
                                <span className="font-mono">{device.fingerprint.substring(0, 16)}...</span>
                                {device.user_agent && (
                                  <span className="mr-2"> - {device.user_agent.substring(0, 50)}...</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="card overflow-x-auto">
              <h2 className="text-lg font-semibold mb-4">لاگ دسترسی (SNI Logging)</h2>
              {accessLogs.length === 0 ? (
                <p className="text-gray-500 text-center py-8">لاگی یافت نشد</p>
              ) : (
                <div className="min-w-full">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">زمان</th>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">دامنه</th>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">ارسال</th>
                        <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">دریافت</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {accessLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm">{formatDate(log.timestamp)}</td>
                          <td className="px-4 py-3 text-sm font-mono">{log.domain || '-'}</td>
                          <td className="px-4 py-3 text-sm">{formatBytes(log.bytes_sent)}</td>
                          <td className="px-4 py-3 text-sm">{formatBytes(log.bytes_received)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'domains' && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-4">دامنه‌های پربازدید (24 ساعت گذشته)</h2>
              {topDomains.length === 0 ? (
                <p className="text-gray-500 text-center py-8">داده‌ای یافت نشد</p>
              ) : (
                <div className="space-y-2">
                  {topDomains.map((domain, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">{domain.domain}</p>
                        <p className="text-sm text-gray-500">{domain.visits} بازدید</p>
                      </div>
                      <div className="text-left">
                        <p className="font-medium">{formatBytes(domain.traffic)}</p>
                        <p className="text-xs text-gray-500">ترافیک</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

