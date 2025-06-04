import { BarChart3, Eye, FileText, LayoutDashboard, Settings, Shield, MessageSquareWarning } from "lucide-react"
import Image from "next/image"
import Link from "next/link"

export default function Sidebar() {
  return (
    <div className="flex h-screen w-[240px] flex-col border-r bg-white">
      <div className="p-6">
        <Image
          src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image%20(2)-aSrFSqsI8iE8MgfhVLMRNifpjIPNph.png"
          alt="Mimecast Logo"
          width={120}
          height={32}
          className="mb-8"
        />
        <nav className="space-y-2">
          <Link
            href="#"
            className="flex items-center gap-3 rounded-md bg-primary px-3 py-2 text-sm text-primary-foreground"
          >
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Link>
          <Link
            href="#"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
          >
            <Eye className="h-4 w-4" />
            Detections
          </Link>
          <Link
            href="/spam-test"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
          >
            <MessageSquareWarning className="h-4 w-4" />
            Spam Test
          </Link>
          <Link
            href="#"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
          >
            <Shield className="h-4 w-4" />
            Policies
          </Link>
          <Link
            href="#"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
          >
            <BarChart3 className="h-4 w-4" />
            Reports
          </Link>
          <Link
            href="#"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
          >
            <FileText className="h-4 w-4" />
            Audit Logs
          </Link>
          <Link
            href="#"
            className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted"
          >
            <Settings className="h-4 w-4" />
            Configuration
          </Link>
        </nav>
      </div>
    </div>
  )
}

