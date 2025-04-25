# Whisper-SpeechToText

## Overview
This project focuses on Urdu speech transcription using **OpenAI Whisper Model**. It aims to evaluate the transcription performance on publicly available Urdu speech datasets and real-time audio inputs. The evaluation includes **Word Error Rate (WER) and Character Error Rate (CER)** comparisons with established benchmarks.

## Abstract
Low-resource languages like Urdu lack robust speech-to-text solutions, impacting accessibility in education, media, and public services. This project evaluates OpenAI’s Whisper for real-time Urdu transcription, focusing on accuracy, latency, and resource eﬃciency. By testing Whisper on clean and noisy audio samples, we aim to benchmark its performance using Word Error Rate (WER) and Character Error Rate (CER). The outcomes will include a validated Urdu transcription pipeline, performance benchmarks, and an annotated dataset, contributing to improved accessibility for Urdu speakers.

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

## Techniques and Tools Used

- Whisper by OpenAI for high-quality transcription.
- Google Cloud Speech-to-Text API for baseline comparison.
- [RNNoise](https://github.com/dbklim/RNNoise_Wrapper) Wrapper for real-time noise reduction, ensuring cleaner inputs to the transcription models.
- Custom content filtering to ensure output aligns with safe language guidelines, embedding basic guardrails for ethical AI usage.

## Evaluations
The system is evaluated using:

- **Word Error Rate (WER)**: Measures transcription accuracy by comparing word-level differences.
- **Character Error Rate (CER)**: Assesses fine-grained errors at the character level.
- **Comparison with Google Cloud STT Baseline**:
  - Both **batch processing** and **real-time transcription**.
  - Constraint: Real-time transcription is limited to **1-minute audio clips**.

## Transcription Evaluation Results - not real time

| Dataset       | Method           | WER     | CER     | Latency (s) |
|---------------|------------------|---------|---------|-------------|
| **Kaggle**    | Whisper Medium   | 0.3679  | 0.1320  | 1.06        |
|               | Whisper Large    | 0.2763  | 0.0894  | 1.29        |
|               | GCP              | 0.2894  | 0.1283  | 1.02        |
| **Hugging Face** | Whisper Medium | 0.2963  | 0.0978  | 1.18        |
|               | Whisper Large    | 0.1955  | 0.0626  | 1.46        |
|               | GCP              | 0.1743  | 0.0692  | 0.89        |

## Transcription Evaluation Results - Performance of WHISPER - Urdu vs english

| Language | CER         | WER     |
|----------|---------------|---------|
| Urdu     | Whisper Large | 0.2666  |
| English  | Whisper Large | 0.0608  |

## Transcription Evaluation Results - Clean vs Noisy Audio Performance (Whisper Large) - HuggingFace Dataset

| Type  | Model  | WER   |
|-------|--------|--------|
| Clean | 0.0978 | 0.315  |
| Noisy | 0.0999 | 0.324  |

 
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
