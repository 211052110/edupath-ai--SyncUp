export default function TagPill({ children, className = "" }) {
  return (
    <span className={`inline-flex items-center justify-center h-[28px] px-[12px] rounded-full bg-primary/10 border border-primary/20 text-[12px] font-medium text-secondary whitespace-nowrap ${className}`}>
      {children}
    </span>
  );
}
