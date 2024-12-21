import { useEffect, useState } from "react";
export function GraphVisualizer({ htmlGraphPath }: { htmlGraphPath: string }) {
  const [graphFiles, setGraphFiles] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchGraphFiles() {
      try {
        console.log("Fetching from path:", `${htmlGraphPath}/html_graphs`);
        const response = await fetch(`${htmlGraphPath}/html_graphs`);

        console.log("Response status:", response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const files = await response.json();
        console.log("Received files:", files);
        setGraphFiles(files);
      } catch (error) {
        console.error("Failed to load graph files:", error);
        setError((error as Error).message);
      }
    }

    fetchGraphFiles();
  }, [htmlGraphPath]);

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  if (graphFiles?.length === 0) {
    return <p>No graphs available to display.</p>;
  }

  return (
    <div className="grid gap-4">
      {graphFiles.map((file, index) => (
        <div key={index} className="border rounded p-4">
          <h3 className="text-lg font-semibold mb-2">
            {file.replace(".html", "").replace(/_/g, " ")}
          </h3>
          <iframe
            src={`http://localhost:8000/public/html_graphs/${file}`}
            title={`Graph ${index + 1}`}
            style={{ width: "39vw", height: "500px" }}
          />
        </div>
      ))}
    </div>
  );
}
