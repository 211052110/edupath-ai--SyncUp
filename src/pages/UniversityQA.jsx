import { useState, useRef, useEffect } from 'react';
import { Search, BookOpen, Lightbulb, AlertCircle, Send } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const SUGGESTED = [
  "What are visa requirements for Germany as an Indian student?",
  "Compare MIT vs Stanford CS MS programs",
  "What is the Poonawalla Fincorp loan process?",
  "Which country has highest ROI for CS degree?",
  "How does UK Graduate Route visa work?",
  "What scholarships are available for Indian students?",
  "What is the DAAD scholarship for Germany?",
  "Canada PGWP eligibility after graduation?",
];

const CONFIDENCE_STYLE = {
  high:   'bg-success/10 border-success/30 text-success',
  medium: 'bg-warning/10 border-warning/30 text-warning',
  low:    'bg-destructive/10 border-destructive/30 text-destructive',
};

export default function UniversityQA() {
  const [question, setQuestion]   = useState('');
  const [history, setHistory]     = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]         = useState(null);
  const endRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, isLoading]);

  const ask = async (q) => {
    const text = (q ?? question).trim();
    if (!text || isLoading) return;
    setQuestion('');
    setError(null);
    setIsLoading(true);
    setHistory(prev => [...prev, { role: 'user', text }]);

    try {
      const res = await fetch(`${API_BASE}/university-qa/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      });
      if (!res.ok) throw new Error('Request failed');
      const data = await res.json();
      setHistory(prev => [...prev, { role: 'ai', ...data }]);
    } catch (e) {
      setError('Backend unavailable. Make sure the server is running.');
      setHistory(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex-1 flex flex-col h-[100vh] max-w-[860px] mx-auto w-full p-8 pt-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-[32px] font-display font-bold text-text-primary flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-primary" />
          University Q&amp;A
        </h1>
        <p className="text-[14px] text-text-secondary mt-1">
          RAG-powered answers from curated university, visa &amp; loan knowledge base.
        </p>
      </div>

      {/* Suggested chips — only when no history */}
      {history.length === 0 && (
        <div className="mb-6">
          <p className="text-[12px] text-text-tertiary uppercase tracking-widest mb-3">Suggested questions</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED.map((s, i) => (
              <button key={i} onClick={() => ask(s)}
                className="h-[32px] px-4 rounded-full border border-border bg-elevated text-[12px] text-text-secondary hover:text-text-primary hover:border-primary/50 transition-colors">
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat history */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-5 pb-4">
        {history.map((msg, i) => (
          msg.role === 'user' ? (
            <div key={i} className="flex justify-end">
              <div className="max-w-[75%] bg-primary/10 border border-primary/20 rounded-[16px] rounded-br-[4px] px-5 py-3 text-[14px] text-text-primary">
                {msg.text}
              </div>
            </div>
          ) : (
            <div key={i} className="flex flex-col gap-2">
              <div className="bg-elevated border border-border rounded-[16px] rounded-bl-[4px] px-5 py-4">
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-primary shrink-0" />
                  <span className="text-[12px] font-medium text-text-secondary uppercase tracking-wider">AI Answer</span>
                  <span className={`ml-auto text-[10px] px-2 py-0.5 rounded-full border font-medium uppercase ${CONFIDENCE_STYLE[msg.confidence] || ''}`}>
                    {msg.confidence} confidence
                  </span>
                </div>
                <p className="text-[14px] text-text-primary leading-relaxed">{msg.answer}</p>
                {msg.sources?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-2">Sources used</p>
                    <div className="flex flex-col gap-1">
                      {msg.sources.map((s, si) => (
                        <p key={si} className="text-[11px] text-text-tertiary">
                          <span className="text-primary font-mono">[{si+1}]</span> {s}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="bg-elevated border border-border rounded-[16px] rounded-bl-[4px] px-5 py-4 flex gap-1 items-center">
              <span className="w-2 h-2 bg-text-tertiary rounded-full dot-typing"></span>
              <span className="w-2 h-2 bg-text-tertiary rounded-full dot-typing"></span>
              <span className="w-2 h-2 bg-text-tertiary rounded-full dot-typing"></span>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-[13px]">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="pt-4 border-t border-border">
        <div className="relative flex items-center">
          <Search className="absolute left-4 w-4 h-4 text-text-tertiary pointer-events-none" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask about universities, visas, scholarships, loans..."
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && ask()}
            disabled={isLoading}
            className="w-full h-[52px] bg-elevated border border-border rounded-full pl-11 pr-[56px] text-[14px] text-text-primary focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
          />
          <button onClick={() => ask()} disabled={isLoading || !question.trim()}
            className="absolute right-2 w-[38px] h-[38px] rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white hover:brightness-110 transition-all disabled:opacity-40">
            <Send className="w-4 h-4 ml-[-1px]" />
          </button>
        </div>
      </div>
    </div>
  );
}
