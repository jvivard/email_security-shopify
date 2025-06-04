import { Bug, ShieldAlert, ShieldX, SpellCheckIcon as Spam } from "lucide-react"
import DetectionChart from "../components/detection-chart"
import DetectionOverview from "./detection-overview"
import RecentDetections from "./recent-detections"
import SecurityMetricCard from "../components/security-metric-card"

export default function SecurityDashboard() {
  const metrics = [
    {
      title: "Malware",
      detections: 33,
      icon: Bug,
      color: "text-blue-500",
    },
    {
      title: "Phishing",
      detections: 65,
      icon: ShieldAlert,
      color: "text-green-500",
    },
    {
      title: "Untrustworthy",
      detections: 80,
      icon: ShieldX,
      color: "text-yellow-500",
    },
    {
      title: "Spam",
      detections: 77,
      icon: Spam,
      color: "text-purple-500",
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Security</h1>
      <div className="grid gap-6 lg:grid-cols-[1fr,auto]">
        <div className="grid gap-6 md:grid-cols-2">
          <DetectionOverview totalDetections={255} percentageChange={4} />
          <DetectionChart />
        </div>
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <SecurityMetricCard key={metric.title} {...metric} />
        ))}
      </div>
      <RecentDetections />
    </div>
  )
}

