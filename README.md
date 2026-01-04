# AI Earbud Assistant

Real-time AI assistant for in-ear responses using OpenAI Realtime API, FastAPI, and Streamlit.

## Features

- 🎤 Real-time voice interaction
- 🤖 AI-powered question detection and response
- 📄 Context-aware responses
- 🎧 Text-to-speech for in-ear feedback
- 📊 Conversation history tracking
- ⚡ WebSocket support for real-time communication

## Project Structure

```
ai-earbud-assistant/
├── backend/           # FastAPI backend
│   ├── main.py       # Main application
│   ├── config.py     # Configuration
│   ├── models.py     # Data models
│   ├── services/     # Business logic
│   └── routes/       # API routes
├── frontend/         # Streamlit frontend
│   └── app.py       # Main UI
├── requirements.txt
└── .env
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-earbud-assistant
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Running the Application

### Start Backend (Terminal 1):
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend (Terminal 2):
```bash
streamlit run frontend/app.py
```

OR

.venv\Scripts\python.exe -m streamlit run frontend/app.py

The application will be available at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Start Listening**: Click the microphone button to start recording
2. **Ask Questions**: Speak naturally or type your questions
3. **Upload Context**: Add context files to improve AI responses
4. **View History**: Check conversation history in the sidebar

## API Endpoints

### REST API
- `POST /api/question` - Submit a question
- `POST /api/context` - Upload context file
- `GET /api/history` - Get conversation history
- `DELETE /api/history` - Clear history
- `GET /api/health` - Health check

### WebSocket
- `WS /ws/{client_id}` - Real-time communication

## Configuration

Edit `.env` file to configure:
- `OPENAI_API_KEY` - Your OpenAI API key
- `BACKEND_PORT` - Backend server port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 8501)

## Development

### Run Tests:
```bash
pytest tests/
```

### Format Code:
```bash
black backend/ frontend/
```

### Lint Code:
```bash
flake8 backend/ frontend/
```

## Deployment

### Using Docker:
```bash
docker-compose up -d
```

### Manual Deployment:
1. Set environment variables
2. Run backend: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
3. Run frontend: `streamlit run frontend/app.py --server.port 8501`

## Troubleshooting

**Issue:** WebSocket connection fails
**Solution:** Check if backend is running and firewall allows connections

**Issue:** Audio not working
**Solution:** Grant microphone permissions in browser

**Issue:** API key error
**Solution:** Verify OPENAI_API_KEY in .env file

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.