export default function MetricCard({ title, value, subtext, accentClass = "from-primary to-secondary", children, className = "" }) {
  return (
    <div className={`relative p-[28px] rounded-[16px] bg-surface border border-border shadow-card overflow-hidden card-hover ${className}`}>
      <div className={`absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r ${accentClass}`}></div>
      <h3 className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-2">{title}</h3>
      {value && <div className="text-[36px] font-mono text-text-primary mb-1">{value}</div>}
      {subtext && <div className="text-[13px] text-text-tertiary mb-4">{subtext}</div>}
      {children}
    </div>
  );
}
