# Step 1: Import necessary libraries for API and TTS
import torch
import numpy as np
import soundfile as sf
import re
from typing import List
import warnings
import os
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Hugging Face model imports
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

warnings.filterwarnings('ignore')

# --- GLOBAL VARIABLES AND MODEL LOADING ---

# This dictionary will hold our loaded model and tokenizers
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This function runs ONCE when the server starts.
    # It's the perfect place to load our large AI model.
    print("🚀 Server starting up: Loading AI model...")
    
    # Setup device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load the Parler TTS model
    model_name = "ai4bharat/indic-parler-tts"
    ml_models['model'] = ParlerTTSForConditionalGeneration.from_pretrained(model_name).to(device)
    ml_models['tokenizer'] = AutoTokenizer.from_pretrained(model_name)
    ml_models['description_tokenizer'] = AutoTokenizer.from_pretrained(ml_models['model'].config.text_encoder._name_or_path)
    ml_models['device'] = device
    
    print("✅ AI model and tokenizers loaded successfully!")
    
    yield
    
    # This part runs when the server shuts down (optional cleanup)
    print("🌙 Server shutting down...")
    ml_models.clear()

# Initialize the FastAPI app with the lifespan event handler
app = FastAPI(lifespan=lifespan)


# --- DATA MODELS FOR API REQUEST ---

# This defines the structure of the JSON data we expect in a request.
class PodcastRequest(BaseModel):
    script: str
    mode: str = "Podcast Mode"
    single_speaker: str = "Female Expressive"
    output_filename: str = "api_output.wav"


# --- HELPER FUNCTIONS (Adapted from your Colab notebook) ---

SPEAKERS = {
    "Female Expressive": "Divya speaks in a clear, expressive female voice with moderate pace. The recording is of very high quality with no background noise.",
    "Male Energetic": "Rohit speaks in a clear male voice with slightly fast pace and energetic tone. The recording is very close and clear.",
    "Happy Female": "Divya speaks in a happy and cheerful female voice with high energy and moderate speed. The recording is crystal clear.",
    "Formal News Male": "Rohit speaks in a formal, clear male voice with measured pace and authoritative tone for news delivery. The recording is of very high quality."
}

def split_text_into_chunks(text: str, max_chars_per_chunk: int = 150) -> List[str]:
    sentences = re.split(r'(?<=।|\?|\!|\.)', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence: continue
        if len(current_chunk) + len(sentence) <= max_chars_per_chunk:
            current_chunk += sentence + " "
        else:
            if current_chunk.strip(): chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk.strip(): chunks.append(current_chunk.strip())
    return [c for c in chunks if len(c.strip()) > 20]

def generate_chunk_audio(chunk_text: str, voice_description: str):
    model = ml_models['model']
    tokenizer = ml_models['tokenizer']
    description_tokenizer = ml_models['description_tokenizer']
    device = ml_models['device']

    description_input_ids = description_tokenizer(voice_description, return_tensors="pt").to(device)
    prompt_input_ids = tokenizer(chunk_text, return_tensors="pt").to(device)

    with torch.no_grad():
        generation = model.generate(
            input_ids=description_input_ids.input_ids,
            attention_mask=description_input_ids.attention_mask,
            prompt_input_ids=prompt_input_ids.input_ids,
            prompt_attention_mask=prompt_input_ids.attention_mask,
            do_sample=True,
            temperature=1.0
        )
    return generation.cpu().numpy().squeeze()

def generate_podcast_audio(request: PodcastRequest):
    sampling_rate = ml_models['model'].config.sampling_rate
    all_audio_chunks = []
    silence_duration = 0.5
    
    podcast_script = request.script
    mode = request.mode
    single_speaker = request.single_speaker

    if mode == "Podcast Mode":
        segments = re.split(r'\[([^\]]+)\]', podcast_script)
        segments = [s.strip() for s in segments if s.strip()]
        for i in range(0, len(segments), 2):
            if i + 1 >= len(segments): break
            speaker, text = segments[i], segments[i + 1]
            if speaker not in SPEAKERS: raise ValueError(f"Invalid speaker: {speaker}")
            
            voice_description = SPEAKERS[speaker]
            chunks = split_text_into_chunks(text)
            for j, chunk in enumerate(chunks):
                audio_chunk = generate_chunk_audio(chunk, voice_description)
                all_audio_chunks.append(audio_chunk)
                if j < len(chunks) - 1 or i + 2 < len(segments):
                    silence = np.zeros(int(silence_duration * sampling_rate))
                    all_audio_chunks.append(silence)
    else: # Single Speaker mode
        voice_description = SPEAKERS.get(single_speaker, SPEAKERS["Female Expressive"])
        chunks = split_text_into_chunks(podcast_script)
        for i, chunk in enumerate(chunks):
            audio_chunk = generate_chunk_audio(chunk, voice_description)
            all_audio_chunks.append(audio_chunk)
            if i < len(chunks) - 1:
                silence = np.zeros(int(silence_duration * sampling_rate))
                all_audio_chunks.append(silence)

    if not all_audio_chunks:
        return None
        
    combined_audio = np.concatenate(all_audio_chunks)
    sf.write(request.output_filename, combined_audio, sampling_rate)
    return request.output_filename


# --- API ENDPOINT DEFINITION ---

@app.post("/generate-podcast/")
async def create_podcast_endpoint(request: PodcastRequest):
    """
    Receives a script and returns a generated audio file.
    """
    print(f"Received request for mode: {request.mode}")
    try:
        output_filename = generate_podcast_audio(request)
        if output_filename and os.path.exists(output_filename):
            return FileResponse(
                path=output_filename,
                media_type='audio/wav',
                filename=output_filename
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio file.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))