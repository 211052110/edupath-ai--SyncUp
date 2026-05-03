import { Bot, CheckCircle, XCircle, Lightbulb } from 'lucide-react';

export default function ChatBubble({ message, isAi, timestamp, feedback }) {
  if (isAi) {
    return (
      <div className="flex gap-3 mb-6">
        <div className="w-[28px] h-[28px] rounded-full bg-primary flex-shrink-0 flex items-center justify-center text-white mt-1">
          <Bot className="w-4 h-4" />
        </div>
        <div className="flex flex-col gap-2 max-w-[75%]">
          <div className="bg-elevated border border-border rounded-[16px] rounded-bl-[4px] p-[14px] px-[18px] text-[14px] text-text-primary leading-[1.6]">
            {message}
          </div>
          
          {feedback && feedback.confidence_score !== undefined && (
            <div className="bg-surface border border-border rounded-[12px] p-4 flex flex-col gap-3 mt-1">
               <div className="flex justify-between items-center border-b border-border pb-2 mb-1">
                  <span className="text-[12px] uppercase tracking-wider font-bold text-text-secondary">Evaluation</span>
                  <div className="flex items-center gap-2">
                     <span className="text-[12px] text-text-tertiary">Confidence Score</span>
                     <span className={`text-[13px] font-mono font-bold ${feedback.confidence_score >= 80 ? 'text-success' : feedback.confidence_score >= 50 ? 'text-warning' : 'text-destructive'}`}>
                        {feedback.confidence_score}/100
                     </span>
                  </div>
               </div>
               
               {feedback.strengths && feedback.strengths.length > 0 && (
                 <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-success shrink-0 mt-0.5" />
                    <div>
                       <span className="text-[13px] font-medium text-text-primary block mb-0.5">Strengths</span>
                       <ul className="list-disc pl-4">
                         {feedback.strengths.map((s, i) => (
                           <li key={i} className="text-[13px] text-text-secondary">{s}</li>
                         ))}
                       </ul>
                    </div>
                 </div>
               )}

               {feedback.weaknesses && feedback.weaknesses.length > 0 && (
                 <div className="flex items-start gap-2">
                    <XCircle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
                    <div>
                       <span className="text-[13px] font-medium text-text-primary block mb-0.5">Weaknesses</span>
                       <ul className="list-disc pl-4">
                         {feedback.weaknesses.map((w, i) => (
                           <li key={i} className="text-[13px] text-text-secondary">{w}</li>
                         ))}
                       </ul>
                    </div>
                 </div>
               )}

               {feedback.suggested_improvement && (
                 <div className="flex items-start gap-2 mt-1 bg-primary/10 border border-primary/20 p-3 rounded-[8px]">
                    <Lightbulb className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                    <div>
                       <span className="text-[13px] font-medium text-primary block mb-0.5">Improvement</span>
                       <p className="text-[13px] text-text-primary">{feedback.suggested_improvement}</p>
                    </div>
                 </div>
               )}
            </div>
          )}
          <span className="text-[11px] text-text-tertiary ml-1">{timestamp}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1 items-end mb-6">
      <div className="bg-primary rounded-[16px] rounded-br-[4px] p-[14px] px-[18px] text-[14px] text-white max-w-[75%]">
        {message}
      </div>
      <span className="text-[11px] text-text-tertiary mr-1">{timestamp}</span>
    </div>
  );
}
