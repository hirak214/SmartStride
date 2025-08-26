# 💻 Software

AI-powered backend and machine learning components for SmartStride.

## 📁 Structure

- **`ai-models/`** - Trained LSTM models for speed and inclination prediction
- **`backend/`** - FastAPI server with database integration
- **`training/`** - Jupyter notebooks and scripts for model training

## 🧠 AI Components

### LSTM Models
- **Speed Prediction**: Predicts optimal running speed based on user profile and historical data
- **Inclination Prediction**: Adapts treadmill incline for personalized workouts

### Features
- User profiling and goal tracking
- Real-time workout adaptation
- Performance analytics and visualization
- Historical data analysis

## 🛠️ Tech Stack

- **Python 3.8+**
- **TensorFlow/Keras** - Deep learning models
- **FastAPI** - REST API backend
- **PostgreSQL** - User data and workout storage
- **Pandas/NumPy** - Data processing
- **Scikit-learn** - ML preprocessing

## 🚀 Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up PostgreSQL database
3. Run the API server: `uvicorn main:app --reload`
4. Access API documentation at `http://localhost:8000/docs`
