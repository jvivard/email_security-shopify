export default function DetectionChart() {
  return (
    <div className="rounded-xl border bg-white p-6">
      <div className="flex h-[160px] items-end gap-2">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className="w-full bg-muted"
            style={{
              height: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>
    </div>
  )
}

