
import { useEffect } from "react";
import { GraphVisualizer } from "../components/GraphVisualizer";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import remarkGfm from "remark-gfm";
import ReactMarkdown from 'react-markdown';
export default function Dashboard({tableWithSummary}:any) {
  const navigate=useNavigate();
  useEffect(()=>{
    !tableWithSummary && toast("Please upload the files first from HomePage") && navigate("/")
  },[]);
  const summaries=tableWithSummary?.map((current : any)=>{
    return current.summary;
  })
  return (
    <div className="min-h-screen pt-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Graph Visualization</h2>
            <div className="aspect-square bg-gray-100 rounded-lg flex w-full items-center justify-center">
              <GraphVisualizer htmlGraphPath="http://localhost:8000/api/parse" />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Summary Data</h2>
              {
                summaries?.map((summary : any,index:any)=>{
                  return (
                    <div key={index} className=" bg-gray-100 rounded-lg flex-col items-center my-5 justify-center p-4">
                      <ReactMarkdown children={summary} remarkPlugins={[remarkGfm]} className="prose" />
                    </div>
                  )
                })
              }
          </div>
        </div>
      </div>
    </div>
  );
}
