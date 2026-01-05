import { useState, useEffect } from 'react'
import { subscriptionsAPI } from '../../services/api'
import { QRCodeSVG } from 'qrcode.react'

export default function SubscriptionModal({ user, onClose }) {
  const [subscription, setSubscription] = useState(null)
  const [loading, setLoading] = useState(true)
  const [serverIp, setServerIp] = useState('')
  const [activeTab, setActiveTab] = useState('v2rayng')

  useEffect(() => {
    loadSubscription()
  }, [serverIp, user.id])

  const loadSubscription = async () => {
    if (!serverIp) {
      setLoading(false)
      return
    }

    try {
      const response = await subscriptionsAPI.getUserSubscription(user.id, serverIp)
      setSubscription(response.data)
    } catch (error) {
      console.error('Error loading subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('کپی شد!')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">لینک اشتراک‌گذاری - {user.username}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              آدرس IP سرور
            </label>
            <input
              type="text"
              value={serverIp}
              onChange={(e) => setServerIp(e.target.value)}
              placeholder="مثال: 1.2.3.4"
              className="input-field"
            />
          </div>

          {loading ? (
            <div className="text-center py-8">در حال بارگذاری...</div>
          ) : subscription ? (
            <div className="space-y-4">
              {/* Tabs */}
              <div className="flex gap-2 border-b">
                <button
                  onClick={() => setActiveTab('v2rayng')}
                  className={`px-4 py-2 ${activeTab === 'v2rayng' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-600'}`}
                >
                  v2rayNG
                </button>
                <button
                  onClick={() => setActiveTab('shadowrocket')}
                  className={`px-4 py-2 ${activeTab === 'shadowrocket' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-600'}`}
                >
                  Shadowrocket
                </button>
                <button
                  onClick={() => setActiveTab('nekoray')}
                  className={`px-4 py-2 ${activeTab === 'nekoray' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-600'}`}
                >
                  Nekoray
                </button>
              </div>

              {/* Link Display */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <code className="flex-1 text-sm break-all">
                    {subscription[activeTab]}
                  </code>
                  <button
                    onClick={() => copyToClipboard(subscription[activeTab])}
                    className="btn-primary text-sm"
                  >
                    کپی
                  </button>
                </div>
              </div>

              {/* QR Code */}
              <div className="flex justify-center">
                <div className="bg-white p-4 rounded-lg border">
                  <QRCodeSVG value={subscription[activeTab]} size={200} />
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              لطفاً آدرس IP سرور را وارد کنید
            </div>
          )}

          <div className="mt-6">
            <button onClick={onClose} className="w-full btn-secondary">
              بستن
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

