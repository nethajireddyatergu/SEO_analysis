from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import nltk
from function import *
nltk.download('punkt')

app = FastAPI()

# Directory to store uploaded videos
UPLOAD_DIRECTORY = "uploaded_videos"

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Configure CORS to allow specific origins or allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins or specify a list like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    # Validate the file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return {"error": "Invalid file type. Only video files are allowed."}

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # Save the uploaded video file
    with open(file_path, "wb") as video_file:
        video_file.write(await file.read())

    return {"filename": file.filename, "message": "Video uploaded successfully."}

@app.post("/keywords-bart/")
async def keywords_bart(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return {"error": "Invalid file type. Only video files are allowed."}

    # Prepare file paths
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    audio_path = os.path.join(UPLOAD_DIRECTORY, file.filename.split(".")[0] + ".wav")

    # Save video file
    with open(file_path, "wb") as video_file:
        video_file.write(await file.read())

    # Convert video to audio and extract text
    video_to_wav(file_path, audio_path)
    text = wav_to_text(audio_path)

    # Generate keywords using BART
    keywords, seo_rank = generate_keywords_with_bart_and_seeds_using_youtube(text, [])

    return {"keywords": keywords, "seo_rank": seo_rank, "message": "Keywords and SEO rank generated successfully."}

@app.post("/keywords-bart-seed/")
async def keywords_bart_with_seed(file: UploadFile = File(...), seed_keywords: str = Form(...)):
    # Validate file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return {"error": "Invalid file type. Only video files are allowed."}

    # Prepare file paths
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    audio_path = os.path.join(UPLOAD_DIRECTORY, file.filename.split(".")[0] + ".wav")

    # Save video file
    with open(file_path, "wb") as video_file:
        video_file.write(await file.read())

    # Convert video to audio and extract text
    video_to_wav(file_path, audio_path)
    text = wav_to_text(audio_path)

    # Process seed keywords
    seed_keywords_list = [keyword.strip() for keyword in seed_keywords.split(',') if keyword.strip()]

    # Generate keywords and SEO ranking
    combined_keywords, seo_rank = generate_keywords_with_bart_and_seeds_using_youtube(text, seed_keywords_list)

    return {
        "keywords": combined_keywords,
        "seo_rank": seo_rank,
        "seed_keywords": seed_keywords_list,
        "message": "Keywords and SEO rank generated successfully."
    }


@app.post("/keywords-bart-seed-seo/")
async def keywords_bart_with_seed_and_seo(file: UploadFile = File(...), seed_keywords: str = Form(...)):
    """
    Endpoint to generate keywords from the uploaded video using BART and include user-provided seed keywords,
    and ranks the keywords based on YouTube SEO.
    """
    # Validate the file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return {"error": "Invalid file type. Only video files are allowed."}

    # Prepare file paths
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    audio_path = os.path.join(UPLOAD_DIRECTORY, file.filename.split(".")[0] + ".wav")

    # Save the uploaded video file
    with open(file_path, "wb") as video_file:
        video_file.write(await file.read())

    # Convert video to audio and extract text
    video_to_wav(file_path, audio_path)
    text = wav_to_text(audio_path)


    # Generate keywords using BART and seed keywords
    #combined_keywords, keyword_ranking = generate_keywords_with_bart_and_seeds_using_youtube(text, seed_keywords_list)
    combined_keywords = generate_keywords_with_bart_and_seeds_using_youtube(text, seed_keywords_list)
    return {
        "keywords": combined_keywords,
        "message": "Keywords generated using BART, seed keywords, and SEO ranking from YouTube."
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
