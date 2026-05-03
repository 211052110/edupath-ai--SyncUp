import { useState, useRef, useEffect, useCallback } from 'react';
import { Target, Wallet, Home, BookOpen, Map, CheckCircle, Mic, Send, Star, RotateCcw, TrendingUp } from 'lucide-react';
import ChatBubble from '../components/ChatBubble';
import ProgressBar from '../components/ProgressBar';
import { chatService } from '../services/api';

const TOPICS = [
  {
    id: 'study_motivation', icon: Target, label: 'Study Motivation',
    questions: [
      "Why have you chosen to study abroad rather than in your home country?",
      "Why did you select this particular university and program?",
      "How does this course align with your previous academic background?",
    ]
  },
  {
    id: 'financial_proof', icon: Wallet, label: 'Financial Proof', active: true,
    questions: [
      "Who is sponsoring your education, and what is their relationship to you?",
      "What is the total estimated cost for your first year, and how are these funds arranged?",
      "Do you have any liquid assets or blocked accounts set up? Please explain.",
      "How do I know you won't become a public burden during your stay?",
    ]
  },
  {
    id: 'ties_to_home', icon: Home, label: 'Ties to Home Country',
    questions: [
      "What ties do you have to your home country that will ensure your return?",
      "Do you have family, property, or a job offer waiting for you back home?",
    ]
  },
  {
    id: 'course_choice', icon: BookOpen, label: 'Course Choice',
    questions: [
      "Why did you choose this specific field of study?",
      "How will this degree benefit your career back home?",
    ]
  },
  {
    id: 'future_plans', icon: Map, label: 'Future Plans',
    questions: [
      "What are your plans after completing your degree?",
      "Do you intend to work in the destination country after graduation?",
    ]
  },
  {
    id: 'mock_interview', icon: CheckCircle, label: 'Mock Interview', recommended: true,
    questions: [
      "This is a full mock interview. I will assess your overall visa readiness. Are you ready to begin?",
      "Why should I grant you a student visa?",
      "Walk me through your complete financial plan for the duration of your studies.",
      "What happens if your sponsoring family member loses their income mid-way through your studies?",
      "Have you applied for any other visas before? Were any rejected?",
    ]
  },
];

const generateSessionId = () => `session-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

export default function VisaChat() {
  const [activeTopic, setActiveTopic] = useState(TOPICS[1]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [messages, setMessages] = useState(() => [{
    id: 1,
    text: TOPICS[1].questions[0],
    isAi: true,
    time: now(),
  }]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [sessionId] = useState(generateSessionId);
  const endRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const switchTopic = useCallback((topic) => {
    if (topic.id === activeTopic.id) return;
    setActiveTopic(topic);
    setCurrentQIndex(0);
    setProgress(0);
    setScoreHistory([]);
    setMessages([{
      id: Date.now(),
      text: topic.questions[0],
      isAi: true,
      time: now(),
    }]);
    inputRef.current?.focus();
  }, [activeTopic.id]);

  const appendMessage = (msg) => setMessages(prev => [...prev, msg]);

  const detectIntent = (text, explicit) => {
    if (explicit && explicit !== 'answer') return explicit;
    const l = text.toLowerCase();
    if (/\b(not sure|help|hint|guidance|confused)\b/.test(l)) return 'help';
    if (/\b(next|skip|move on|move to next|continue)\b/.test(l)) return 'navigation';
    return 'answer';
  };

  const handleSend = async (forcedInput = null, explicitIntent = 'answer') => {
    const text = forcedInput ?? input;
    const intent = detectIntent(text, explicitIntent);
    if ((!text.trim() && intent === 'answer') || isTyping) return;

    if (text.trim()) {
      appendMessage({ id: Date.now(), text, isAi: false, time: now() });
    }
    if (!forcedInput) setInput('');
    setIsTyping(true);

    try {
      const chatHistory = messages.map(m => ({
        role: m.isAi ? 'assistant' : 'user',
        content: m.text,
      }));

      const response = await chatService.sendMessage({
        session_id: sessionId,
        topic_id: activeTopic.id,
        current_question: activeTopic.questions[currentQIndex],
        message: text || intent,
        intent,
        chat_history: chatHistory,
      });

      const feedback = intent === 'answer' && response.confidence_score != null ? {
        confidence_score: response.confidence_score,
        strengths: response.strengths,
        weaknesses: response.weaknesses,
        suggested_improvement: response.suggested_improvement,
      } : null;

      appendMessage({
        id: Date.now() + 1,
        text: response.message + (response.tip ? `\n\n💡 Tip: ${response.tip}` : ''),
        isAi: true,
        feedback,
        time: now(),
      });

      if (feedback?.confidence_score != null) {
        setScoreHistory(prev => [...prev, feedback.confidence_score]);
      }

      setProgress(response.topic_progress ?? 0);

      // Advance question on navigation OR strong answer (score >= 80)
      const shouldAdvance =
        intent === 'navigation' ||
        (intent === 'answer' && response.confidence_score >= 80);

      if (shouldAdvance && currentQIndex < activeTopic.questions.length - 1) {
        const next = currentQIndex + 1;
        setCurrentQIndex(next);
        setTimeout(() => {
          appendMessage({
            id: Date.now() + 2,
            text: activeTopic.questions[next],
            isAi: true,
            time: now(),
          });
        }, 900);
      } else if (shouldAdvance && currentQIndex === activeTopic.questions.length - 1) {
        setProgress(100);
        setTimeout(() => {
          appendMessage({
            id: Date.now() + 2,
            text: "You've completed all questions for this topic. Well done! You can switch to another topic or review your performance.",
            isAi: true,
            time: now(),
          });
        }, 900);
      }
    } catch (err) {
      appendMessage({
        id: Date.now() + 1,
        text: err.message?.includes('API') ? err.message : "Connection error. Please check your backend is running.",
        isAi: true,
        time: now(),
      });
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const avgScore = scoreHistory.length
    ? Math.round(scoreHistory.reduce((a, b) => a + b, 0) / scoreHistory.length)
    : null;

  const handleReset = async () => {
    try { await chatService.resetSession(sessionId); } catch (_) {}
    setCurrentQIndex(0);
    setProgress(0);
    setScoreHistory([]);
    setMessages([{ id: Date.now(), text: activeTopic.questions[0], isAi: true, time: now() }]);
  };

  return (
    <div className="flex-1 flex h-[100vh]">
      {/* Sidebar */}
      <div className="w-[280px] border-r border-border bg-base flex flex-col p-6 h-full">
        <h2 className="text-[18px] font-display font-bold text-text-primary mb-6">Visa Interview Prep</h2>
        <div className="flex-1 flex flex-col gap-2 overflow-y-auto pr-2">
          {TOPICS.map(topic => {
            const Icon = topic.icon;
            const isActive = activeTopic.id === topic.id;
            return (
              <button
                key={topic.id}
                onClick={() => switchTopic(topic)}
                className={`flex items-center gap-3 p-3 rounded-[12px] text-left transition-all ${
                  isActive
                    ? 'bg-primary/10 border border-primary/30 text-text-primary'
                    : 'bg-elevated border border-transparent text-text-secondary hover:bg-white/5'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isActive ? 'bg-primary text-white' : 'bg-surface border border-border'}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-[14px] font-medium truncate">{topic.label}</div>
                  <div className="text-[11px] text-text-tertiary">{topic.questions.length} questions</div>
                </div>
                {topic.recommended && (
                  <span className="text-[10px] px-2 py-1 rounded-full bg-warning/20 text-warning font-medium shrink-0">Rec</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Stats */}
        <div className="pt-6 mt-6 border-t border-border space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[13px] text-text-secondary font-medium">Topic Progress</span>
              <span className="text-[13px] font-mono text-text-primary">{progress}%</span>
            </div>
            <ProgressBar progress={progress} />
          </div>
          {avgScore !== null && (
            <div className="flex items-center justify-between p-3 rounded-[10px] bg-elevated border border-border">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" />
                <span className="text-[13px] text-text-secondary">Avg Score</span>
              </div>
              <span className={`text-[14px] font-mono font-bold ${avgScore >= 80 ? 'text-success' : avgScore >= 55 ? 'text-warning' : 'text-destructive'}`}>
                {avgScore}/100
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-surface">
        {/* Header */}
        <div className="h-[72px] border-b border-border px-8 flex items-center justify-between shrink-0 bg-base/50 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <h1 className="text-[20px] font-display font-bold text-text-primary">{activeTopic.label}</h1>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-success/10 border border-success/20">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
              <span className="text-[12px] text-success font-medium">AI Interviewer Active</span>
            </div>
            <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-elevated border border-border">
              <Star className="w-3 h-3 text-warning" />
              <span className="text-[12px] text-text-primary font-mono">
                {Math.min(currentQIndex + 1, activeTopic.questions.length)}/{activeTopic.questions.length}
              </span>
            </div>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 h-[36px] px-4 rounded-full border border-border text-text-secondary text-[13px] font-medium hover:border-primary hover:text-primary transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-8 flex flex-col">
          {messages.map(msg => (
            <ChatBubble key={msg.id} message={msg.text} isAi={msg.isAi} timestamp={msg.time} feedback={msg.feedback} />
          ))}
          {isTyping && (
            <div className="flex gap-3 mb-6">
              <div className="w-[28px] h-[28px] rounded-full bg-primary flex-shrink-0 flex items-center justify-center text-white mt-1">
                <Target className="w-4 h-4" />
              </div>
              <div className="bg-elevated border border-border rounded-[16px] rounded-bl-[4px] p-[14px] px-[18px] flex gap-1 items-center">
                <span className="w-2 h-2 bg-text-tertiary rounded-full dot-typing"></span>
                <span className="w-2 h-2 bg-text-tertiary rounded-full dot-typing"></span>
                <span className="w-2 h-2 bg-text-tertiary rounded-full dot-typing"></span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <div className="p-8 pt-0 shrink-0">
          <div className="flex gap-2 mb-4 flex-wrap">
            <Chip onClick={() => handleSend("I'm not sure how to answer that.", 'help')}>I'm not sure</Chip>
            <Chip onClick={() => handleSend("Can you give me a hint?", 'help')}>Give me a hint</Chip>
            <Chip onClick={() => handleSend("Let's move to the next question.", 'navigation')}>Next question</Chip>
          </div>
          <div className="relative flex items-center">
            <input
              ref={inputRef}
              type="text"
              placeholder="Type your answer..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
              disabled={isTyping}
              className="w-full h-[56px] bg-elevated border border-border rounded-full pl-6 pr-[120px] text-[15px] text-text-primary focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
            />
            <div className="absolute right-2 flex items-center gap-2">
              <button className="w-[40px] h-[40px] rounded-full flex items-center justify-center text-text-tertiary hover:text-primary hover:bg-primary/10 transition-colors">
                <Mic className="w-5 h-5" />
              </button>
              <button
                onClick={() => handleSend()}
                disabled={isTyping || !input.trim()}
                className="w-[40px] h-[40px] rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white hover:brightness-110 transition-all disabled:opacity-50"
              >
                <Send className="w-4 h-4 ml-[-2px]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Chip({ children, onClick }) {
  return (
    <button onClick={onClick} className="h-[32px] px-4 rounded-full border border-border bg-elevated text-[13px] text-text-secondary hover:text-text-primary hover:border-primary/50 transition-colors">
      {children}
    </button>
  );
}

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
