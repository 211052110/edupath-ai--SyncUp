export default function SecondaryButton({ children, onClick, className = "", type = "button" }) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`h-[48px] px-[24px] rounded-full bg-transparent border border-border text-[14px] font-medium text-text-primary transition-all hover:bg-white/5 hover:-translate-y-[1px] active:translate-y-0 ${className}`}
    >
      {children}
    </button>
  );
}
