import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function CircularScoreGauge({ score = 0, size = 200, strokeWidth = 10, label, subtext, showMax = false, colorClass = "text-primary" }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  useEffect(() => {
    if (score === 0) {
      const t = setTimeout(() => setAnimatedScore(0), 0);
      return () => clearTimeout(t);
    }

    let start = 0;
    const duration = 1200;
    const increment = score / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(start);
      }
    }, 16);

    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className="flex flex-col items-center justify-center relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <defs>
          <linearGradient id={`gauge-gradient-${size}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#5B6AF0" />
            <stop offset="100%" stopColor="#3ECF8E" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={`url(#gauge-gradient-${size})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-[48px] font-mono leading-none mb-1 ${colorClass}`}>
          {Math.round(animatedScore)}
          {showMax && <span className="text-[20px] text-text-tertiary">/100</span>}
        </span>
        {label && <span className={`text-[13px] ${colorClass} mt-1 font-medium`}>{label}</span>}
        {subtext && <span className="text-[11px] text-text-tertiary mt-1">{subtext}</span>}
      </div>
    </div>
  );
}
