import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Word {
  id: string;
  arabic: string;
  transliteration: string;
  meaning: string;
}

interface QuizQuestion {
  word: Word;
  options: string[];
  correctAnswer: string;
}

export default function LessonScreen() {
  const { id } = useLocalSearchParams();
  const [loading, setLoading] = useState(true);
  const [words, setWords] = useState<Word[]>([]);
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState<{ word_id: string; is_correct: boolean; time_spent: number }[]>([]);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());

  useEffect(() => {
    loadLesson();
  }, [id]);

  const loadLesson = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/api/lessons/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWords(response.data);
    } catch (error) {
      console.error('Error loading lesson:', error);
      Alert.alert('Error', 'Failed to load lesson');
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = () => {
    // Generate quiz questions
    const quizQuestions: QuizQuestion[] = words.map(word => {
      // Get 3 random wrong answers
      const wrongOptions = words
        .filter(w => w.id !== word.id)
        .map(w => w.meaning)
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);
      
      // Combine and shuffle
      const options = [...wrongOptions, word.meaning]
        .sort(() => Math.random() - 0.5);
      
      return {
        word,
        options,
        correctAnswer: word.meaning,
      };
    });

    setQuestions(quizQuestions);
    setQuizMode(true);
    setQuestionStartTime(Date.now());
  };

  const handleAnswerSelect = (answer: string) => {
    if (showResult) return;
    setSelectedAnswer(answer);
  };

  const handleSubmitAnswer = () => {
    if (!selectedAnswer) {
      Alert.alert('Please select an answer');
      return;
    }

    const question = questions[currentQuestion];
    const isCorrect = selectedAnswer === question.correctAnswer;
    const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);

    if (isCorrect) {
      setScore(score + 1);
    }

    // Store answer
    setAnswers([
      ...answers,
      {
        word_id: question.word.id,
        is_correct: isCorrect,
        time_spent: timeSpent,
      },
    ]);

    setShowResult(true);
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowResult(false);
      setQuestionStartTime(Date.now());
    } else {
      completeLesson();
    }
  };

  const completeLesson = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      await axios.post(
        `${API_URL}/api/lessons/complete`,
        {
          lesson_id: `lesson_${id}`,
          answers: [...answers, {
            word_id: questions[currentQuestion].word.id,
            is_correct: selectedAnswer === questions[currentQuestion].correctAnswer,
            time_spent: Math.floor((Date.now() - questionStartTime) / 1000),
          }],
          total_time: 900, // 15 minutes
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      Alert.alert(
        'Lesson Complete!',
        `You scored ${score + (selectedAnswer === questions[currentQuestion].correctAnswer ? 1 : 0)} out of ${questions.length}`,
        [
          {
            text: 'Continue',
            onPress: () => router.back(),
          },
        ]
      );
    } catch (error) {
      console.error('Error completing lesson:', error);
      Alert.alert('Error', 'Failed to save progress');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  if (quizMode) {
    const question = questions[currentQuestion];
    const isCorrect = selectedAnswer === question.correctAnswer;

    return (
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#FFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Lesson {id}</Text>
          <View style={styles.progressIndicator}>
            <Text style={styles.progressText}>
              {currentQuestion + 1}/{questions.length}
            </Text>
          </View>
        </View>

        {/* Progress Bar */}
        <View style={styles.progressBarContainer}>
          <View
            style={[
              styles.progressBar,
              { width: `${((currentQuestion + 1) / questions.length) * 100}%` },
            ]}
          />
        </View>

        <ScrollView contentContainerStyle={styles.quizContainer}>
          {/* Question */}
          <View style={styles.questionCard}>
            <Text style={styles.questionLabel}>What does this word mean?</Text>
            <Text style={styles.arabicWord}>{question.word.arabic}</Text>
            <Text style={styles.transliteration}>{question.word.transliteration}</Text>
          </View>

          {/* Options */}
          <View style={styles.optionsContainer}>
            {question.options.map((option, index) => {
              const isSelected = selectedAnswer === option;
              const isCorrectOption = option === question.correctAnswer;
              
              let optionStyle = styles.option;
              if (showResult) {
                if (isSelected && isCorrect) {
                  optionStyle = [styles.option, styles.optionCorrect];
                } else if (isSelected && !isCorrect) {
                  optionStyle = [styles.option, styles.optionWrong];
                } else if (isCorrectOption) {
                  optionStyle = [styles.option, styles.optionCorrect];
                }
              } else if (isSelected) {
                optionStyle = [styles.option, styles.optionSelected];
              }

              return (
                <TouchableOpacity
                  key={index}
                  style={optionStyle}
                  onPress={() => handleAnswerSelect(option)}
                  disabled={showResult}
                  activeOpacity={0.7}
                >
                  <Text style={[
                    styles.optionText,
                    showResult && isCorrectOption && styles.optionTextCorrect,
                    showResult && isSelected && !isCorrect && styles.optionTextWrong,
                  ]}>
                    {option}
                  </Text>
                  {showResult && isCorrectOption && (
                    <Ionicons name="checkmark-circle" size={24} color="#2E7D32" />
                  )}
                  {showResult && isSelected && !isCorrect && (
                    <Ionicons name="close-circle" size={24} color="#F44336" />
                  )}
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Result Message */}
          {showResult && (
            <View style={[styles.resultCard, isCorrect ? styles.resultCardCorrect : styles.resultCardWrong]}>
              <Ionicons
                name={isCorrect ? 'checkmark-circle' : 'close-circle'}
                size={32}
                color={isCorrect ? '#2E7D32' : '#F44336'}
              />
              <Text style={styles.resultText}>
                {isCorrect ? 'Correct!' : 'Incorrect'}
              </Text>
            </View>
          )}
        </ScrollView>

        {/* Action Button */}
        <View style={styles.footer}>
          {!showResult ? (
            <TouchableOpacity
              style={[styles.submitButton, !selectedAnswer && styles.submitButtonDisabled]}
              onPress={handleSubmitAnswer}
              disabled={!selectedAnswer}
            >
              <Text style={styles.submitButtonText}>Submit Answer</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.nextButton} onPress={handleNextQuestion}>
              <Text style={styles.nextButtonText}>
                {currentQuestion < questions.length - 1 ? 'Next Question' : 'Complete Lesson'}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  }

  // Learning Mode (before quiz)
  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#FFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Lesson {id}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.contentContainer}>
        <View style={styles.introCard}>
          <Ionicons name="book" size={48} color="#2E7D32" />
          <Text style={styles.introTitle}>Learn These Words</Text>
          <Text style={styles.introSubtitle}>
            Study the {words.length} words below, then take the quiz to test your knowledge.
          </Text>
        </View>

        {/* Words List */}
        {words.map((word, index) => (
          <View key={word.id} style={styles.wordCard}>
            <View style={styles.wordNumber}>
              <Text style={styles.wordNumberText}>{index + 1}</Text>
            </View>
            <View style={styles.wordContent}>
              <Text style={styles.wordArabic}>{word.arabic}</Text>
              <Text style={styles.wordTransliteration}>{word.transliteration}</Text>
              <Text style={styles.wordMeaning}>{word.meaning}</Text>
            </View>
          </View>
        ))}

        <TouchableOpacity style={styles.startQuizButton} onPress={startQuiz}>
          <Text style={styles.startQuizButtonText}>Start Quiz</Text>
          <Ionicons name="arrow-forward" size={20} color="#FFF" />
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  header: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 16,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
  },
  progressIndicator: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFF',
  },
  progressBarContainer: {
    height: 4,
    backgroundColor: '#E0E0E0',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#FFD700',
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 32,
  },
  introCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  introTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
  },
  introSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  wordCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  wordNumber: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2E7D32',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  wordNumberText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
  wordContent: {
    flex: 1,
  },
  wordArabic: {
    fontSize: 24,
    color: '#2E7D32',
    marginBottom: 4,
  },
  wordTransliteration: {
    fontSize: 16,
    color: '#666',
    marginBottom: 2,
  },
  wordMeaning: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  startQuizButton: {
    flexDirection: 'row',
    backgroundColor: '#2E7D32',
    borderRadius: 12,
    padding: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
    shadowColor: '#2E7D32',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 5,
  },
  startQuizButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFF',
    marginRight: 8,
  },
  quizContainer: {
    padding: 16,
    paddingBottom: 100,
  },
  questionCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  questionLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 16,
  },
  arabicWord: {
    fontSize: 48,
    color: '#2E7D32',
    marginBottom: 8,
  },
  transliteration: {
    fontSize: 20,
    color: '#999',
  },
  optionsContainer: {
    marginBottom: 24,
  },
  option: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 18,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E0E0E0',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  optionSelected: {
    borderColor: '#2E7D32',
    backgroundColor: '#E8F5E9',
  },
  optionCorrect: {
    borderColor: '#2E7D32',
    backgroundColor: '#E8F5E9',
  },
  optionWrong: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE',
  },
  optionText: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  optionTextCorrect: {
    fontWeight: '600',
    color: '#2E7D32',
  },
  optionTextWrong: {
    color: '#F44336',
  },
  resultCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  resultCardCorrect: {
    backgroundColor: '#E8F5E9',
  },
  resultCardWrong: {
    backgroundColor: '#FFEBEE',
  },
  resultText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 12,
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    backgroundColor: '#FFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  submitButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFF',
  },
  nextButton: {
    backgroundColor: '#FFD700',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
  },
  nextButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
});
