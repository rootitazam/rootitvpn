import { useState, useEffect } from 'react'
import { xrayAPI } from '../../services/api'
import { formatDate } from '../../utils/format'

export default function Settings() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [formData, setFormData] = useState({
    reality_dest: '',
    reality_server_names: [],
    server_name_input: '',
    server_ip: '',
  })

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await xrayAPI.getConfig()
      const data = response.data
      setConfig(data)
      setFormData({
        reality_dest: data.reality_dest || '',
        reality_server_names: data.reality_server_names || [],
        server_name_input: '',
        server_ip: data.server_ip || '',
      })
    } catch (error) {
      console.error('Error loading config:', error)
      setMessage({ type: 'error', text: 'خطا در بارگذاری تنظیمات' })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage({ type: '', text: '' })

    try {
      await xrayAPI.updateConfig({
        reality_dest: formData.reality_dest,
        reality_server_names: formData.reality_server_names,
        server_ip: formData.server_ip,
      })
      setMessage({ type: 'success', text: 'تنظیمات با موفقیت ذخیره شد' })
      await loadConfig()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'خطا در ذخیره تنظیمات',
      })
    } finally {
      setSaving(false)
    }
  }

  const handleRotate = async () => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید تنظیمات Reality را چرخش دهید؟')) {
      return
    }

    setSaving(true)
    setMessage({ type: '', text: '' })

    try {
      const response = await xrayAPI.rotateReality()
      setMessage({ type: 'success', text: 'تنظیمات Reality با موفقیت چرخش یافت' })
      await loadConfig()
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'خطا در چرخش تنظیمات',
      })
    } finally {
      setSaving(false)
    }
  }

  const handleReload = async () => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید کانفیگ Xray را reload کنید؟')) {
      return
    }

    setSaving(true)
    setMessage({ type: '', text: '' })

    try {
      await xrayAPI.reload()
      setMessage({ type: 'success', text: 'درخواست reload ارسال شد' })
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'خطا در reload',
      })
    } finally {
      setSaving(false)
    }
  }

  const addServerName = () => {
    if (formData.server_name_input.trim()) {
      setFormData({
        ...formData,
        reality_server_names: [...formData.reality_server_names, formData.server_name_input.trim()],
        server_name_input: '',
      })
    }
  }

  const removeServerName = (index) => {
    setFormData({
      ...formData,
      reality_server_names: formData.reality_server_names.filter((_, i) => i !== index),
    })
  }

  if (loading) {
    return <div className="text-center py-8">در حال بارگذاری...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-800">تنظیمات</h1>
      </div>

      {message.text && (
        <div
          className={`p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Server Settings */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">تنظیمات سرور</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              آدرس IP سرور (Server IP) *
            </label>
            <input
              type="text"
              value={formData.server_ip}
              onChange={(e) => setFormData({ ...formData, server_ip: e.target.value })}
              placeholder="مثال: 185.123.45.67 یا vpn.example.com"
              className="input-field"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              آدرس IP عمومی سرور یا دامنه که در لینک‌های اشتراک‌گذاری استفاده می‌شود
            </p>
          </div>
        </div>
      </div>

      {/* Reality Settings */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">تنظیمات Reality</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Destination (Dest)
            </label>
            <input
              type="text"
              value={formData.reality_dest}
              onChange={(e) => setFormData({ ...formData, reality_dest: e.target.value })}
              placeholder="مثال: www.microsoft.com:443"
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              آدرس مقصد برای Reality protocol (باید یک سرور معتبر باشد)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Server Names (SNI)
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={formData.server_name_input}
                onChange={(e) => setFormData({ ...formData, server_name_input: e.target.value })}
                placeholder="مثال: www.microsoft.com"
                className="input-field flex-1"
                onKeyPress={(e) => e.key === 'Enter' && addServerName()}
              />
              <button onClick={addServerName} className="btn-primary whitespace-nowrap">
                افزودن
              </button>
            </div>
            {formData.reality_server_names.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.reality_server_names.map((name, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm"
                  >
                    {name}
                    <button
                      onClick={() => removeServerName(index)}
                      className="hover:text-primary-600"
                    >
                      ✕
                    </button>
                  </span>
                ))}
              </div>
            )}
            <p className="text-xs text-gray-500 mt-1">
              لیست دامنه‌هایی که برای SNI استفاده می‌شوند
            </p>
          </div>

          <div className="flex gap-2 pt-4">
            <button onClick={handleSave} disabled={saving} className="btn-primary">
              {saving ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
            </button>
            <button onClick={handleRotate} disabled={saving} className="btn-secondary">
              چرخش تنظیمات Reality
            </button>
          </div>
        </div>
      </div>

      {/* Current Configuration Info */}
      {config && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">اطلاعات کانفیگ فعلی</h2>

          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Public Key:</span>
              <code className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                {config.reality_public_key
                  ? `${config.reality_public_key.substring(0, 20)}...`
                  : 'در حال تولید...'}
              </code>
            </div>

            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Short IDs:</span>
              <div className="flex gap-2">
                {config.reality_short_ids && config.reality_short_ids.length > 0 ? (
                  config.reality_short_ids.map((id, index) => (
                    <code key={index} className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                      {id}
                    </code>
                  ))
                ) : (
                  <span className="text-gray-400 text-sm">هیچ</span>
                )}
              </div>
            </div>

            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Server IP:</span>
              <span className="text-sm font-mono">
                {config.server_ip || 'تنظیم نشده'}
              </span>
            </div>

            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">آخرین چرخش:</span>
              <span className="text-sm">
                {config.last_rotated ? formatDate(config.last_rotated) : 'هنوز انجام نشده'}
              </span>
            </div>

            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">آخرین به‌روزرسانی:</span>
              <span className="text-sm">{formatDate(config.updated_at)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Xray Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">عملیات Xray</h2>

        <div className="space-y-3">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>توجه:</strong> بعد از تغییر تنظیمات، باید Xray را reload کنید تا تغییرات اعمال شوند.
            </p>
          </div>

          <button onClick={handleReload} disabled={saving} className="btn-primary w-full">
            {saving ? 'در حال reload...' : 'Reload Xray Config'}
          </button>
        </div>
      </div>

      {/* System Info */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">اطلاعات سیستم</h2>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">پروتکل:</span>
            <span className="font-medium">VLESS + Reality + XTLS-RPX-Vision</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Fragment:</span>
            <span className="font-medium">فعال (tlshello)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">TCP Fast Open:</span>
            <span className="font-medium">فعال</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Routing:</span>
            <span className="font-medium">ایران IPs و .ir domains = DIRECT</span>
          </div>
        </div>
      </div>
    </div>
  )
}

