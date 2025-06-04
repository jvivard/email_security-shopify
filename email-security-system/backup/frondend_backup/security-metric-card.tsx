import type { LucideIcon } from "lucide-react"

interface SecurityMetricCardProps {
  title: string
  detections: number
  icon: LucideIcon
  color: string
}

export default function SecurityMetricCard({ title, detections, icon: Icon, color }: SecurityMetricCardProps) {
  return (
    <div className="rounded-xl border bg-white p-6">
      <div className="mb-4 flex items-center gap-2">
        <Icon className={`h-5 w-5 ${color}`} />
        <h3 className="font-medium">{title}</h3>
      </div>
      <p className="text-2xl font-semibold">{detections} Detections</p>
      <div className="mt-4 h-2 rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${color.replace("text-", "bg-")}`}
          style={{ width: `${(detections / 100) * 100}%` }}
        />
      </div>
    </div>
  )
}

