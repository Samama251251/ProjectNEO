import React, {useState, useRef, useEffect} from 'react';
import { motion } from 'framer-motion';
import JarvisResponse from './components/JarvisResponse';
import AIBackground from './components/AIBackground';
import AIOrb from './components/Orb';

async function getResponse(prompt: string, onPartialResponse: (text: string) => void) {
  const response = await fetch(`http://localhost:8000/?prompt=${encodeURIComponent(prompt)}`, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'method': 'GET',
      'mode': 'cors',
    },
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let done = false;

  while (!done) {
    const { value, done: readerDone } = await reader!.read();
    done = readerDone;
    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      const parsed = JSON.parse(chunk); // Parse JSON chunks
      console.log(parsed); // For debugging
      const { response, type } = parsed;

      // Handle different types of responses
      if (type === 'chat') {
        onPartialResponse(response); // For text-based chat responses
      } else if (type === 'text_content') {
        onPartialResponse(`${response.result}`); // Handle text generation output
        console.log(response); // For debugging
      } else if (type === 'images') {
        // Add logic to handle image generation (e.g., store image URL and update state)
        onPartialResponse(`${response}`); // For now, just log or display as text
      } else {
        console.warn('Unhandled response type:', type);
      }
    }
  }
}

interface ResponseItem {
  id: number;
  text: string;
  mood: 'normal' | 'creative' | 'offensive';
}

function App() {
  const [input, setInput] = useState<string>('');
  const [responses, setResponses] = useState<ResponseItem[]>([
    { 
      id: 0, 
      text: `# Greetings, I am NEO

Feel free to ask me anything!`, 
      mood: 'normal' 
    }
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(true);
  const [currentMood, setCurrentMood] = useState<'normal' | 'creative' | 'offensive'>('normal');

  const mainRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (mainRef.current) {
      mainRef.current.scrollTop = mainRef.current.scrollHeight;
    }
  }, [responses]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
  
    setIsLoading(true);
    setResponses(prev => [...prev, { id: prev.length, text: 'Processing your request...', mood: currentMood }]);
    setIsTyping(true);
  
    try {
      await getResponse(input, (partialResponse: string) => {
        // Update the response list as partial responses arrive
        setResponses(prev => [...prev, { id: prev.length, text: partialResponse, mood: 'normal' }]);
      });
    } catch (error) {
      console.error('Error fetching response:', error);
      setResponses(prev => {
        const newResponses = [...prev];
        newResponses[newResponses.length - 1] = { id: prev.length - 1, text: 'I apologize, I encountered an error processing your request.', mood: 'normal' };
        return newResponses;
      });
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };
  

  const handleVoiceRecognition = () => {
    // Implement voice recognition logic here
    console.log('Voice recognition activated');
  };

  return (
    <div className="flex flex-col h-screen bg-black relative overflow-hidden">
      <AIBackground mood={currentMood} />
      <header className="p-4 flex justify-center items-center relative z-10">
        <AIOrb />
      </header>
      <main className="flex-1 overflow-y-auto relative z-10 px-4">
        {responses.map((response, index) => (
          <JarvisResponse 
            key={response.id} 
            response={response.text} 
            mood={response.mood}
            onTypingComplete={() => {
              if (index === responses.length - 1) {
                setIsTyping(false);
              }
            }} 
          />
        ))}
      </main>
      <footer className="p-4 relative z-10">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Right Away..."
              className="w-full font-mono p-4 rounded-full bg-gray-900 bg-opacity-50 text-white border-2 border-gray-700 focus:border-cyan-500 focus:outline-none pr-12 transition-all duration-300 ease-in-out"
            />
            <motion.button
              type="button"
              onClick={handleVoiceRecognition}
              className="absolute right-2 top-1/2 transform text-cyan-500 p-2 rounded-full focus:outline-none bg-gray-800 hover:bg-gray-700 transition-colors duration-300"
              //whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 1.3 }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </motion.button>
          </div>
        </form>
      </footer>
    </div>
  );
}

export default App;

