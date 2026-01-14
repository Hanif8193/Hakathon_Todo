/**
 * TaskCard component displays an individual task with title, description, and completion status.
 *
 * Features:
 * - Visual distinction for completed vs incomplete tasks
 * - Responsive design (mobile to desktop)
 * - Shows all task details (title, description, status, dates)
 * - Edit mode with inline TaskForm
 */

'use client'

import { useState } from 'react'
import TaskForm from './TaskForm'

interface TaskCardProps {
  task: {
    id: number
    title: string
    description: string | null
    completed: boolean
    created_at: string
    updated_at: string
  }
  onUpdate?: (taskId: number, title: string, description: string | null) => Promise<void>
  onToggleComplete?: (taskId: number) => Promise<void>
  onDelete?: (taskId: number) => Promise<void>
}

export default function TaskCard({ task, onUpdate, onToggleComplete, onDelete }: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [toggling, setToggling] = useState(false)
  const [deleting, setDeleting] = useState(false)
  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const handleEdit = async (title: string, description: string | null) => {
    if (onUpdate) {
      await onUpdate(task.id, title, description)
      setIsEditing(false)
    }
  }

  const handleToggleComplete = async () => {
    if (onToggleComplete) {
      setToggling(true)
      try {
        await onToggleComplete(task.id)
      } finally {
        setToggling(false)
      }
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return

    // Show confirmation dialog
    const confirmed = window.confirm(
      `Are you sure you want to delete "${task.title}"? This action cannot be undone.`
    )

    if (!confirmed) return

    setDeleting(true)
    try {
      await onDelete(task.id)
    } finally {
      setDeleting(false)
    }
  }

  // If in edit mode, show TaskForm
  if (isEditing) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-blue-300 p-4">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Edit Task</h4>
        <TaskForm
          onSubmit={handleEdit}
          onCancel={() => setIsEditing(false)}
          initialTitle={task.title}
          initialDescription={task.description}
          mode="edit"
        />
      </div>
    )
  }

  // Normal display mode
  return (
    <div
      className={`
        bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow
        ${task.completed ? 'opacity-60 border-gray-300' : 'border-gray-200'}
      `}
    >
      <div className="flex items-start gap-3">
        {/* Completion Checkbox */}
        {onToggleComplete && (
          <div className="flex-shrink-0 pt-1">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={handleToggleComplete}
              disabled={toggling}
              className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 cursor-pointer disabled:cursor-not-allowed"
            />
          </div>
        )}

        <div className="flex-1 min-w-0">
          {/* Task Title */}
          <h3
            className={`
              text-lg font-semibold text-gray-900 mb-2
              ${task.completed ? 'line-through text-gray-500' : ''}
            `}
          >
            {task.title}
          </h3>

          {/* Task Description */}
          {task.description && (
            <p
              className={`
                text-sm text-gray-600 mb-3
                ${task.completed ? 'line-through' : ''}
              `}
            >
              {task.description}
            </p>
          )}

          {/* Task Metadata */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>Created: {formatDate(task.created_at)}</span>
            {task.updated_at !== task.created_at && (
              <span>Updated: {formatDate(task.updated_at)}</span>
            )}
          </div>
        </div>

        {/* Actions and Status */}
        <div className="ml-4 flex flex-col items-end gap-2">
          {/* Completion Status Badge */}
          {task.completed ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              ✓ Complete
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Pending
            </span>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            {onUpdate && (
              <button
                onClick={() => setIsEditing(true)}
                disabled={deleting}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Edit
              </button>
            )}

            {onDelete && (
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="text-sm text-red-600 hover:text-red-800 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
