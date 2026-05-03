const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
const API_KEY  = import.meta.env.VITE_API_KEY  || '';

async function fetchWithConfig(endpoint, data) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'API Request Failed');
  }
  return response.json();
}

export const loanService = {
  calculateScore: (data) => fetchWithConfig('/loan/calculate-score', data),
};
export const roiService = {
  calculateROI: (data) => fetchWithConfig('/roi/calculate', data),
};
export const chatService = {
  sendMessage: (data) => fetchWithConfig('/chat/message', data),
  resetSession: (session_id) => fetchWithConfig('/chat/reset', { session_id }),
};
export const universityQAService = {
  ask: (question) => fetchWithConfig('/university-qa/ask', { question }),
};
export const skillGapService = {
  analyze: (data) => fetchWithConfig('/skill-gap/analyze', data),
};

export const careerSimService = {
  simulate: (data) => fetchWithConfig('/career-sim/simulate', data),
};
