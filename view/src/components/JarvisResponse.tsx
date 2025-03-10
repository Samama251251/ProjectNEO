import React, { useEffect, useRef, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

interface JarvisResponseProps {
  response: string;
  onTypingComplete: () => void;
  mood: 'normal' | 'creative' | 'offensive';
}

const JarvisResponse: React.FC<JarvisResponseProps> = ({ response, onTypingComplete, mood }) => {
  const controls = useAnimation();
  const containerRef = useRef<HTMLDivElement>(null);
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  const moodColors = {
    normal: 'text-cyan-400',
    creative: 'text-purple-400',
    offensive: 'text-red-400',
  };

  useEffect(() => {
    controls.start({
      opacity: 1,
      transition: { duration: 0.5 }
    });
  }, [controls]);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [displayedText]);

  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
  }, [response]);

  useEffect(() => {
    if (currentIndex < response.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + response[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 30);
      return () => clearTimeout(timeout);
    } else {
      onTypingComplete();
    }
  }, [currentIndex, response, onTypingComplete]);

  return (
    <motion.div
      ref={containerRef}
      initial={{ opacity: 0 }}
      animate={controls}
      className={`p-4 ${moodColors[mood]} font-mono relative z-10`}
    >
      <ReactMarkdown
        components={{
          h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-2" {...props} />,
          h2: ({ node, ...props }) => <h2 className="text-xl font-bold mb-2" {...props} />,
          h3: ({ node, ...props }) => <h3 className="text-lg font-bold mb-2" {...props} />,
          p: ({ node, ...props }) => <p className="mb-2" {...props} />,
          ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-2" {...props} />,
          ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-2" {...props} />,
          li: ({ node, ...props }) => <li className="mb-1" {...props} />,
          a: ({ node, ...props }) => <a className="underline hover:text-white" {...props} />,
          code: ({ node, inline, ...props }) => 
            inline 
              ? <code className="bg-gray-800 rounded px-1" {...props} />
              : <code className="block bg-gray-800 rounded p-2 my-2 overflow-x-auto" {...props} />,
        }}
      >
        {displayedText}
      </ReactMarkdown>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 0] }}
        transition={{ repeat: Infinity, duration: 0.8 }}
        className="inline-block w-2 h-4 bg-current ml-1"
      />
    </motion.div>
  );
};

export default JarvisResponse;