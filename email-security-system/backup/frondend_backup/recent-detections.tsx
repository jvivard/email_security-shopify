interface Detection {
  subject: string
  analysis: string
  service: string
  policy: string
  rule: string
  dateTime: string
}

export default function RecentDetections() {
  const detections: Detection[] = [
    {
      subject: "Suspicious Email Alert",
      analysis: "Malware",
      service: "Email Security",
      policy: "Default",
      rule: "Malware Detection",
      dateTime: "2024-02-23 15:30",
    },
    {
      subject: "Potential Phishing Attempt",
      analysis: "Phishing",
      service: "Email Security",
      policy: "Strict",
      rule: "Phishing Detection",
      dateTime: "2024-02-23 15:25",
    },
    {
      subject: "Spam Message Detected",
      analysis: "Phishing",
      service: "Email Security",
      policy: "Default",
      rule: "Spam Filter",
      dateTime: "2024-02-23 15:20",
    },
  ]

  return (
    <div className="rounded-xl border bg-white p-6">
      <h2 className="mb-4 text-lg font-semibold">Recent Detections</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b text-sm text-muted-foreground">
              <th className="pb-3 text-left font-medium">Message Subject</th>
              <th className="pb-3 text-left font-medium">Analysis</th>
              <th className="pb-3 text-left font-medium">Service</th>
              <th className="pb-3 text-left font-medium">Policy</th>
              <th className="pb-3 text-left font-medium">Rule</th>
              <th className="pb-3 text-left font-medium">Date/Time</th>
            </tr>
          </thead>
          <tbody>
            {detections.map((detection, index) => (
              <tr key={index} className="border-b last:border-0">
                <td className="py-3">{detection.subject}</td>
                <td className="py-3">
                  <span className="rounded-full bg-muted px-2 py-1 text-xs">{detection.analysis}</span>
                </td>
                <td className="py-3">{detection.service}</td>
                <td className="py-3">{detection.policy}</td>
                <td className="py-3">{detection.rule}</td>
                <td className="py-3">{detection.dateTime}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

