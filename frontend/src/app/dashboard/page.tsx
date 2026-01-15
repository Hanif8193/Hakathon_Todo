'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { clearToken, apiRequest } from '@/lib/api'
import TaskList from '@/components/TaskList'
import TaskForm from '@/components/TaskForm'

interface Task {
  id: number
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [tasks, setTasks] = useState<Task[]>([])
  const [error, setError] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)

  useEffect(() => {
    // Check if user is authenticated and fetch tasks
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    fetchTasks()
  }, [router])

  const fetchTasks = async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await apiRequest('/api/tasks')
      setTasks(data.tasks || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    clearToken()
    router.push('/login')
  }

  const handleCreateTask = async (title: string, description: string | null) => {
    await apiRequest('/api/tasks', {
      method: 'POST',
      body: JSON.stringify({ title, description }),
    })

    // Refresh task list and hide form
    await fetchTasks()
    setShowAddForm(false)
  }

  const handleUpdateTask = async (taskId: number, title: string, description: string | null) => {
    await apiRequest(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify({ title, description }),
    })

    // Refresh task list
    await fetchTasks()
  }

  const handleToggleComplete = async (taskId: number) => {
    await apiRequest(`/api/tasks/${taskId}/complete`, {
      method: 'PATCH',
    })

    // Refresh task list
    await fetchTasks()
  }

  const handleDeleteTask = async (taskId: number) => {
    await apiRequest(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    })

    // Refresh task list
    await fetchTasks()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Todo App</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">My Tasks</h2>
              <p className="mt-1 text-sm text-gray-600">
                Manage your todo list
              </p>
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium"
            >
              {showAddForm ? 'Cancel' : '+ Add Task'}
            </button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {showAddForm && (
            <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Task</h3>
              <TaskForm
                onSubmit={handleCreateTask}
                onCancel={() => setShowAddForm(false)}
                mode="create"
              />
            </div>
          )}

          <TaskList
            tasks={tasks}
            onUpdate={handleUpdateTask}
            onToggleComplete={handleToggleComplete}
            onDelete={handleDeleteTask}
          />
        </div>
      </main>
    </div>
  )
}
