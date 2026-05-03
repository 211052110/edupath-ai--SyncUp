export default function FormInput({ label, type = "text", placeholder, value, onChange, prefix, suffix, className = "" }) {
  return (
    <div className={`flex flex-col mb-4 ${className}`}>
      {label && (
        <label className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-2 font-medium">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {prefix && (
          <span className="absolute left-3 text-text-tertiary text-[14px]">{prefix}</span>
        )}
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className={`h-[48px] w-full rounded-[10px] bg-elevated border border-border text-[14px] text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-primary focus:ring-[3px] focus:ring-primary/15 transition-all ${
            prefix ? "pl-8" : "pl-4"
          } ${suffix ? "pr-12" : "pr-4"}`}
        />
        {suffix && (
          <span className="absolute right-4 text-text-tertiary text-[14px] font-mono">{suffix}</span>
        )}
      </div>
    </div>
  );
}
