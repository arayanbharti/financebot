import { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

export default function FileUpload({tableWithSummary,setTableWithSummary,setIsActive}:any) {
  const navigate=useNavigate();
  const [fileName, setFileName] = useState('');
  useEffect(()=>{
    console.log("TABLE WITH SUMMARY",tableWithSummary)
  },tableWithSummary)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      console.error("No files accepted");
      return;
    }

    setFileName(acceptedFiles.map(f => f.name).join(", "));

    try {
      const base64Files = await Promise.all(
        acceptedFiles.map(async (file) => {
          const reader = new FileReader();
          reader.readAsDataURL(file);
          const base64File = await new Promise<string>((resolve, reject) => {
            reader.onload = () =>
              resolve(reader.result?.toString().split(",")[1] || "");
            reader.onerror = (error) => reject(error);
          });
          return base64File;
        })
      );

      const payload = {
        files: base64Files,
      };
      console.log("SENDING REQUEST")
      const response = await fetch("http://localhost:8000/api/uploads/finance-data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Internal Server Error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response:", data);
      toast(data.message)
      setIsActive(()=>true)
      const parsingResponse=await fetch("http://localhost:8000/api/parse/start-parsing",{
        method:"POST",
        headers:{
          "Content-Type":"application/json",
        },
      })
      setIsActive(()=>false)
      if(!parsingResponse.ok){
        throw new Error(`Internal Server Error: ${response.status}`);
      }
      toast("Success")
      const parsingData=await parsingResponse.json();
      setTableWithSummary(parsingData?.details?.table_with_summary);
      console.log("Parsing Response",parsingData);
      navigate("/dashboard")
    } catch (error : any) {
      console.error("Error during upload:", error);
      toast(error.message)
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
  });

  return (
    <div
      {...getRootProps()}
      className="w-full max-w-2xl mx-auto p-8 border-2 border-dashed border-indigo-300 rounded-lg bg-white hover:border-indigo-500 transition-colors cursor-pointer"
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center space-y-4">
        <Upload size={48} className="text-indigo-500" />
        {isDragActive ? (
          <p className="text-lg text-gray-600">Drop your PDF here...</p>
        ) : (
          <>
            <p className="text-lg text-gray-600">
              {fileName
                ? `Uploaded: ${fileName}`
                : "Upload your documents (PDF format only)"}
            </p>
            <p className="text-sm text-gray-500">
              Drag and drop your files here, or click to select
            </p>
          </>
        )}
      </div>
    </div>
  );
}
