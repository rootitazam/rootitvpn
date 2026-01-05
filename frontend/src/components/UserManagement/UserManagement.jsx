import { useState, useEffect } from 'react'
import { usersAPI, subscriptionsAPI } from '../../services/api'
import { formatBytes, formatDate } from '../../utils/format'
import UserModal from './UserModal'
import SubscriptionModal from './SubscriptionModal'

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [editingUser, setEditingUser] = useState(null)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const response = await usersAPI.getAll()
      setUsers(response.data)
    } catch (error) {
      console.error('Error loading users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingUser(null)
    setShowModal(true)
  }

  const handleEdit = (user) => {
    setEditingUser(user)
    setShowModal(true)
  }

  const handleDelete = async (userId) => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این کاربر را حذف کنید؟')) {
      return
    }

    try {
      await usersAPI.delete(userId)
      loadUsers()
    } catch (error) {
      alert('خطا در حذف کاربر')
    }
  }

  const handleShowSubscription = (user) => {
    setSelectedUser(user)
    setShowSubscriptionModal(true)
  }

  const handleResetData = async (userId) => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید مصرف داده این کاربر را صفر کنید؟')) {
      return
    }

    try {
      await usersAPI.resetData(userId)
      loadUsers()
    } catch (error) {
      alert('خطا در ریست کردن داده')
    }
  }

  if (loading) {
    return <div className="text-center py-8">در حال بارگذاری...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-800">مدیریت کاربران</h1>
        <button onClick={handleCreate} className="btn-primary">
          + افزودن کاربر جدید
        </button>
      </div>

      {/* Mobile-first responsive table */}
      <div className="card overflow-x-auto">
        <div className="min-w-full">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">نام کاربری</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">UUID</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">مصرف داده</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">وضعیت</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                    کاربری یافت نشد
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{user.username}</td>
                    <td className="px-4 py-3 text-sm font-mono text-xs">
                      {user.uuid.substring(0, 8)}...
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="space-y-1">
                        <div>{formatBytes(user.data_used)}</div>
                        {user.data_limit > 0 && (
                          <div className="text-xs text-gray-500">
                            از {formatBytes(user.data_limit)}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {user.is_active ? 'فعال' : 'غیرفعال'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => handleEdit(user)}
                          className="text-primary-600 hover:text-primary-800 text-xs"
                        >
                          ویرایش
                        </button>
                        <button
                          onClick={() => handleShowSubscription(user)}
                          className="text-blue-600 hover:text-blue-800 text-xs"
                        >
                          لینک اشتراک
                        </button>
                        <button
                          onClick={() => handleResetData(user.id)}
                          className="text-yellow-600 hover:text-yellow-800 text-xs"
                        >
                          ریست داده
                        </button>
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="text-red-600 hover:text-red-800 text-xs"
                        >
                          حذف
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <UserModal
          user={editingUser}
          onClose={() => {
            setShowModal(false)
            setEditingUser(null)
          }}
          onSave={loadUsers}
        />
      )}

      {showSubscriptionModal && selectedUser && (
        <SubscriptionModal
          user={selectedUser}
          onClose={() => {
            setShowSubscriptionModal(false)
            setSelectedUser(null)
          }}
        />
      )}
    </div>
  )
}

