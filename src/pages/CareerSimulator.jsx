import { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend
} from 'recharts';
import { TrendingUp, DollarSign, Clock, Award, Lightbulb, BarChart2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const FIELDS    = ['Computer Science', 'Data Science', 'AI / Machine Learning', 'Business', 'Finance'];
const COUNTRIES = ['USA', 'Germany', 'UK', 'Canada', 'Australia'];
const ROLES     = ['Data Scientist', 'ML Engineer', 'Software Engineer', 'AI Researcher', 'Data Analyst', 'Full Stack Developer'];

const GRADE_COLOR = { 'A+': 'text-emerald-400', A: 'text-green-400', 'B+': 'text-yellow-400', B: 'text-orange-400', C: 'text-red-400' };

const fmt = (n) => n >= 1000 ? `$${(n / 1000).toFixed(0)}K` : `$${n}`;
const fmtFull = (n) => `$${Number(n).toLocaleString()}`;

export default function CareerSimulator() {
  const [form, setForm] = useState({
    gpa: 3.5, field_of_study: 'Computer Science', target_country: 'USA',
    work_experience_years: 1, program_duration_years: 2,
    annual_tuition_usd: 35000, monthly_living_usd: 1500,
    target_role: 'Data Scientist', skills_text: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await fetch(`${API_BASE}/career-sim/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, gpa: parseFloat(form.gpa),
          annual_tuition_usd: parseFloat(form.annual_tuition_usd),
          monthly_living_usd: parseFloat(form.monthly_living_usd) }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result?.projections?.map(p => ({
    year: `Yr ${p.year}`,
    Salary: Math.round(p.salary),
    'Net Position': Math.round(p.net_position),
    'Cumulative Earnings': Math.round(p.cumulative_earnings),
  })) ?? [];

  const breakEvenYear = result ? `Yr ${Math.ceil(result.break_even_years)}` : null;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Career Simulator</h1>
        <p className="text-text-secondary text-sm mt-1">10-year financial projection + job demand index + skill roadmap.</p>
      </div>

      {/* Form */}
      <div className="bg-surface border border-border rounded-2xl p-5 grid grid-cols-3 gap-4">
        {[
          { label: 'Field of Study',     key: 'field_of_study',         type: 'select', opts: FIELDS },
          { label: 'Target Country',     key: 'target_country',         type: 'select', opts: COUNTRIES },
          { label: 'Target Role',        key: 'target_role',            type: 'select', opts: ROLES },
          { label: 'GPA',                key: 'gpa',                    type: 'number', min: 0, max: 4,      step: 0.1 },
          { label: 'Annual Tuition ($)', key: 'annual_tuition_usd',     type: 'number', min: 0, max: 100000, step: 1000 },
          { label: 'Monthly Living ($)', key: 'monthly_living_usd',     type: 'number', min: 0, max: 5000,   step: 100 },
          { label: 'Program Duration',   key: 'program_duration_years', type: 'select', opts: ['1','2','3','4'] },
          { label: 'Work Exp (yrs)',     key: 'work_experience_years',  type: 'select', opts: ['0','1','2','3','4','5'] },
        ].map(({ label, key, type, opts, min, max, step }) => (
          <div key={key}>
            <label className="text-xs font-medium text-text-secondary mb-1 block">{label}</label>
            {type === 'select' ? (
              <select value={form[key]} onChange={e => set(key, isNaN(e.target.value) ? e.target.value : Number(e.target.value))}
                className="w-full bg-base border border-border rounded-xl px-3 py-2 text-sm text-text-primary">
                {opts.map(o => <option key={o}>{o}</option>)}
              </select>
            ) : (
              <input type="number" value={form[key]} min={min} max={max} step={step}
                onChange={e => set(key, parseFloat(e.target.value))}
                className="w-full bg-base border border-border rounded-xl px-3 py-2 text-sm text-text-primary" />
            )}
          </div>
        ))}

        <div className="col-span-3">
          {error && <p className="text-destructive text-sm mb-2">{error}</p>}
          <button onClick={handleSubmit} disabled={loading}
            className="flex items-center gap-2 bg-primary text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:opacity-90 disabled:opacity-50">
            <TrendingUp className="w-4 h-4" />
            {loading ? 'Simulating...' : 'Run Career Simulation'}
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* KPI row */}
          <div className="grid grid-cols-6 gap-3">
            {[
              { icon: DollarSign, label: 'Starting Salary', value: fmtFull(result.predicted_starting_salary), sub: 'per year' },
              { icon: TrendingUp, label: '5-Year Salary',   value: fmtFull(result.salary_at_5yr),             sub: 'per year' },
              { icon: TrendingUp, label: '10-Year Salary',  value: fmtFull(result.salary_at_10yr),            sub: 'per year' },
              { icon: Clock,      label: 'Break Even',      value: `${result.break_even_years.toFixed(1)} yrs`, sub: 'after graduation' },
              { icon: BarChart2,  label: '10-yr ROI',       value: `${result.roi_percent}%`,                  sub: 'return on investment' },
              { icon: Award,      label: 'Career Grade',    value: result.career_grade,                       sub: `Demand ${result.demand_index}/100`, grade: true },
            ].map(({ icon: Icon, label, value, sub, grade }) => (
              <div key={label} className="bg-surface border border-border rounded-2xl p-3 text-center">
                <Icon className="w-4 h-4 text-primary mx-auto mb-1" />
                <p className={`text-lg font-bold ${grade ? GRADE_COLOR[value] || 'text-primary' : 'text-primary'}`}>{value}</p>
                <p className="text-[10px] text-text-secondary leading-tight mt-0.5">{label}</p>
                <p className="text-[10px] text-text-secondary opacity-60">{sub}</p>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="bg-surface border border-border rounded-2xl p-4 flex gap-3">
            <Lightbulb className="w-5 h-5 text-warning shrink-0 mt-0.5" />
            <p className="text-sm text-text-primary">{result.summary}</p>
          </div>

          {/* Chart */}
          <div className="bg-surface border border-border rounded-2xl p-5">
            <p className="text-sm font-semibold text-text-primary mb-4">10-Year Career Projection</p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                <XAxis dataKey="year" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <YAxis tickFormatter={fmt} tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3a', borderRadius: 8 }}
                  formatter={(v) => fmtFull(v)}
                />
                <Legend />
                {breakEvenYear && (
                  <ReferenceLine x={breakEvenYear} stroke="#f59e0b" strokeDasharray="4 4"
                    label={{ value: 'Break Even', fill: '#f59e0b', fontSize: 10 }} />
                )}
                <Line type="monotone" dataKey="Salary" stroke="#6366f1" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Net Position" stroke="#10b981" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Cumulative Earnings" stroke="#f59e0b" strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Skills */}
          <div className="bg-surface border border-border rounded-2xl p-4">
            <p className="text-sm font-semibold text-text-primary mb-3">Top Skills to Add for {form.target_role} in {form.target_country}</p>
            <div className="flex flex-wrap gap-2">
              {result.top_skills_to_add.map(s => (
                <span key={s} className="bg-primary/10 text-primary text-xs px-3 py-1.5 rounded-full font-medium">{s}</span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
