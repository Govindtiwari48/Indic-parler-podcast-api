# Indic Parler TTS Podcast API

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)
![Model](https://img.shields.io/badge/Model-AI4Bharat%20Parler%20TTS-orange.svg)

A high-performance FastAPI server that uses the `ai4bharat/indic-parler-tts` model to generate multi-speaker podcasts in Hindi from a text script.

## Features

* **Multi-Speaker Podcast Generation:** Processes scripts with `[Speaker]` tags to create conversations with different voices.
* **Single-Speaker Mode:** Generates audio for a single block of text using a specified voice.
* **REST API Endpoint:** Provides a simple and robust API endpoint (`/generate-podcast/`) to generate and receive audio files.
* **Automatic API Docs:** Comes with interactive Swagger UI documentation for easy testing and integration.
* **Optimized Model Loading:** The large AI model is loaded only once at server startup for fast and efficient inference on subsequent requests.

## Tech Stack

* **Backend:** Python 3.9+
* **API Framework:** FastAPI
* **Server:** Uvicorn
* **AI/ML:** PyTorch, Hugging Face (Transformers, Parler-TTS)

---

## 🚀 Step-by-Step Setup Instructions

Follow these terminal commands to set up and run the project locally.

### Step 1: Prerequisites

Make sure you have Python 3.9+ installed on your system:

```bash
python --version
# or
python3 --version
```

**Note:** An NVIDIA GPU with CUDA is highly recommended for acceptable performance. The model will run on CPU, but audio generation will be significantly slower.

### Step 2: Clone the Repository

Clone this repository to your local machine:

```bash
git clone <your-repository-url>
cd podcast_api
```

### Step 3: Create Virtual Environment (Recommended)

Create and activate a virtual environment to isolate your project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 4: Install Python Dependencies

Install the required packages from the requirements file:

```bash
pip install -r requirements.txt
```

### Step 5: Install Parler TTS Library

Install the parler-tts library directly from GitHub:

```bash
pip install git+https://github.com/huggingface/parler-tts.git
```

### Step 6: Start the Server

Run the FastAPI server using uvicorn:

```bash
uvicorn app:app --reload
```

**What this command does:**
- `uvicorn`: The ASGI server that runs the FastAPI application
- `app:app`: Refers to the `app` object inside the `app.py` file
- `--reload`: Automatically restarts the server when you make code changes

### Step 7: Verify Installation

Once the server starts successfully, you should see output similar to:

```
🚀 Server starting up: Loading AI model...
Using device: cuda
✅ AI model and tokenizers loaded successfully!
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

The server will be running at: **http://127.0.0.1:8000**

---

## 📝 Important Notes

### Initial Model Download
On the first run, the server will automatically download the `ai4bharat/indic-parler-tts` model (~3.75 GB). This may take several minutes depending on your internet connection. Subsequent startups will be much faster as the model will be cached locally.

### Performance Considerations
- The server automatically detects if a CUDA-enabled GPU is available
- If no GPU is found, it defaults to CPU mode
- Audio generation on CPU can be very slow (several minutes for short scripts)
- GPU acceleration provides much faster generation times

---

## 🔧 Using the API

### 1. Interactive API Documentation (Swagger UI)

The easiest way to test the endpoint:

1. Open your browser and navigate to: **http://127.0.0.1:8000/docs**
2. Click on the `POST /generate-podcast/` endpoint to expand it
3. Click "Try it out"
4. Modify the request body with your script and settings
5. Click "Execute" to generate and download the audio file

### 2. Example Request Body

```json
{
  "script": "[Female Expressive] नमस्कार दोस्तों! यह एक परीक्षण है। [Male Energetic] आशा है कि यह काम करेगा।",
  "mode": "Podcast Mode",
  "single_speaker": "Female Expressive",
  "output_filename": "api_test.wav"
}
```

### 3. API Endpoint Details

- **Endpoint:** `POST /generate-podcast/`
- **Content-Type:** `application/json`
- **Success Response:** `200 OK` - Returns the generated audio file (`audio/wav`)
- **Error Response:** `500 Internal Server Error` - Returns JSON with error details

### 4. Example curl Request

Test the API from your terminal:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate-podcast/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "script": "[Female Expressive] नमस्कार! यह कर्ल से एक परीक्षण है।",
    "mode": "Single Speaker"
  }' \
  --output my_podcast.wav
```

This command sends the request and saves the returned audio directly to `my_podcast.wav`.

---

## 🎤 Available Voice Options

The API supports the following pre-configured voices:

- **Female Expressive**: Clear, expressive female voice with moderate pace
- **Male Energetic**: Clear male voice with slightly fast pace and energetic tone
- **Happy Female**: Happy and cheerful female voice with high energy
- **Formal News Male**: Formal, clear male voice with measured pace for news delivery

---

## 📂 Project Structure

```
podcast_api/
├── app.py             # Main FastAPI application file
├── requirements.txt   # Python package dependencies
├── README.md          # This documentation file
└── api_output.wav     # Generated audio file (created after first API call)
```

---

## 🛠️ Troubleshooting

### Common Issues:

1. **CUDA Out of Memory**: Reduce the text chunk size or use CPU mode
2. **Model Download Fails**: Check your internet connection and try again
3. **Import Errors**: Ensure all dependencies are installed correctly
4. **Slow Generation**: Use GPU acceleration for better performance

### Getting Help:

- Check the FastAPI documentation: https://fastapi.tiangolo.com/
- Parler TTS GitHub: https://github.com/huggingface/parler-tts
- AI4Bharat Indic Parler TTS: https://huggingface.co/ai4bharat/indic-parler-tts

---

## 📄 License

This project uses the AI4Bharat Indic Parler TTS model. Please refer to the respective licenses of the dependencies and models used.
