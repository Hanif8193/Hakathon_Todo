/**
 * TaskForm component for creating and editing tasks.
 *
 * Features:
 * - Create new tasks with title and optional description
 * - Edit existing tasks (populated with current data)
 * - Form validation (title required, max lengths enforced)
 * - Loading states and error handling
 */

'use client'

import { useState, FormEvent } from 'react'

interface TaskFormProps {
  onSubmit: (title: string, description: string | null) => Promise<void>
  onCancel?: () => void
  initialTitle?: string
  initialDescription?: string | null
  mode?: 'create' | 'edit'
}

export default function TaskForm({
  onSubmit,
  onCancel,
  initialTitle = '',
  initialDescription = null,
  mode = 'create',
}: TaskFormProps) {
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState(initialDescription || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate title
    const trimmedTitle = title.trim()
    if (!trimmedTitle) {
      setError('Title is required')
      return
    }

    if (trimmedTitle.length > 200) {
      setError('Title must be 200 characters or less')
      return
    }

    const trimmedDescription = description.trim()
    if (trimmedDescription.length > 2000) {
      setError('Description must be 2000 characters or less')
      return
    }

    try {
      setLoading(true)
      await onSubmit(
        trimmedTitle,
        trimmedDescription || null
      )

      // Reset form on successful create
      if (mode === 'create') {
        setTitle('')
        setDescription('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      // Reset form to initial values
      setTitle(initialTitle)
      setDescription(initialDescription || '')
      setError(null)
      onCancel()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          maxLength={200}
          disabled={loading}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          required
        />
        <p className="mt-1 text-xs text-gray-500">
          {title.length}/200 characters
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description <span className="text-gray-400">(optional)</span>
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description"
          maxLength={2000}
          rows={4}
          disabled={loading}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed resize-none"
        />
        <p className="mt-1 text-xs text-gray-500">
          {description.length}/2000 characters
        </p>
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
        >
          {loading ? (mode === 'create' ? 'Creating...' : 'Saving...') : (mode === 'create' ? 'Create Task' : 'Save Changes')}
        </button>

        {onCancel && (
          <button
            type="button"
            onClick={handleCancel}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
