import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, Wallet, Briefcase, Globe2, FileText, CheckCircle2, Info, Lightbulb, ExternalLink } from 'lucide-react';
import CircularScoreGauge from '../components/CircularScoreGauge';
import FormInput from '../components/FormInput';
import PrimaryButton from '../components/PrimaryButton';
import ProgressBar from '../components/ProgressBar';
import { loanService } from '../services/api';

const COUNTRIES = [
  { label: 'Germany 🇩🇪', value: 'Germany' },
  { label: 'USA 🇺🇸', value: 'USA' },
  { label: 'UK 🇬🇧', value: 'UK' },
  { label: 'Canada 🇨🇦', value: 'Canada' },
  { label: 'Australia 🇦🇺', value: 'Australia' },
  { label: 'Netherlands 🇳🇱', value: 'Netherlands' },
  { label: 'Singapore 🇸🇬', value: 'Singapore' },
  { label: 'Ireland 🇮🇪', value: 'Ireland' },
  { label: 'New Zealand 🇳🇿', value: 'New Zealand' },
  { label: 'Sweden 🇸🇪', value: 'Sweden' },
];

const LENDER_LINKS = {
  'Poonawalla Fincorp Education Loan': 'https://www.poonawallafincorp.com/education-loan',
  'HDFC Credila': 'https://www.hdfccredila.com',
  'Avanse Financial Services': 'https://www.avanse.com',
  'InCred Education Loan': 'https://www.incred.com/education-loan',
  'SBI Global Ed-Vantage': 'https://sbi.co.in/web/personal-banking/loans/education-loans/sbi-global-ed-vantage-scheme',
  'Prodigy Finance': 'https://prodigyfinance.com',
  'MPOWER Financing': 'https://www.mpowerfinancing.com',
  'Bank of Baroda Baroda Scholar': 'https://www.bankofbaroda.in/personal-banking/loans/education-loan/baroda-scholar',
};

const getClassification = (val) => {
  if (val <= 40) return { label: 'Poor', colorClass: 'text-destructive' };
  if (val <= 65) return { label: 'Average', colorClass: 'text-warning' };
  if (val <= 85) return { label: 'Good', colorClass: 'text-success' };
  return { label: 'Excellent', colorClass: 'text-primary' };
};

const getRiskColor = (risk) => {
  if (risk === 'Low Risk') return 'bg-success/20 text-success border-success/30';
  if (risk === 'Medium Risk') return 'bg-warning/20 text-warning border-warning/30';
  if (risk === 'High Risk') return 'bg-destructive/20 text-destructive border-destructive/30';
  return 'bg-surface border-border text-text-secondary';
};

export default function LoanScore() {
  const [formData, setFormData] = useState({
    gpa: '3.8',
    budget: '50000',
    country: 'Germany',
    workExp: '2',
    english: '7.5',
  });

  const [result, setResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const debounceRef = useRef(null);

  const handleRecalculate = async () => {
    if (isCalculating) return;
    setIsCalculating(true);
    setError(null);

    try {
      const payload = {
        gpa: Math.min(4.0, Math.max(0, parseFloat(formData.gpa) || 0)),
        annual_budget: Math.max(0, parseInt(formData.budget) || 0),
        target_country: formData.country,
        work_experience_years: Math.max(0, parseInt(formData.workExp) || 0),
        english_score: Math.min(9.0, Math.max(0, parseFloat(formData.english) || 0)),
      };

      const data = await loanService.calculateScore(payload);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to calculate score. Is the backend running?');
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => {
    handleRecalculate();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChange = (e, field) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  // Auto-recalculate 800ms after last input change
  const handleChangeWithDebounce = (e, field) => {
    handleChange(e, field);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => handleRecalculate(), 800);
  };

  const score = result?.overall_score ?? 0;
  const { label: scoreLabel, colorClass } = getClassification(score);
  const factors = result ? {
    academic:    result.factors.academic_record,
    financial:   result.factors.financial_stability,
    employment:  result.factors.employment_prospects,
    countryRisk: result.factors.country_risk,
    language:    result.factors.english_proficiency,
  } : { academic: 0, financial: 0, employment: 0, countryRisk: 0, language: 0 };

  return (
    <div className="flex-1 flex flex-col p-[48px] pt-8 max-w-[1000px] mx-auto w-full">
      {/* Hero */}
      <div className="flex flex-col items-center text-center mb-[48px]">
        <h1 className="text-[40px] font-display font-bold text-text-primary mb-12">Your Loan Eligibility Score</h1>
        <div className="relative mb-6">
          <div className="gradient-orb w-[200px] h-[200px] bg-primary top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-0 opacity-20"></div>
          <div className="relative z-10">
            <CircularScoreGauge
              score={isCalculating ? 0 : score}
              size={240}
              strokeWidth={12}
              label={isCalculating ? 'Calculating...' : `${scoreLabel} Eligibility`}
              showMax={true}
              colorClass={isCalculating ? 'text-text-primary' : colorClass}
            />
          </div>
        </div>

        {!isCalculating && result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-4 w-full max-w-[700px] mx-auto mt-4"
          >
            <div className="flex items-start gap-3 p-4 rounded-[12px] bg-primary/10 border border-primary/20 text-left">
              <Info className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-[14px] font-bold text-text-primary">Score Analysis</span>
                  {result.risk_level && (
                    <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium uppercase tracking-wider ${getRiskColor(result.risk_level)}`}>
                      {result.risk_level}
                    </span>
                  )}
                </div>
                <p className="text-[14px] text-text-secondary leading-relaxed">{result.explanation}</p>
              </div>
            </div>

            {result.improvement_suggestions?.length > 0 && (
              <div className="flex items-start gap-3 p-4 rounded-[12px] bg-elevated border border-border text-left">
                <Lightbulb className="w-5 h-5 text-warning shrink-0 mt-0.5" />
                <div className="w-full">
                  <span className="text-[14px] font-bold text-text-primary mb-2 block">Actionable Insights</span>
                  <ul className="flex flex-wrap gap-2">
                    {result.improvement_suggestions.map((s, idx) => (
                      <li key={idx} className="bg-surface border border-border rounded-full px-3 py-1.5 text-[12px] text-text-secondary flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary"></div>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-destructive/10 border border-destructive text-destructive text-sm max-w-[700px] w-full text-left">
            {error}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-[32px] mb-[32px]">
        {/* Form */}
        <div className="bg-surface border border-border rounded-[16px] p-[28px] shadow-card">
          <h2 className="text-[20px] font-display font-bold text-text-primary mb-6">Update Profile</h2>
          <div className="grid grid-cols-2 gap-x-4">
            <FormInput
              label="Current GPA"
              placeholder="3.8"
              suffix="/4.0"
              value={formData.gpa}
              onChange={(e) => handleChangeWithDebounce(e, 'gpa')}
              type="number"
              min="0" max="4" step="0.1"
            />
            <FormInput
              label="Annual Budget"
              placeholder="50,000"
              prefix="$"
              value={formData.budget}
              onChange={(e) => handleChangeWithDebounce(e, 'budget')}
              type="number"
              min="0"
            />
          </div>

          <div className="flex flex-col mb-4">
            <label className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-2 font-medium">Preferred Country</label>
            <select
              value={formData.country}
              onChange={(e) => handleChangeWithDebounce(e, 'country')}
              className="h-[48px] w-full rounded-[10px] bg-elevated border border-border text-[14px] text-text-primary px-4 focus:outline-none focus:border-primary focus:ring-[3px] focus:ring-primary/15 transition-all appearance-none"
            >
              {COUNTRIES.map(c => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-x-4 mb-6">
            <FormInput
              label="Work Experience"
              type="number"
              placeholder="2"
              suffix="yrs"
              value={formData.workExp}
              onChange={(e) => handleChangeWithDebounce(e, 'workExp')}
              min="0" max="20"
            />
            <FormInput
              label="English Score"
              placeholder="7.5"
              prefix="IELTS"
              value={formData.english}
              onChange={(e) => handleChangeWithDebounce(e, 'english')}
              type="number"
              min="0" max="9" step="0.5"
            />
          </div>

          <PrimaryButton className="w-full" onClick={handleRecalculate} disabled={isCalculating}>
            {isCalculating ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Recalculating...
              </span>
            ) : 'Recalculate Score'}
          </PrimaryButton>
        </div>

        {/* Breakdown */}
        <div className="bg-surface border border-border rounded-[16px] p-[28px] shadow-card flex flex-col">
          <h2 className="text-[20px] font-display font-bold text-text-primary mb-6">Score Breakdown</h2>
          <div className="flex-1 flex flex-col gap-6">
            <BreakdownRow icon={GraduationCap} label="Academic Record"      score={isCalculating ? 0 : factors.academic}    weight="30%" />
            <BreakdownRow icon={Wallet}        label="Financial Stability"   score={isCalculating ? 0 : factors.financial}   weight="25%" />
            <BreakdownRow icon={Briefcase}     label="Employment Prospects"  score={isCalculating ? 0 : factors.employment}  weight="20%" />
            <BreakdownRow icon={Globe2}        label="Country Risk"          score={isCalculating ? 0 : factors.countryRisk} weight="15%" />
            <BreakdownRow icon={FileText}      label="English Proficiency"   score={isCalculating ? 0 : factors.language}    weight="10%" />
          </div>
        </div>
      </div>

      {/* Lenders */}
      {result?.recommended_lenders?.length > 0 && (
        <div>
          <h2 className="text-[20px] font-display font-bold text-text-primary mb-6">Recommended Lenders</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {result.recommended_lenders.map((lender, i) => (
              <LenderCard key={i} lender={lender} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function BreakdownRow({ icon: Icon, label, score, weight }) {
  return (
    <div className="flex items-center gap-4">
      <div className="w-[40px] h-[40px] rounded-[10px] bg-elevated border border-border flex items-center justify-center text-text-secondary shrink-0">
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-center mb-2">
          <span className="text-[14px] font-medium text-text-primary">{label}</span>
          <div className="flex items-center gap-3">
            <span className="text-[13px] font-mono text-text-primary">{score}%</span>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-white/5 text-text-secondary border border-border">{weight}</span>
          </div>
        </div>
        <ProgressBar progress={score} />
      </div>
    </div>
  );
}

function LenderCard({ lender }) {
  const link = LENDER_LINKS[lender.name];
  return (
    <div className="p-5 rounded-[16px] bg-elevated border border-border card-hover">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-display font-bold text-[15px] text-text-primary leading-tight pr-2">{lender.name}</h3>
        <CheckCircle2 className="w-5 h-5 text-success shrink-0" />
      </div>
      <div className="flex flex-col gap-2 mb-4">
        <div className="flex justify-between">
          <span className="text-[13px] text-text-secondary">Interest Rate</span>
          <span className="text-[13px] font-mono text-text-primary">{lender.interest_rate}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[13px] text-text-secondary">Max Amount</span>
          <span className="text-[13px] font-mono text-text-primary">{lender.max_amount}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[13px] text-text-secondary">Processing</span>
          <span className="text-[13px] font-medium text-text-primary">{lender.processing_time}</span>
        </div>
      </div>
      {link && (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-[12px] text-primary hover:underline mt-1"
        >
          Apply Now <ExternalLink className="w-3 h-3" />
        </a>
      )}
    </div>
  );
}
