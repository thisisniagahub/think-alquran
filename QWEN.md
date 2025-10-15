# ThinkQuran Mobile App - Project Context

## 📋 Overview

ThinkQuran is a comprehensive Islamic learning mobile application that helps users learn Quranic Arabic vocabulary through interactive lessons, quizzes, and advanced AI-powered features. The app combines traditional Islamic learning with modern technology, featuring JAKIM/JAIS compliance standards and integration with Peace TV educational content.

## 🏗️ Architecture

### Backend (FastAPI + MongoDB)
- **Framework**: FastAPI with Python 3.9+
- **Database**: MongoDB with motor async driver
- **Authentication**: JWT-based with bcrypt password hashing
- **API Version**: RESTful API with comprehensive endpoints
- **Deployment**: Vercel-ready with proper environment configuration

### Frontend (Expo React Native)
- **Framework**: Expo with React Native
- **Navigation**: Expo Router for mobile navigation
- **State Management**: Zustand
- **Storage**: AsyncStorage for local persistence
- **HTTP Client**: Axios for API communication

## 🚀 Key Features

### 📚 Core Learning System
- **30+ Quranic Words**: Carefully curated vocabulary across 5 lessons
- **Multiple Choice Quizzes**: Interactive assessment system
- **Progress Tracking**: Individual word mastery levels (0-100%)
- **Streak Tracking**: Daily practice motivation system

### 🔐 Authentication System
- JWT-based user authentication
- Secure registration and login (password validation)
- Session management (30-day token validity)
- Password hashing with bcrypt

### 🤖 Advanced AI Systems
- **AI Tutoring Engine**: Revolutionary AI tutoring with ChatGPT/Claude integration
- **Adaptive Learning**: Spaced repetition system with memory science
- **AI Ustaz Assistant**: Personalized Islamic guidance system
- **Comprehensive Analytics**: Learning insights and recommendations

### 🎮 Gamification System
- **Revolutionary Gamification**: XP, achievements, leaderboards
- **Halal Achievements**: No gambling elements, Islamic-compliant
- **Daily Quests**: Motivational learning challenges
- **Community Features**: Islamic learning leaderboards

### 📺 Integrated Systems
- **Peace TV Integration**: JAKIM-approved Islamic educational content
- **Prayer Times**: Accurate calculation using JAKIM method
- **Qibla Direction**: Precise compass-based direction
- **Islamic Supplications**: JAKIM-approved duas
- **Voice Recognition**: Arabic pronunciation analysis

### 🌐 Advanced Features
- **Offline Mode**: Complete functionality without internet
- **Multi-Reciter Audio**: JAKIM-compliant Quranic recitation
- **Social Learning**: Community features and leaderboards
- **Subscription System**: Tier-based feature access

## 📁 Directory Structure

```
L:\THINK-QURAN\think-alquran\
├── api/                    # Vercel API endpoints
├── backend/               # FastAPI server and modules
│   ├── server.py          # Main application server
│   ├── islamic_compliance.py # JAKIM/JAIS compliance
│   ├── ai_tutoring_engine.py # Advanced AI tutoring
│   ├── adaptive_learning_engine.py # SRS system
│   └── ...                # Various specialized modules
├── frontend/              # Expo React Native app
│   ├── app/              # Application screens
│   ├── assets/           # Images and resources
│   ├── package.json      # Dependencies
│   └── ...               # Configuration files
├── logs/                 # Application logs
├── tests/                # Test files
└── ...                   # Configuration and documentation
```

## 🛠️ Setup Instructions

### Backend Setup
```bash
cd backend/
pip install -r requirements.txt
```

Create `.env` file with:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=thinkquran_advanced
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### Frontend Setup
```bash
cd frontend/
yarn install
```

Create `.env` file with:
```
EXPO_PUBLIC_BACKEND_URL=http://localhost:8000
EXPO_PUBLIC_API_VERSION=v1
```

### Running the Application
- **Backend**: `python server.py` (starts on http://localhost:8000)
- **Frontend**: `yarn start` (starts Expo development server)
- **API Documentation**: http://localhost:8000/docs

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Core Learning
- `GET /api/dashboard` - Dashboard statistics
- `GET /api/lessons` - List all lessons
- `GET /api/lessons/{lesson_number}` - Get lesson words
- `POST /api/lessons/complete` - Submit quiz results
- `GET /api/progress/words` - Word progress tracking

### Advanced Features
- `GET /api/audio/reciters` - JAKIM-approved reciters
- `GET /api/prayer-times` - Prayer times calculation
- `GET /api/qibla-direction` - Qibla direction
- `POST /api/ai-tutor/ask` - AI tutoring
- `GET /api/duas` - Islamic supplications
- `GET /api/community/leaderboard` - Learning community

### Revolutionary Systems
- `GET /api/ai-tutor/comprehensive` - Advanced AI tutoring
- `GET /api/adaptive-learning/due-reviews` - SRS system
- `GET /api/gamification/profile` - Gamification system
- `GET /api/peace-tv/recommendations` - Peace TV integration
- `GET /api/ai-ustaz/guidance/{context}` - Islamic guidance

## 🧪 Testing

### Backend Tests
- `backend_test.py` - Comprehensive API testing suite
- `test_advanced_features.py` - Advanced feature testing

### Deployment Verification
- `deploy_advanced_app.py` - Automated deployment and verification

## 🌟 JAKIM/JAIS Compliance

The application follows Islamic compliance standards:
- Content verification through JAKIM Malaysia and JAIS standards
- Halal gamification system without gambling elements
- Authentic Islamic content and references
- Proper Islamic learning methodology

## 🚀 Deployment

### Vercel Deployment
The application is configured for Vercel deployment with:
- Environment variables for MongoDB, API keys
- Proper build configuration in `vercel.json`
- Separate builds for API and static content

### Environment Variables Required
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name
- `JWT_SECRET_KEY` - JWT signing key
- `OPENAI_API_KEY` (optional) - For AI features

## 🔧 Development Conventions

- **Backend**: Python with FastAPI framework, async/await patterns
- **Frontend**: TypeScript with React Native, Expo Router for navigation
- **Database**: MongoDB with proper indexing and queries
- **Authentication**: JWT tokens with proper security measures
- **Islamic Compliance**: All content verified against JAKIM/JAIS standards

## 📈 Advanced Systems

The application features revolutionary advanced systems that make it unique:
1. **Adaptive Learning Engine**: Personalized spaced repetition based on memory science
2. **AI Ustaz Assistant**: Contextual Islamic guidance system
3. **Peace TV Integration**: Access to authentic Islamic educational content
4. **Comprehensive Gamification**: Halal achievement system with XP and leaderboards
5. **Integrated Guidance System**: Personalized recommendations based on progress
6. **Advanced Analytics**: Deep learning insights and progress tracking

## 🎓 Learning Methodology

The app follows a progressive learning approach:
1. **Foundation**: Basic Quranic vocabulary in Lesson 1
2. **Expansion**: Common verbs and pronouns in Lessons 2-3
3. **Deepening**: Names of Allah and worship concepts in Lessons 4-5
4. **Integration**: Advanced AI tutoring and community features

This application represents a revolutionary approach to Islamic learning, combining traditional scholarship with modern technology while maintaining strict Islamic compliance standards.