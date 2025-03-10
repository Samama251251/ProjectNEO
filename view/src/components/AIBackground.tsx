import React, { useEffect, useRef } from 'react';

interface AIBackgroundProps {
  mood: 'normal' | 'creative' | 'offensive';
}

const AIBackground: React.FC<AIBackgroundProps> = ({ mood }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles: Particle[] = [];
    const particleCount = 50;
    const maxDistance = 100;

    class Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      color: string;

      constructor() {
        this.x = Math.random() * (canvas?.width || 0);
        this.y = Math.random() * (canvas?.height || 0);
        this.vx = Math.random() * 2 - 1;
        this.vy = Math.random() * 2 - 1;
        this.size = Math.random() * 2 + 1;
        this.color = getParticleColor();
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (canvas && (this.x < 0 || this.x > canvas.width)) this.vx *= -1;
        if (canvas && (this.y < 0 || this.y > canvas.height)) this.vy *= -1;
      }

      draw() {
        if (!ctx) return;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
      }
    }

    function getParticleColor() {
      const colors = {
        normal: ['rgba(0, 255, 255, 0.3)', 'rgba(0, 200, 255, 0.3)'],
        creative: ['rgba(255, 0, 255, 0.3)', 'rgba(200, 0, 255, 0.3)'],
        offensive: ['rgba(255, 0, 0, 0.3)', 'rgba(255, 100, 0, 0.3)'],
      };
      const moodColors = colors[mood];
      return moodColors[Math.floor(Math.random() * moodColors.length)];
    }

    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }

    function drawLines() {
      if (!ctx) return;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < maxDistance) {
            ctx.beginPath();
            ctx.strokeStyle = particles[i].color;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
    }

    function animate() {
      if (!ctx) return;
      if (canvas) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
      
      for (const particle of particles) {
        particle.update();
        particle.draw();
      }

      drawLines();

      requestAnimationFrame(animate);
    }

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [mood]);

  return (
    <canvas ref={canvasRef} className="absolute inset-0 bg-black" />
  );
};

export default AIBackground;

