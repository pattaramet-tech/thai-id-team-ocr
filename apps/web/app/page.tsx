export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Thai ID Team OCR</h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            OCR Management Dashboard
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Extract Thai names from ID cards and application documents
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <a
              href="/teams"
              className="block rounded-lg bg-blue-600 p-6 text-white hover:bg-blue-700 transition"
            >
              <h3 className="text-xl font-semibold mb-2">Teams</h3>
              <p>Create and manage competition teams</p>
            </a>

            <div className="block rounded-lg bg-gray-300 p-6 text-gray-600 cursor-not-allowed">
              <h3 className="text-xl font-semibold mb-2">Upload & OCR</h3>
              <p>Coming in Phase 2</p>
            </div>

            <div className="block rounded-lg bg-gray-300 p-6 text-gray-600 cursor-not-allowed">
              <h3 className="text-xl font-semibold mb-2">Review Players</h3>
              <p>Coming in Phase 2</p>
            </div>

            <div className="block rounded-lg bg-gray-300 p-6 text-gray-600 cursor-not-allowed">
              <h3 className="text-xl font-semibold mb-2">Export XLSX</h3>
              <p>Coming in Phase 3</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
