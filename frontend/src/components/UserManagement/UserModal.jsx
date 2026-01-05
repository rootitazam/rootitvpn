import { useState, useEffect } from 'react'
import { usersAPI } from '../../services/api'

export default function UserModal({ user, onClose, onSave }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    data_limit: 0,
    expire_date: '',
    is_active: true,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        data_limit: user.data_limit || 0,
        expire_date: user.expire_date ? user.expire_date.split('T')[0] : '',
        is_active: user.is_active !== undefined ? user.is_active : true,
      })
    }
  }, [user])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (user) {
        await usersAPI.update(user.id, formData)
      } else {
        await usersAPI.create(formData)
      }
      onSave()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'خطا در ذخیره کاربر')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">
              {user ? 'ویرایش کاربر' : 'افزودن کاربر جدید'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نام کاربری *
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ایمیل
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                محدودیت داده (بایت) - 0 برای نامحدود
              </label>
              <input
                type="number"
                value={formData.data_limit}
                onChange={(e) => setFormData({ ...formData, data_limit: parseInt(e.target.value) || 0 })}
                className="input-field"
                min="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تاریخ انقضا
              </label>
              <input
                type="date"
                value={formData.expire_date}
                onChange={(e) => setFormData({ ...formData, expire_date: e.target.value })}
                className="input-field"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-primary-600 rounded"
              />
              <label htmlFor="is_active" className="mr-2 text-sm text-gray-700">
                کاربر فعال است
              </label>
            </div>

            <div className="flex gap-2 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 btn-secondary"
              >
                انصراف
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 btn-primary disabled:opacity-50"
              >
                {loading ? 'در حال ذخیره...' : 'ذخیره'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

