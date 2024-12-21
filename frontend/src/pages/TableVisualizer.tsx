import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useEffect } from 'react';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';

const TableVisualizer = ({ tableWithSummary }:any) => {
  const navigate=useNavigate();
  useEffect(()=>{
    !tableWithSummary && toast("Please upload the files first from HomePage") && navigate("/")
  },[tableWithSummary]);
  const tables=tableWithSummary?.map((current:any)=>{
    return current.table;
  })
  return (
    <div className="p-4 bg-white rounded-lg shadow-lg mt-16">
      {tables?.map((tableContent: any, index: any) => (
        <div key={index} className="mb-8">
          <ReactMarkdown
            children={tableContent}
            remarkPlugins={[remarkGfm]}
            className="table-auto w-full"
            components={{
              table: ({ children }) => <table className="table-auto w-full">{children}</table>,
              thead: ({ children }) => <thead className="bg-gray-100">{children}</thead>,
              tr: ({ children }) => <tr className="hover:bg-gray-100">{children}</tr>,
              th: ({ children }) => (
                <th className="px-6 py-3 text-left text-xs leading-4 font-medium text-gray-500 uppercase border-b-2 border-gray-300">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-6 py-4 whitespace-no-wrap border-b-2 border-gray-300">{children}</td>
              ),
            }}
          />
          {index < tables.length - 1 && <hr className="my-8 border-gray-300" />}
        </div>
      ))}
    </div>
  );
};

export default TableVisualizer;
