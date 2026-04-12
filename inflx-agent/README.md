# AutoStream AI Lead Gen

Hey! This is my submission for the AI Lead Generation Agent. I built this using LangGraph for the backend control flow, FastAPI for the endpoints, and Next.js for the interface. Since I was running into rate-limit bottlenecks with the big providers, I fully wired this to run on **Groq** using the Llama-3.1-8B-Instant model, which makes it blazing fast.

Here's how to get it running.

## Local Setup

### 1. The Backend
First, pop open your terminal and head into the `backend` folder. You'll want to set up a virtual environment so nothing conflicts:
```bash
cd backend
python -m venv venv

# On Mac/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install all the required packages listed in requirements.txt
pip install -r requirements.txt
```

You'll need an environment file to hook up the Groq API. Just make a `.env` file right inside the `backend` folder with this:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant
KNOWLEDGE_BASE_PATH=./app/rag/knowledge_base.json
```

Then, fire up the server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. The Frontend
Open a totally new terminal window, go into the `frontend` folder, and run:
```bash
cd frontend
npm install
npm run dev
```
That's it! Just open `http://localhost:3000` to start chatting with the agent.

---

## Why LangGraph? (Architecture)

I decided to go with LangGraph instead of traditional, straight-line RAG frameworks because lead generation isn't a straight line. It's heavily stateful. By structuring the AI logic as a Finite State Machine (FSM), I could create distinct, isolated nodes for `extractor`, `intent`, `retriever`, and `responder`. 

This keeps things perfectly deterministic. If the intent router figures out you're just asking a random question about pricing, it won't ever hallucinate aggressively asking for your email. 

### How Retrieval (RAG) Actually Works Here
Instead of using a clumsy vector database with cosine similarity searches (which often pull irrelevant chunks of text), my retrieval is built on a **Deterministic Tool-Calling Router**:
1. **Intent Gating**: LangGraph only fires the `retriever` node if the earlier `intent` node classifies the user's message as an *"inquiry"*. 
2. **Dynamic Tool Selection**: I wrote five strict Python functions loaded against my JSON knowledge base (`get_pricing`, `get_plans`, `get_policy`, etc). Each is decorated with LangChain's `@tool` wrapper and a thorough docstring.
3. **The LLM Router**: By binding these tools to the Groq model, I force the LLM to mathematically analyze the user's question and select the absolute best function to run.
4. **Perfect Context Injection**: Because the LLM is explicitly picking a function rather than guessing text distance, it gets deterministic accuracy. This perfectly parsed data is passed safely down to the `responder` node which reliably streams out an accurate, grounded answer.

State management across these nodes is completely immutable. Behind the scenes, the graph holds an `AgentState` dictionary containing the raw message history, parsed intent, retrieved context, and passively collected variables. Every time the frontend sends a chat message, FastAPI pushes the current state entirely through the LangGraph cycle, updating the dictionary, and cleanly streaming the result back seamlessly.

---

## WhatsApp Deployment Approach

If I needed to hook this exact agent up to WhatsApp instead of a Next.js web application, I'd use a Webhook pattern with the Meta WhatsApp Cloud API. 

Here is exactly how I would build it:
1. **The Webhook Route**: I'd throw a new `POST /webhook/whatsapp` endpoint into my FastAPI app. Meta hits this URL whenever someone sends a WhatsApp message to our business number.
2. **Session Handling**: I'd use the person's phone number as the unique `session_id`. Using a fast store like Redis, I'd fetch their exact `AgentState` history based on that phone number, so the agent remembers who they are.
3. **Graph Execution**: I'd pass the new text from WhatsApp directly into my existing LangGraph pipeline. It would classify intent, run RAG, and extract leads without changing a single line of the graph logic!
4. **Sending Replies**: The exact moment LangGraph finishes running and spits out an `AIMessage`, I'd trigger a simple HTTP request back to Meta's API to immediately zap that generated text back to the user's WhatsApp.
5. **Capturing Leads**: If the user drops their email while chatting, my silent `LeadCapture` node executes organically mid-graph and pushes their details to wherever I need them (like Google Sheets), completely invisible to the WhatsApp interface.

---

## Evaluation Criteria Addressed

1. **Agent reasoning & intent detection**: Intent is continuously evaluated via a dedicated LangGraph node analyzing the last 6 conversation turns, enabling dynamic switching between casual chat, RAG inquiries, and high-intent sales capture.
2. **Correct use of RAG**: RAG is decoupled from the main LLM loop; it strictly executes via deterministic LangChain `@tool` binding only when the intent classifier identifies an inquiry, guaranteeing zero hallucinated data fetches.
3. **Clean state management**: LangGraph acts as a strict Finite State Machine. The `AgentState` dictionary enforces purely immutable state transitions for messages, confidence scores, and passively extracted lead data cleanly across FastAPI boundaries.
4. **Proper tool calling logic**: Tools are rigorously defined with strict docstrings for the Groq/LLaMA engine, ensuring the AI autonomously delegates tasks (like `get_pricing` or `get_plans`) only when mathematically confident.
5. **Code clarity & structure**: The architecture is fully modularized—nodes (intent, extractor, retriever, responder), utilities, models, and graph routing logic are completely isolated in their own cleanly-typed Python files.
6. **Real-world deployability**: Production-ready configuration including Next.js Server-Sent Events (SSE) streaming, asynchronous Python endpoints, CORS security, and comprehensive environment variable abstraction for instant cloud deployment.
