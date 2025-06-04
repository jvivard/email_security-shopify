import { Search } from "lucide-react"
import SecurityDashboard from "./security-dashboard"
import Sidebar from "../components/sidebar";  // Adjust path based on structure
export default function Page() {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="mb-6 flex justify-end">
            <div className="relative w-[300px]">
              <input
                type="text"
                placeholder="Search date range here..."
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              <Search className="absolute right-3 top-2.5 h-4 w-4 text-muted-foreground" />
            </div>
          </div>
          <SecurityDashboard />
        </main>
      </div>
    </div>
  )
}

