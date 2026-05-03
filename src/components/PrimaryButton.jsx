export default function PrimaryButton({ children, onClick, className = "", type = "button" }) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`h-[48px] px-[24px] rounded-full bg-gradient-to-br from-primary to-secondary text-[14px] font-semibold text-white transition-all hover:brightness-110 hover:-translate-y-[1px] hover:shadow-[0_0_15px_rgba(91,106,240,0.4)] active:translate-y-0 active:shadow-none ${className}`}
    >
      {children}
    </button>
  );
}
