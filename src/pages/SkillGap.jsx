import { useState } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import { Brain, CheckCircle, XCircle, Lightbulb, Send } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const ROLES = ['Data Scientist', 'ML Engineer', 'Software Engineer', 'AI Researcher', 'Data Analyst', 'Full Stack Developer'];
const COUNTRIES = ['USA', 'Germany', 'UK', 'Canada', 'Australia'];

export default function SkillGap() {
  const [form, setForm] = useState({ resume_text: '', target_role: 'Data Scientist', target_country: 'USA' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!form.resume_text.trim() || form.resume_text.length < 10) {
      setError('Paste at least a short resume or skill summary.');
      return;
    }
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await fetch(`${API_BASE}/skill-gap/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error('Request failed');
      setResult(await res.json());
    } catch {
      setError('Backend unavailable. Start the FastAPI server.');
    } finally {
      setLoading(false);
    }
  };

  const radarData = result?.radar_data?.map(d => ({
    skill: d.skill, You: d.user_score, Industry: d.industry_score,
  })) ?? [];

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Skill Gap Analyzer</h1>
        <p className="text-text-secondary text-sm mt-1">Paste your resume or skill list — AI maps gaps vs industry benchmarks.</p>
      </div>

      {/* Form */}
      <div className="bg-surface border border-border rounded-2xl p-5 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-text-secondary mb-1 block">Target Role</label>
            <select
              value={form.target_role}
              onChange={e => setForm(f => ({ ...f, target_role: e.target.value }))}
              className="w-full bg-base border border-border rounded-xl px-3 py-2 text-sm text-text-primary"
            >
              {ROLES.map(r => <option key={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-text-secondary mb-1 block">Target Country</label>
            <select
              value={form.target_country}
              onChange={e => setForm(f => ({ ...f, target_country: e.target.value }))}
              className="w-full bg-base border border-border rounded-xl px-3 py-2 text-sm text-text-primary"
            >
              {COUNTRIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="text-xs font-medium text-text-secondary mb-1 block">Resume / Skill Summary</label>
          <textarea
            rows={8}
            placeholder="Paste your resume text, skills, or a brief profile here..."
            value={form.resume_text}
            onChange={e => setForm(f => ({ ...f, resume_text: e.target.value }))}
            className="w-full bg-base border border-border rounded-xl px-3 py-2 text-sm text-text-primary resize-none"
          />
          <p className="text-xs text-text-secondary mt-1">{form.resume_text.length}/5000</p>
        </div>
        {error && <p className="text-destructive text-sm">{error}</p>}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="flex items-center gap-2 bg-primary text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          <Brain className="w-4 h-4" />
          {loading ? 'Analyzing...' : 'Analyze Skill Gap'}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Score + Recommendation */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-surface border border-border rounded-2xl p-4 text-center">
              <p className="text-4xl font-bold text-primary">{result.overall_match}%</p>
              <p className="text-xs text-text-secondary mt-1">Overall Match</p>
            </div>
            <div className="col-span-2 bg-surface border border-border rounded-2xl p-4 flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-warning shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-semibold text-text-secondary mb-1">Top Recommendation</p>
                <p className="text-sm text-text-primary">{result.top_recommendation}</p>
              </div>
            </div>
          </div>

          {/* Radar Chart */}
          <div className="bg-surface border border-border rounded-2xl p-5">
            <p className="text-sm font-semibold text-text-primary mb-4">Skills Radar — You vs Industry</p>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#2a2a3a" />
                <PolarAngleAxis dataKey="skill" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <Radar name="You" dataKey="You" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                <Radar name="Industry" dataKey="Industry" stroke="#10b981" fill="#10b981" fillOpacity={0.15} />
                <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3a', borderRadius: 8 }} />
              </RadarChart>
            </ResponsiveContainer>
            <div className="flex gap-4 justify-center mt-2">
              <span className="flex items-center gap-1.5 text-xs text-text-secondary"><span className="w-3 h-3 rounded-full bg-[#6366f1]" />You</span>
              <span className="flex items-center gap-1.5 text-xs text-text-secondary"><span className="w-3 h-3 rounded-full bg-[#10b981]" />Industry Benchmark</span>
            </div>
          </div>

          {/* Matched / Missing */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-surface border border-border rounded-2xl p-4">
              <p className="text-xs font-semibold text-success mb-3 flex items-center gap-1.5"><CheckCircle className="w-4 h-4" />Matched Skills</p>
              <div className="space-y-1">
                {result.matched_skills.length ? result.matched_skills.map(s => (
                  <span key={s} className="inline-block bg-success/10 text-success text-xs px-2.5 py-1 rounded-full mr-1.5 mb-1">{s}</span>
                )) : <p className="text-xs text-text-secondary">None matched benchmark threshold.</p>}
              </div>
            </div>
            <div className="bg-surface border border-border rounded-2xl p-4">
              <p className="text-xs font-semibold text-destructive mb-3 flex items-center gap-1.5"><XCircle className="w-4 h-4" />Skill Gaps</p>
              <div className="space-y-1">
                {result.missing_skills.length ? result.missing_skills.map(s => (
                  <span key={s} className="inline-block bg-destructive/10 text-destructive text-xs px-2.5 py-1 rounded-full mr-1.5 mb-1">{s}</span>
                )) : <p className="text-xs text-success">No critical gaps found!</p>}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
