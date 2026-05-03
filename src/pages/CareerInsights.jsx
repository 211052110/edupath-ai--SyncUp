import { useState } from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from 'recharts';
import { Briefcase, CheckCircle2, AlertTriangle, Lightbulb, ChevronDown } from 'lucide-react';
import PrimaryButton from '../components/PrimaryButton';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const ROLES = [
  'Data Scientist', 'ML Engineer', 'Software Engineer',
  'AI Researcher', 'Data Analyst', 'Full Stack Developer',
];
const COUNTRIES = ['USA', 'Germany', 'UK', 'Canada', 'Australia'];

const SALARY_DATA = [
  { role: 'Data Sci',    USA: 120, UK: 85,  GER: 95  },
  { role: 'ML Eng',      USA: 135, UK: 95,  GER: 105 },
  { role: 'SDE',         USA: 110, UK: 80,  GER: 90  },
  { role: 'Analyst',     USA: 85,  UK: 60,  GER: 70  },
];

const PLACEHOLDER = `Paste your resume or skills summary here.

Example:
- 2 years experience with Python, PyTorch, TensorFlow
- Built CNN models for image classification (92% accuracy)
- Used LangChain and FAISS for RAG pipelines
- AWS Cloud Practitioner certified
- Published research on NLP at college symposium
- Experience with React, FastAPI, PostgreSQL`;

export default function CareerInsights() {
  const [resumeText, setResumeText]   = useState('');
  const [targetRole, setTargetRole]   = useState('Data Scientist');
  const [targetCountry, setCountry]   = useState('USA');
  const [result, setResult]           = useState(null);
  const [isLoading, setIsLoading]     = useState(false);
  const [error, setError]             = useState(null);

  const analyze = async () => {
    if (!resumeText.trim() || isLoading) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/skill-gap/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          target_role: targetRole,
          target_country: targetCountry,
        }),
      });
      if (!res.ok) throw new Error('Analysis failed');
      setResult(await res.json());
    } catch (e) {
      setError('Backend unavailable. Make sure the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const radarData = result?.radar_data?.map(d => ({
    subject: d.skill,
    You: d.user_score,
    Industry: d.industry_score,
  })) ?? [];

  return (
    <div className="flex-1 flex flex-col p-[48px] pt-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-end flex-wrap gap-4">
        <div>
          <h1 className="text-[40px] font-display font-bold text-text-primary">Career & Skill Gap Analyzer</h1>
          <p className="text-[15px] text-text-secondary mt-2">Paste your resume → get live skill gap vs industry benchmark.</p>
        </div>
        <div className="flex gap-2">
          {COUNTRIES.map(c => (
            <button key={c} onClick={() => setCountry(c)}
              className={`px-3 py-1.5 rounded-[10px] text-[13px] font-medium border transition-colors ${
                targetCountry === c
                  ? 'bg-primary/10 border-primary/30 text-primary'
                  : 'bg-surface border-border text-text-secondary hover:text-text-primary'
              }`}>
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-[32px] flex-1">
        {/* Input Panel */}
        <div className="w-[38%] flex flex-col gap-4">
          {/* Role selector */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[12px] text-text-secondary uppercase tracking-[0.08em] font-medium">Target Role</label>
            <div className="relative">
              <select value={targetRole} onChange={e => setTargetRole(e.target.value)}
                className="w-full h-[44px] rounded-[10px] bg-elevated border border-border text-[14px] text-text-primary px-4 pr-10 focus:outline-none focus:border-primary appearance-none">
                {ROLES.map(r => <option key={r}>{r}</option>)}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary pointer-events-none" />
            </div>
          </div>

          {/* Resume input */}
          <div className="flex flex-col gap-1.5 flex-1">
            <label className="text-[12px] text-text-secondary uppercase tracking-[0.08em] font-medium">
              Resume / Skills Summary
            </label>
            <textarea
              value={resumeText}
              onChange={e => setResumeText(e.target.value)}
              placeholder={PLACEHOLDER}
              className="flex-1 min-h-[280px] bg-elevated border border-border rounded-[12px] p-4 text-[13px] text-text-primary placeholder-text-tertiary focus:outline-none focus:border-primary transition-colors resize-none font-mono leading-relaxed"
            />
          </div>

          <PrimaryButton onClick={analyze} disabled={isLoading || !resumeText.trim()} className="w-full">
            {isLoading
              ? <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing with spaCy...
                </span>
              : 'Analyze Skill Gap'}
          </PrimaryButton>

          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-[13px]">
              {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="flex-1 flex flex-col gap-[24px]">
          {/* Overall match + recommendation */}
          {result && (
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-1 bg-surface border border-border rounded-[16px] p-5 flex flex-col items-center justify-center">
                <div className="text-[48px] font-mono font-bold text-text-primary">{result.overall_match}%</div>
                <div className="text-[13px] text-text-secondary mt-1">Role Match</div>
                <div className={`mt-2 text-[11px] px-3 py-1 rounded-full border font-medium ${
                  result.overall_match >= 70 ? 'bg-success/10 border-success/30 text-success'
                  : result.overall_match >= 45 ? 'bg-warning/10 border-warning/30 text-warning'
                  : 'bg-destructive/10 border-destructive/30 text-destructive'
                }`}>
                  {result.overall_match >= 70 ? 'Strong' : result.overall_match >= 45 ? 'Moderate' : 'Needs Work'}
                </div>
              </div>
              <div className="col-span-2 bg-primary/10 border border-primary/20 rounded-[16px] p-5 flex flex-col justify-between">
                <div className="flex items-center gap-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-primary" />
                  <span className="text-[13px] font-bold text-text-primary">Top Recommendation</span>
                </div>
                <p className="text-[13px] text-text-secondary leading-relaxed">{result.top_recommendation}</p>
                <div className="flex gap-4 mt-3 pt-3 border-t border-primary/20">
                  <div className="flex-1">
                    <p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1.5">Matched Skills</p>
                    <div className="flex flex-wrap gap-1">
                      {result.matched_skills.map(s => (
                        <span key={s} className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-success/10 border border-success/20 text-success">
                          <CheckCircle2 className="w-2.5 h-2.5" />{s}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1.5">Gaps</p>
                    <div className="flex flex-wrap gap-1">
                      {result.missing_skills.map(s => (
                        <span key={s} className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-warning/10 border border-warning/20 text-warning">
                          <AlertTriangle className="w-2.5 h-2.5" />{s}
                        </span>
                      ))}
                      {result.missing_skills.length === 0 && (
                        <span className="text-[12px] text-success">No major gaps!</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Radar chart */}
          <div className="bg-surface border border-border rounded-[16px] p-[28px] shadow-card">
            <h2 className="text-[18px] font-display font-bold text-text-primary mb-6">
              {result ? `Skill Radar — You vs ${targetRole}` : 'Skill Radar (submit to see your scores)'}
            </h2>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={result ? radarData : STATIC_RADAR}>
                  <PolarGrid stroke="var(--color-border)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }} />
                  <Radar name="Industry" dataKey="Industry" stroke="#5B6AF0" fill="#5B6AF0" fillOpacity={0.15} strokeWidth={2} />
                  <Radar name="You" dataKey="You" stroke="#3ECF8E" fill="#3ECF8E" fillOpacity={0.25} strokeWidth={2} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--color-elevated)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-mono)' }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex gap-6 mt-2 justify-center">
              <LegendDot color="#3ECF8E" label="Your Profile" />
              <LegendDot color="#5B6AF0" label="Industry Benchmark" />
            </div>
          </div>

          {/* Static salary comparison — always visible */}
          <div className="bg-surface border border-border rounded-[16px] p-[28px] shadow-card">
            <h2 className="text-[18px] font-display font-bold text-text-primary mb-6">Salary Benchmarks (k USD)</h2>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={SALARY_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                  <XAxis dataKey="role" stroke="var(--color-text-tertiary)" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                  <YAxis stroke="var(--color-text-tertiary)" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--color-elevated)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-mono)' }}
                    cursor={{ fill: 'var(--color-border)', opacity: 0.4 }} />
                  <Bar dataKey="USA" fill="var(--color-primary)" radius={[4,4,0,0]} />
                  <Bar dataKey="UK"  fill="var(--color-secondary)" radius={[4,4,0,0]} />
                  <Bar dataKey="GER" fill="#3ECF8E" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const STATIC_RADAR = [
  { subject: 'Python',        You: 0, Industry: 85 },
  { subject: 'ML / AI',       You: 0, Industry: 88 },
  { subject: 'Data Science',  You: 0, Industry: 90 },
  { subject: 'Cloud',         You: 0, Industry: 70 },
  { subject: 'Research',      You: 0, Industry: 75 },
  { subject: 'Communication', You: 0, Industry: 72 },
];

function LegendDot({ color, label }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
      <span className="text-[12px] text-text-secondary">{label}</span>
    </div>
  );
}
