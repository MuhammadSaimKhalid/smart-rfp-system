import json
from apps.api.schemas.chat import RFPState
from services.review.llm_client import complete_json

SYSTEM_PROMPT = """You are an expert RFP Consultant AI. Your goal is to help the user define a robust Request for Proposal (RFP).
You will receive the CURRENT STATE of the RFP and the user's latest message.

Your responsibilities:
1. **Analyze** the user's input to extract these 5 key fields if present:
   - **Title**: A clear, professional title for the RFP.
   - **Scope**: A detailed description of the project scope.
   - **Requirements**: A list of specific deliverables or requirements.
   - **Budget**: The estimated budget (e.g., "$50,000" or "TBD").
   - **Timeline End**: The due date in YYYY-MM-DD format (use last day of month if unspecified).

2. **Update** the `updated_state` object. If the user provides new info, overwrite the corresponding field. If they don't mention a field, KEEP the value from `current_state`.
   - **Crucial:** If the user provides a detailed block of text, extract ALL 5 fields from it if possible. Do not wait to ask for them one by one if the information is already there.

3. **Reply** to the user conversationally (`reply` field).
   - If fields are missing, ask for them politely (one or two at a time).
   - If the user provided everything, verify it and suggest next steps (like "This looks great! Review the draft on the right.").
   - Keep answers professional, encouraging, and concise.

**Current RFP State:**
{current_state_json}

**Respond with STRICT JSON ONLY:**
{
  "reply": "Your conversational response here...",
  "updated_state": {
      "title": "...",
      "scope": "...",
      "requirements": ["req1", "req2"],
      "budget": "...",
      "timeline_end": "..."
  }
}
"""

def consult_on_rfp(message: str, current_state: RFPState, history: list[dict]) -> dict:
    """
    Sends message + state to LLM, returns {reply: str, updated_state: dict}
    """
    import traceback
    
    try:
        # Debug logging
        with open("/tmp/rfp_debug.log", "a") as f:
            f.write(f"Incoming message: {message}\n")
            f.write(f"Current State: {current_state}\n")

        state_json = current_state.model_dump_json()
        
        # Construct conversation history string for context
        # Limit history to last 10 messages to save context window
        history_text = ""
        for msg in history[-10:]:
            role = "AI" if msg.get("role") == "ai" else "User"
            text = msg.get("text", "")
            history_text += f"{role}: {text}\n"

        # prompt construction
        final_prompt = f"""
Conversation History:
{history_text}

User's Latest Message:
{message}
"""
        
        formatted_system = SYSTEM_PROMPT.replace("{current_state_json}", state_json)

        response = complete_json(formatted_system, final_prompt, temperature=0.7)
        
        # Validation fallback
        if "reply" not in response or "updated_state" not in response:
             raise ValueError("Missing keys in AI response")
             
        return response

    except Exception as e:
        with open("/tmp/rfp_debug.log", "a") as f:
            f.write(f"ERROR: {str(e)}\n")
            f.write(traceback.format_exc())
            
        print(f"AI Error: {e}")
        # Fallback if AI fails
        return {
            "reply": "I'm having trouble processing that specific request. Please try again later.",
            "updated_state": current_state.model_dump()
        }
