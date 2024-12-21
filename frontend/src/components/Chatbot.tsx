import { useState } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';

export default function Chatbot({tableWithSummary}:any) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ text: string; isUser: boolean }[]>([]);
  const [input, setInput] = useState('');

  const handleSubmit = async(e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { text: input, isUser: true }]);
    try {
      const userMessage=input.trim();
      const response=await fetch("http://localhost:8000/api/agent/chat",{
        method:"POST",
        headers:{
          "Content-Type":"application/json"
        },
        body:JSON.stringify({"query":userMessage})
      });
      if(!response.ok){
        throw new Error("Internal server error"+response.status);
      }
      const content=await response.json();
      console.log(content);
      setMessages((prev) => [...prev, { text: content.response, isUser: false }]);
    } catch (error : any) {
      console.log(error.message);
    }
    // setTimeout(() => {
    //   setMessages((prev) => [...prev, { text: 'This is a sample response.', isUser: false }]);
    // }, 1000);
    setInput('');
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-colors"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {isOpen && (
        <div className="bg-white rounded-lg shadow-xl w-80 h-96 flex flex-col">
          <div className="p-4 bg-indigo-600 text-white rounded-t-lg flex justify-between items-center">
            <span>Chat Support</span>
            <button onClick={() => setIsOpen(false)} className="hover:text-gray-200">
              <X size={20} />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`${
                  msg.isUser ? 'ml-auto bg-indigo-600 text-white' : 'mr-auto bg-gray-200'
                } p-2 rounded-lg max-w-[80%]`}
              >
                {msg.text}
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
            <input
              type="text"
              value={!tableWithSummary ? "Please upload the file first" : input}
              disabled={!tableWithSummary}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={!tableWithSummary}
              className="bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-700"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}