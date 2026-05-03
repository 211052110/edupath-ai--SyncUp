export default function ProgressBar({ progress = 0, className = "" }) {
  return (
    <div className={`h-[6px] rounded-full bg-border overflow-hidden ${className}`}>
      <div 
        className="h-full bg-gradient-to-r from-primary to-success transition-all duration-800 ease-out"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}
