# Agani A.I. — Personal AI Assistant

Agani A.I. is a Python-based personal AI assistant designed to simplify everyday computer operations through voice and text commands. It combines predefined commands with AI-powered responses.

## Features

- **Website Access:** Open websites using simple commands.
- **Application Launcher:** Open supported Windows applications.
- **Folder Access:** Open commonly used folders.
- **File Management:** Find, open, and delete files.
- **System Controls:** Check the date and time, take screenshots, and manage supported volume and brightness settings.
- **Voice Interaction:** Speech recognition and text-to-speech support.
- **Memory System:** Store, recall, and remove user-provided information.
- **AI-Powered Responses:** Uses Ollama with the `llama3.2` model to answer general queries.

## Technologies Used

- **Python** — Core programming language
- **SpeechRecognition** — Speech input processing
- **Vosk** — Offline speech recognition support
- **pyttsx3** — Text-to-speech
- **Ollama** — AI-powered responses
- **PyAutoGUI** — Keyboard, mouse, and screenshot automation
- **Requests** — HTTP requests
- **Feedparser** — RSS and Atom feed processing

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ashish-vaghjiyani/Agani-AI.git
```

### 2. Navigate to the Project Directory

```bash
cd Agani-AI
```

### 3. Install Dependencies

If `requirements.txt` is available, run:

```bash
pip install -r requirements.txt
```

### 4. Configure the Environment

- Install Python and the required dependencies.
- Configure Ollama and the `llama3.2` model for AI responses.
- Set up the required Vosk speech-recognition model.
- Update local file paths according to your computer.

### 5. Run the Assistant

```bash
python main.py
```

**Note:** Some features require Windows, compatible audio devices, and correctly configured model files.

## Project Objective

The objective of Agani A.I. is to simplify everyday computer tasks using Python, system automation, voice interaction, memory functionality, and AI-based responses.

## Future Improvements

- Improve voice recognition and command handling.
- Add more useful commands and features.
- Improve error handling and portability.
- Enhance the memory system and user experience.

## Developer

**Ashish Vaghjiyani**

B.Tech Computer Engineering Student

---

*Agani A.I. — Making everyday computer tasks simpler with Python and AI.*
