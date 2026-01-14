/**
 * TaskList component renders a list of tasks using TaskCard components.
 *
 * Features:
 * - Displays multiple tasks in a vertical list
 * - Responsive grid layout
 * - Shows empty state when no tasks
 */

import TaskCard from './TaskCard'

interface Task {
  id: number
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

interface TaskListProps {
  tasks: Task[]
  onUpdate?: (taskId: number, title: string, description: string | null) => Promise<void>
  onToggleComplete?: (taskId: number) => Promise<void>
  onDelete?: (taskId: number) => Promise<void>
}

export default function TaskList({ tasks, onUpdate, onToggleComplete, onDelete }: TaskListProps) {
  // Show empty state if no tasks
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks yet</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first task.
        </p>
      </div>
    )
  }

  // Render task list
  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onToggleComplete={onToggleComplete}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
