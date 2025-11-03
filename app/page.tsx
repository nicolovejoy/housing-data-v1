export default function Home() {
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Welcome to the Data Explorer</h2>
        <p className="text-gray-600 mb-4">
          This application provides interactive exploration of HUD Fair Market Rent data across the United States.
        </p>
        <p className="text-gray-600">
          The explorer is being built out with pivot tables and drill-down capabilities. Check back soon!
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-2">📊 Features Coming</h3>
          <ul className="text-gray-600 space-y-1 text-sm">
            <li>• Interactive pivot tables</li>
            <li>• Drill-down by state and area type</li>
            <li>• Real-time search and filtering</li>
            <li>• Rent statistics and comparisons</li>
          </ul>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-2">🗄️ Data</h3>
          <ul className="text-gray-600 space-y-1 text-sm">
            <li>• 5,400+ rental areas</li>
            <li>• Metro areas and counties</li>
            <li>• All US states and territories</li>
            <li>• Studio through 4-bedroom data</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
