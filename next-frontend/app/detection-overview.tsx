import { TrendingUp } from 'lucide-react';

interface DetectionOverviewProps {
  totalDetections: number;
  percentageChange: number; // Keep this prop to match your UI
}

export default function DetectionOverview({ totalDetections, percentageChange }: DetectionOverviewProps) {
  return (
    <div className="rounded-xl border bg-white p-6">
      <h2 className="mb-4 text-lg font-semibold">Detection Overview</h2>
      <div className="flex items-center justify-between">
        <div className="relative h-32 w-32">
          <svg className="h-full w-full" viewBox="0 0 100 100">
            <circle className="stroke-muted" cx="50" cy="50" r="45" fill="none" strokeWidth="10" />
            <circle
              className="stroke-primary"
              cx="50"
              cy="50"
              r="45"
              fill="none"
              strokeWidth="10"
              strokeDasharray={`${(totalDetections / 500) * 283} 283`}
              transform="rotate(-90 50 50)"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-3xl font-bold">{totalDetections}</span>
            <span className="text-xs text-muted-foreground">Total Detections</span>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm text-primary">
          <TrendingUp className="h-4 w-4" />+{percentageChange}%
        </div>
      </div>
    </div>
  );
}