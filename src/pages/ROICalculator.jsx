import { useState, useEffect, useRef } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, Info } from 'lucide-react';
import FormInput from '../components/FormInput';
import PrimaryButton from '../components/PrimaryButton';
import MetricCard from '../components/MetricCard';
import { roiService } from '../services/api';

const COUNTRIES = ['USA', 'UK', 'Germany', 'Canada', 'Australia', 'Netherlands', 'Singapore', 'Ireland', 'New Zealand', 'Sweden'];

const FIELDS = [
  'Computer Science', 'Data Science', 'AI / Machine Learning',
  'Software Engineering', 'Business Administration', 'Finance',
  'Electrical Engineering', 'Mechanical Engineering',
  'Medicine', 'Law', 'Economics',
];

// Median starting salary benchmarks (USD) shown as hint to user
const SALARY_HINTS = {
  'USA': { 'Computer Science': 115000, 'Data Science': 112000, 'AI / Machine Learning': 130000, 'Business Administration': 85000, 'Finance': 92000, 'default': 78000 },
  'Germany': { 'Computer Science': 72000, 'Data Science': 70000, 'AI / Machine Learning': 78000, 'Business Administration': 58000, 'default': 52000 },
  'UK': { 'Computer Science': 65000, 'Data Science': 64000, 'AI / Machine Learning': 72000, 'Business Administration': 55000, 'default': 48000 },
  'Canada': { 'Computer Science': 90000, 'Data Science': 88000, 'AI / Machine Learning': 100000, 'Business Administration': 70000, 'default': 62000 },
  'Australia': { 'Computer Science': 88000, 'Data Science': 86000, 'AI / Machine Learning': 95000, 'Business Administration': 72000, 'default': 65000 },
};

function getBenchmark(country, field) {
  const c = SALARY_HINTS[country] || SALARY_HINTS['USA'];
  return c[field] || c['default'];
}

const fmt = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

export default function ROICalculator() {
  const [formData, setFormData] = useState({
    duration: '2', tuition: '35000', living: '1200',
    country: 'USA', field: 'Computer Science', salary: '115000',
  });
  const [result, setResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const debounceRef = useRef(null);

  const handleCalculate = async (data = formData) => {
    if (isCalculating) return;
    setIsCalculating(true);
    setError(null);
    try {
      const payload = {
        duration_years: Math.max(1, parseInt(data.duration) || 1),
        annual_tuition: Math.max(0, parseInt(data.tuition) || 0),
        monthly_living_costs: Math.max(0, parseInt(data.living) || 0),
        target_country: data.country,
        field_of_study: data.field,
        expected_salary: Math.max(0, parseInt(data.salary) || 0),
      };
      const response = await roiService.calculateROI(payload);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Failed to calculate ROI. Is the backend running?');
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => { handleCalculate(); }, []); // eslint-disable-line

  const handleChange = (e, field) => {
    const updated = { ...formData, [field]: e.target.value };
    setFormData(updated);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => handleCalculate(updated), 800);
  };

  // When country/field changes, auto-fill salary benchmark
  const handleSelectChange = (e, field) => {
    const updated = { ...formData, [field]: e.target.value };
    if (field === 'country' || field === 'field') {
      const country = field === 'country' ? e.target.value : formData.country;
      const fieldOfStudy = field === 'field' ? e.target.value : formData.field;
      updated.salary = String(getBenchmark(country, fieldOfStudy));
    }
    setFormData(updated);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => handleCalculate(updated), 800);
  };

  const metrics = result?.metrics;
  const insights = result?.insights;
  const chartData = result?.projection_data ?? [];
  const benchmark = getBenchmark(formData.country, formData.field);

  // Find break-even label for ReferenceLine (must match XAxis key exactly)
  const breakEvenX = metrics?.break_even_year
    ? `Y${Math.round(metrics.break_even_year)}`
    : null;

  return (
    <div className="flex-1 flex flex-col p-[48px] pt-8">
      <div className="mb-[48px]">
        <h1 className="text-[40px] font-display font-bold text-text-primary">Study Abroad ROI Calculator</h1>
        <p className="text-[15px] text-text-secondary mt-2">Is your degree worth the investment? Find out.</p>
      </div>

      <div className="flex gap-[32px] flex-1">
        {/* Input Panel */}
        <div className="w-[40%] bg-surface border border-border rounded-[16px] p-[28px] shadow-card flex flex-col">
          <h2 className="text-[20px] font-display font-bold text-text-primary mb-6">Investment Variables</h2>
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive text-destructive text-sm">{error}</div>
          )}
          <div className="flex-1 flex flex-col gap-2">
            <FormInput label="Course Duration" type="number" placeholder="2" suffix="yrs" min="1" max="10"
              value={formData.duration} onChange={(e) => handleChange(e, 'duration')} />
            <FormInput label="Annual Tuition" placeholder="35000" prefix="$" type="number" min="0"
              value={formData.tuition} onChange={(e) => handleChange(e, 'tuition')} />
            <FormInput label="Living Costs / Month" placeholder="1200" prefix="$" type="number" min="0"
              value={formData.living} onChange={(e) => handleChange(e, 'living')} />

            <div className="flex flex-col mb-1">
              <label className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-2 font-medium">Target Country</label>
              <select value={formData.country} onChange={(e) => handleSelectChange(e, 'country')}
                className="h-[48px] w-full rounded-[10px] bg-elevated border border-border text-[14px] text-text-primary px-4 focus:outline-none focus:border-primary appearance-none">
                {COUNTRIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>

            <div className="flex flex-col mb-1">
              <label className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-2 font-medium">Field of Study</label>
              <select value={formData.field} onChange={(e) => handleSelectChange(e, 'field')}
                className="h-[48px] w-full rounded-[10px] bg-elevated border border-border text-[14px] text-text-primary px-4 focus:outline-none focus:border-primary appearance-none">
                {FIELDS.map(f => <option key={f}>{f}</option>)}
              </select>
            </div>

            <div>
              <FormInput label="Expected Post-grad Salary" placeholder="92000" prefix="$" type="number" min="0"
                value={formData.salary} onChange={(e) => handleChange(e, 'salary')} />
              <div className="flex items-center gap-1.5 mt-1 ml-1">
                <Info className="w-3 h-3 text-text-tertiary" />
                <span className="text-[11px] text-text-tertiary">
                  {formData.field} median in {formData.country}: {fmt(benchmark)}/yr
                </span>
              </div>
            </div>
          </div>

          <PrimaryButton className="w-full mt-6" onClick={() => handleCalculate()} disabled={isCalculating}>
            {isCalculating ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Calculating...
              </span>
            ) : 'Calculate ROI'}
          </PrimaryButton>
        </div>

        {/* Results Panel */}
        <div className="w-[60%] flex flex-col gap-[24px]">
          <div className="grid grid-cols-3 gap-[16px]">
            <MetricCard title="Total Investment"  value={fmt(metrics?.total_investment ?? 0)}          accentClass="from-warning to-destructive" className="!p-5 !pb-6" />
            <MetricCard title="10-yr Earnings"    value={fmt(metrics?.ten_year_earnings ?? 0)}         accentClass="from-primary to-secondary"   className="!p-5 !pb-6" />
            <MetricCard title="10-yr ROI"         value={`${metrics?.ten_year_roi_percentage ?? 0}%`}  accentClass="from-success to-primary"     className="!p-5 !pb-6" />
          </div>

          {!isCalculating && insights && (
            <div className="bg-primary/10 border border-primary/20 rounded-[16px] p-5 flex flex-col gap-3">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-5 h-5 text-primary" />
                <h3 className="text-[16px] font-bold text-text-primary">Investment Analysis</h3>
              </div>
              <p className="text-[14px] text-text-secondary"><strong className="text-text-primary font-medium">Insight: </strong>{insights.insight_text}</p>
              <p className="text-[14px] text-text-secondary"><strong className="text-text-primary font-medium">Recommendation: </strong>{insights.recommendation}</p>
              <p className="text-[14px] text-text-secondary"><strong className="text-text-primary font-medium">vs Market: </strong>{insights.comparison}</p>
            </div>
          )}

          {/* Chart */}
          <div className="flex-1 bg-surface border border-border rounded-[16px] p-[28px] shadow-card min-h-[350px] flex flex-col">
            <h3 className="text-[16px] font-display font-bold text-text-primary mb-6">Cost vs Earnings Projection</h3>
            <div className="flex-1 w-full min-h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorEarnings" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#3ECF8E" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3ECF8E" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#F59E0B" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="year" stroke="#8A8FA8" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                  <YAxis stroke="#8A8FA8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={v => `$${Math.round(v / 1000)}k`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#13141F', borderColor: '#232538', borderRadius: '12px', boxShadow: '0 4px 24px rgba(0,0,0,0.4)' }}
                    itemStyle={{ color: '#F0F1FA', fontFamily: 'var(--font-mono)' }}
                    labelStyle={{ color: '#8A8FA8', marginBottom: '4px' }}
                    cursor={{ stroke: '#232538', strokeWidth: 1, strokeDasharray: '4 4' }}
                    formatter={v => fmt(v)}
                  />
                  {breakEvenX && chartData.some(d => d.year === breakEvenX) && (
                    <ReferenceLine
                      x={breakEvenX}
                      stroke="#5B6AF0"
                      strokeDasharray="4 4"
                      label={{ position: 'top', value: `Break-even ~Y${Math.round(metrics.break_even_year)}`, fill: '#5B6AF0', fontSize: 12, fontWeight: 500, offset: 10 }}
                    />
                  )}
                  <Area type="monotone" dataKey="cost"     name="Cumulative Cost"     stroke="#F59E0B" strokeWidth={2} fillOpacity={1} fill="url(#colorCost)" />
                  <Area type="monotone" dataKey="earnings" name="Cumulative Earnings"  stroke="#3ECF8E" strokeWidth={2} fillOpacity={1} fill="url(#colorEarnings)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* EMI Strip */}
          <div className="bg-surface border border-border rounded-[16px] p-[28px] shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-[16px] font-display font-bold text-text-primary mb-1">Loan Payoff Timeline</h3>
                <p className="text-[13px] text-text-secondary">Reducing-balance EMI at 11.5% p.a. over {metrics?.loan_duration_years ?? 7} years</p>
              </div>
              <div className="flex gap-8">
                <div>
                  <div className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-1">Monthly EMI</div>
                  <div className="text-[20px] font-mono text-text-primary">{fmt(metrics?.monthly_emi ?? 0)}</div>
                </div>
                <div>
                  <div className="text-[12px] text-text-secondary uppercase tracking-[0.08em] mb-1">Break-even</div>
                  <div className="text-[20px] font-mono text-text-primary">Y{metrics?.break_even_year ?? '—'}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
