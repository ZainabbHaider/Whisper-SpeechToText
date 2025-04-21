# Whisper-SpeechToText

## Overview
This project focuses on Urdu speech transcription using **OpenAI Whisper Model**. It aims to evaluate the transcription performance on publicly available Urdu speech datasets and real-time audio inputs. The evaluation includes **Word Error Rate (WER) and Character Error Rate (CER)** comparisons with established benchmarks.

### Objectives
- Extract and preprocess Urdu speech data from various sources.
- Perform transcription using **OpenAI Whisper Model** (both normal and real-time).
- Evaluate performance using **WER and CER**.
- Compare results against **Google Cloud STT baseline**.

## Datasets
We use publicly available Urdu speech datasets for training and evaluation:

1. **[Urdu Common Voice Dataset](https://www.kaggle.com/datasets/muhammadahmedansari/urdu-dataset-20000/data?select=final_main_dataset.tsv)**  
   - 20,000 audio clips with transcriptions.
   - Extracted from Mozilla Common Voice.

2. **[Urdu TTS Dataset](https://huggingface.co/datasets/muhammadsaadgondal/urdu-tts/viewer)**  
   - Contains Urdu speech samples with corresponding text.

3. **[Faith Comes By Hearing](https://www.faithcomesbyhearing.com/audio-bible-resources/recordings-database)**  
   - Used for real-time speech transcription testing.

## Evaluations
The system is evaluated using:

- **Word Error Rate (WER)**: Measures transcription accuracy by comparing word-level differences.
- **Character Error Rate (CER)**: Assesses fine-grained errors at the character level.
- **Comparison with Google Cloud STT Baseline**:
  - Both **batch processing** and **real-time transcription**.
  - Constraint: Real-time transcription is limited to **1-minute audio clips**.

## Weekly Progress

| Week   | Tasks |
|--------|------------------------------------------------------|
| **Week 10** | - Set up Whisper transcription pipeline <br> - Set up Google Cloud STT API <br> - Run initial tests |
| **Week 11** | - Implement evaluation metrics <br> - Evaluate pipeline on data |
| **Week 12** | - Implement real time transciption pipeline for Whisper <br> - Improve Google cloud STT real time pipeline |
| **Week 13** | - Research and Implement Noise removal techniques from audio <br> - Inetgrate into pipeline |
| **Week 14** | - Test pipeline on data <br> -  Work on GUI for displaying transcription |
| **Week 15** | - Compare results of normal and real time tramscription for Whisper and GCP STT <br> -  Compile Results |

## Team Members
- Zainab Haider 
- Hijab Fatima 
- Haya Fatima
