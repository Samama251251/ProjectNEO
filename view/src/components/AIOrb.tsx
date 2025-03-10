import React from 'react';
import { motion } from 'framer-motion';

interface AIOrbProps {
  mood: 'normal' | 'creative' | 'offensive';
  isActive: boolean;
}

const AIOrb: React.FC<AIOrbProps> = ({ mood, isActive }) => {
  const moodGradients = {
    normal: 'from-cyan-400 to-blue-500',
    creative: 'from-purple-400 to-pink-500',
    offensive: 'from-red-400 to-orange-500',
  };

  return (
    <div className="relative w-16 h-16">
      <motion.div
        className={`absolute inset-0 rounded-full bg-gradient-to-br ${moodGradients[mood]}`}
        animate={{
          scale: isActive ? [1, 1.1, 1] : 1,
          rotate: 360,
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        <motion.div
          className="absolute inset-1 rounded-full bg-gray-900 flex items-center justify-center"
          animate={{
            scale: isActive ? [1, 0.9, 1] : 1,
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <motion.div
            className={`w-8 h-8 rounded-full bg-gradient-to-br ${moodGradients[mood]} opacity-75`}
            animate={{
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </motion.div>
      </motion.div>
      {[...Array(3)].map((_, index) => (
        <motion.div
          key={index}
          className={`absolute w-1 h-1 rounded-full bg-white`}
          animate={{
            rotate: 360,
            translateX: 32,
            translateY: 32,
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "linear",
            delay: index * 0.6,
          }}
        />
      ))}
    </div>
  );
};

export default AIOrb;

