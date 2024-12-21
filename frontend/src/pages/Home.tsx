import { Database } from 'lucide-react';
import FileUpload from '../components/FileUpload';

export default function Home({tableWithSummary,setTableWithSummary,setIsActive}:any) {
  return (
    <div className="min-h-screen pt-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <Database size={64} className="text-indigo-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">DataQuest.ai</h1>
          <p className="text-xl text-gray-600">Transform your data into actionable insights</p>
        </div>
        <FileUpload tableWithSummary={tableWithSummary} setTableWithSummary={setTableWithSummary} setIsActive={setIsActive} />
      </div>
    </div>
  );
}