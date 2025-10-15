import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  Modal,
  TextInput,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Word {
  id: string;
  arabic: string;
  transliteration: string;
  meaning: string;
}

interface QuizQuestion {
  word_id: string;
  arabic: string;
  transliteration: string;
  meaning: string;
  options?: string[];
  correct_answer?: string;
  question_text?: string;
  answer?: string;
  instruction?: string;
  target_pronunciation?: string;
}

interface AdvancedQuiz {
  lesson_id: string;
  quiz_type: string;
  total_questions: number;
  questions: QuizQuestion[];
}

export default function AdvancedLessonScreen() {
  const { id } = useLocalSearchParams();
  const [loading, setLoading] = useState(true);
  const [words, setWords] = useState<Word[]>([]);
  const [currentMode, setCurrentMode] = useState<'study' | 'quiz'>('study');
  const [quizType, setQuizType] = useState<'multiple_choice' | 'fill_blank' | 'voice_recognition' | 'writing'>('multiple_choice');
  const [currentQuiz, setCurrentQuiz] = useState<AdvancedQuiz | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioModalVisible, setAudioModalVisible] = useState(false);
  const [selectedReciter, setSelectedReciter] = useState('mishary');

  const reciters = [
    { id: 'mishary', name: 'Mishary Alafasy', country: 'Kuwait' },
    { id: 'husary', name: 'Mahmoud Al-Husary', country: 'Egypt' },
    { id: 'sudais', name: 'Abdul Rahman Al-Sudais', country: 'Saudi Arabia' },
    { id: 'maher', name: 'Maher Al Mueaqly', country: 'Saudi Arabia' }
  ];

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

  const startAdvancedQuiz = async () => {
    try {
      setLoading(true);
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.post(
        `${API_URL}/api/quiz/advanced`,
        {
          lesson_id: `lesson_${id}`,
          quiz_type: quizType
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setCurrentQuiz(response.data);
      setCurrentMode('quiz');
      setCurrentQuestion(0);
      setScore(0);
      setUserAnswer('');
      setShowResult(false);
    } catch (error) {
      console.error('Error creating quiz:', error);
      Alert.alert('Error', 'Failed to create quiz');
    } finally {
      setLoading(false);
    }
  };

  const playAudio = async (word: Word) => {
    try {
      setAudioModalVisible(true);
    } catch (error) {
      console.error('Error playing audio:', error);
      Alert.alert('Error', 'Audio not available');
    }
  };

  const playReciterAudio = async (reciterId: string, word: Word) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(
        `${API_URL}/api/audio/${reciterId}/1/1`, // Using placeholder values
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.audio_url) {
        const { sound } = await Audio.Sound.createAsync(
          { uri: response.data.audio_url },
          { shouldPlay: true }
        );
        await sound.playAsync();
      }
    } catch (error) {
      console.error('Error playing reciter audio:', error);
      Alert.alert('Audio Error', 'Unable to play audio at this time');
    }
  };

  const startRecording = async () => {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert('Permission Required', 'Microphone permission is needed for voice recognition');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      Alert.alert('Error', 'Unable to start recording');
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      setIsRecording(false);
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      
      if (uri) {
        await analyzeVoiceRecording(uri);
      }
      
      setRecording(null);
    } catch (error) {
      console.error('Error stopping recording:', error);
      Alert.alert('Error', 'Unable to process recording');
    }
  };

  const analyzeVoiceRecording = async (audioUri: string) => {
    try {
      if (!currentQuiz) return;
      
      const question = currentQuiz.questions[currentQuestion];
      const token = await AsyncStorage.getItem('auth_token');
      
      const formData = new FormData();
      formData.append('audio_file', {
        uri: audioUri,
        name: 'recording.m4a',
        type: 'audio/m4a',
      } as any);
      formData.append('target_text', question.arabic);

      const response = await axios.post(
        `${API_URL}/api/voice/analyze`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      const analysis = response.data;
      Alert.alert(
        'Pronunciation Analysis',
        `Overall Score: ${analysis.overall_score}/100\n` +
        `Tajweed Score: ${analysis.tajweed_score}/100\n` +
        `Areas for improvement: ${analysis.areas_for_improvement?.map((area: any) => area.area).join(', ') || 'None'}`
      );

      // Consider score above 70 as correct
      const isCorrect = analysis.overall_score >= 70;
      if (isCorrect) {
        setScore(score + 1);
      }
      setShowResult(true);
    } catch (error) {
      console.error('Error analyzing voice:', error);
      Alert.alert('Error', 'Unable to analyze pronunciation');
    }
  };

  const submitAnswer = () => {
    if (!currentQuiz) return;

    const question = currentQuiz.questions[currentQuestion];
    let isCorrect = false;

    switch (quizType) {
      case 'multiple_choice':
        isCorrect = userAnswer === question.correct_answer;
        break;
      case 'fill_blank':
      case 'writing':
        isCorrect = userAnswer.toLowerCase().trim() === question.answer?.toLowerCase().trim();
        break;
      case 'voice_recognition':
        // Voice recognition result is handled in analyzeVoiceRecording
        return;
    }

    if (isCorrect) {
      setScore(score + 1);
    }
    setShowResult(true);
  };

  const nextQuestion = () => {
    if (!currentQuiz) return;

    if (currentQuestion < currentQuiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setUserAnswer('');
      setShowResult(false);
    } else {
      completeQuiz();
    }
  };

  const completeQuiz = () => {
    const finalScore = ((score / (currentQuiz?.questions.length || 1)) * 100).toFixed(0);
    Alert.alert(
      'Quiz Complete!',
      `Your score: ${score}/${currentQuiz?.questions.length} (${finalScore}%)\n\n${getEncouragementMessage(parseInt(finalScore))}`,
      [
        {
          text: 'Review Lesson',
          onPress: () => {
            setCurrentMode('study');
            setCurrentQuiz(null);
          }
        },
        {
          text: 'Continue',
          onPress: () => router.back()
        }
      ]
    );
  };

  const getEncouragementMessage = (score: number) => {
    if (score >= 90) return 'Excellent! ماشاء الله (MashaAllah)';
    if (score >= 80) return 'Very good! Keep up the great work!';
    if (score >= 70) return 'Good job! Practice makes perfect.';
    if (score >= 60) return 'Not bad! Review and try again.';
    return 'Keep practicing! Allah rewards effort.';
  };

  const renderQuizTypeSelector = () => (
    <View style={styles.quizTypeSelector}>
      <Text style={styles.selectorTitle}>Choose Quiz Type:</Text>
      <View style={styles.quizTypeGrid}>
        {[
          { type: 'multiple_choice', label: 'Multiple Choice', icon: 'checkmark-circle' },
          { type: 'fill_blank', label: 'Fill Blanks', icon: 'create' },
          { type: 'voice_recognition', label: 'Voice Recognition', icon: 'mic' },
          { type: 'writing', label: 'Writing Practice', icon: 'pencil' }
        ].map((option) => (
          <TouchableOpacity
            key={option.type}
            style={[
              styles.quizTypeButton,
              quizType === option.type && styles.selectedQuizType
            ]}
            onPress={() => setQuizType(option.type as any)}
          >
            <Ionicons 
              name={option.icon as any} 
              size={24} 
              color={quizType === option.type ? '#FFF' : '#2E7D32'} 
            />
            <Text style={[
              styles.quizTypeLabel,
              quizType === option.type && styles.selectedQuizTypeLabel
            ]}>
              {option.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderQuizQuestion = () => {
    if (!currentQuiz) return null;

    const question = currentQuiz.questions[currentQuestion];
    const isCorrect = showResult && (
      (quizType === 'multiple_choice' && userAnswer === question.correct_answer) ||
      ((quizType === 'fill_blank' || quizType === 'writing') && 
       userAnswer.toLowerCase().trim() === question.answer?.toLowerCase().trim())
    );

    return (
      <View style={styles.quizContainer}>
        {/* Progress */}
        <View style={styles.quizProgress}>
          <Text style={styles.progressText}>
            Question {currentQuestion + 1} of {currentQuiz.questions.length}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${((currentQuestion + 1) / currentQuiz.questions.length) * 100}%` }
              ]}
            />
          </View>
        </View>

        {/* Question */}
        <View style={styles.questionCard}>
          <Text style={styles.arabicWord}>{question.arabic}</Text>
          <Text style={styles.transliteration}>{question.transliteration}</Text>
          
          {quizType === 'voice_recognition' ? (
            <View style={styles.voiceRecognitionContainer}>
              <Text style={styles.instruction}>{question.instruction}</Text>
              <TouchableOpacity
                style={[
                  styles.recordButton,
                  isRecording && styles.recordingButton
                ]}
                onPress={isRecording ? stopRecording : startRecording}
                disabled={showResult}
              >
                <Ionicons 
                  name={isRecording ? 'stop' : 'mic'} 
                  size={32} 
                  color="#FFF" 
                />
                <Text style={styles.recordButtonText}>
                  {isRecording ? 'Stop Recording' : 'Start Recording'}
                </Text>
              </TouchableOpacity>
            </View>
          ) : quizType === 'multiple_choice' ? (
            <View style={styles.optionsContainer}>
              {question.options?.map((option, index) => (
                <TouchableOpacity
                  key={index}
                  style={[
                    styles.option,
                    userAnswer === option && styles.selectedOption,
                    showResult && option === question.correct_answer && styles.correctOption,
                    showResult && userAnswer === option && userAnswer !== question.correct_answer && styles.wrongOption
                  ]}
                  onPress={() => setUserAnswer(option)}
                  disabled={showResult}
                >
                  <Text style={[
                    styles.optionText,
                    showResult && option === question.correct_answer && styles.correctOptionText
                  ]}>
                    {option}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          ) : (
            <View style={styles.inputContainer}>
              <Text style={styles.instruction}>
                {quizType === 'fill_blank' ? question.question_text : question.instruction}
              </Text>
              <TextInput
                style={[
                  styles.textInput,
                  showResult && isCorrect && styles.correctInput,
                  showResult && !isCorrect && styles.wrongInput
                ]}
                value={userAnswer}
                onChangeText={setUserAnswer}
                placeholder="Type your answer..."
                multiline={quizType === 'writing'}
                editable={!showResult}
              />
              {showResult && !isCorrect && (
                <Text style={styles.correctAnswerText}>
                  Correct answer: {question.answer}
                </Text>
              )}
            </View>
          )}
        </View>

        {/* Result */}
        {showResult && quizType !== 'voice_recognition' && (
          <View style={[
            styles.resultCard,
            isCorrect ? styles.correctResult : styles.wrongResult
          ]}>
            <Ionicons
              name={isCorrect ? 'checkmark-circle' : 'close-circle'}
              size={32}
              color={isCorrect ? '#4CAF50' : '#F44336'}
            />
            <Text style={styles.resultText}>
              {isCorrect ? 'Correct! ماشاء الله' : 'Incorrect. Keep practicing!'}
            </Text>
          </View>
        )}

        {/* Action Button */}
        <View style={styles.actionContainer}>
          {!showResult && quizType !== 'voice_recognition' ? (
            <TouchableOpacity
              style={[
                styles.submitButton,
                !userAnswer && styles.disabledButton
              ]}
              onPress={submitAnswer}
              disabled={!userAnswer}
            >
              <Text style={styles.submitButtonText}>Submit Answer</Text>
            </TouchableOpacity>
          ) : showResult ? (
            <TouchableOpacity
              style={styles.nextButton}
              onPress={nextQuestion}
            >
              <Text style={styles.nextButtonText}>
                {currentQuestion < currentQuiz.questions.length - 1 ? 'Next Question' : 'Complete Quiz'}
              </Text>
            </TouchableOpacity>
          ) : null}
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2E7D32" />
        <Text style={styles.loadingText}>Loading lesson...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#FFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Advanced Lesson {id}</Text>
        <TouchableOpacity onPress={() => setCurrentMode(currentMode === 'study' ? 'quiz' : 'study')}>
          <Ionicons 
            name={currentMode === 'study' ? 'play' : 'book'} 
            size={24} 
            color="#FFF" 
          />
        </TouchableOpacity>
      </View>

      {currentMode === 'study' ? (
        <ScrollView style={styles.content}>
          {/* Study Mode */}
          <View style={styles.studyHeader}>
            <Text style={styles.studyTitle}>Study Mode</Text>
            <Text style={styles.studySubtitle}>Learn {words.length} words with audio</Text>
          </View>

          {words.map((word, index) => (
            <View key={word.id} style={styles.wordCard}>
              <View style={styles.wordHeader}>
                <View style={styles.wordNumber}>
                  <Text style={styles.wordNumberText}>{index + 1}</Text>
                </View>
                <TouchableOpacity
                  style={styles.audioButton}
                  onPress={() => playAudio(word)}
                >
                  <Ionicons name="volume-high" size={24} color="#2E7D32" />
                </TouchableOpacity>
              </View>
              
              <Text style={styles.wordArabic}>{word.arabic}</Text>
              <Text style={styles.wordTransliteration}>{word.transliteration}</Text>
              <Text style={styles.wordMeaning}>{word.meaning}</Text>
            </View>
          ))}

          {renderQuizTypeSelector()}

          <TouchableOpacity
            style={styles.startQuizButton}
            onPress={startAdvancedQuiz}
          >
            <Text style={styles.startQuizButtonText}>Start {quizType.replace('_', ' ')} Quiz</Text>
            <Ionicons name="arrow-forward" size={20} color="#FFF" />
          </TouchableOpacity>
        </ScrollView>
      ) : (
        renderQuizQuestion()
      )}

      {/* Audio Modal */}
      <Modal
        visible={audioModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setAudioModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.audioModal}>
            <Text style={styles.modalTitle}>Choose Reciter</Text>
            {reciters.map((reciter) => (
              <TouchableOpacity
                key={reciter.id}
                style={styles.reciterOption}
                onPress={() => {
                  setSelectedReciter(reciter.id);
                  playReciterAudio(reciter.id, words[0]);
                  setAudioModalVisible(false);
                }}
              >
                <Text style={styles.reciterName}>{reciter.name}</Text>
                <Text style={styles.reciterCountry}>{reciter.country}</Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setAudioModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
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
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 12,
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
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  studyHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  studyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  studySubtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  wordCard: {
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
  wordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  wordNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#2E7D32',
    justifyContent: 'center',
    alignItems: 'center',
  },
  wordNumberText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFF',
  },
  audioButton: {
    padding: 8,
  },
  wordArabic: {
    fontSize: 28,
    color: '#2E7D32',
    textAlign: 'center',
    marginBottom: 8,
  },
  wordTransliteration: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 4,
  },
  wordMeaning: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  quizTypeSelector: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    marginVertical: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  selectorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
    textAlign: 'center',
  },
  quizTypeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quizTypeButton: {
    width: '48%',
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E0E0E0',
  },
  selectedQuizType: {
    backgroundColor: '#2E7D32',
    borderColor: '#2E7D32',
  },
  quizTypeLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginTop: 8,
    textAlign: 'center',
  },
  selectedQuizTypeLabel: {
    color: '#FFF',
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
    textTransform: 'capitalize',
  },
  quizContainer: {
    flex: 1,
    padding: 16,
  },
  quizProgress: {
    marginBottom: 24,
  },
  progressText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    textAlign: 'center',
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E0E0E0',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2E7D32',
    borderRadius: 3,
  },
  questionCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  arabicWord: {
    fontSize: 48,
    color: '#2E7D32',
    textAlign: 'center',
    marginBottom: 8,
  },
  transliteration: {
    fontSize: 20,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  optionsContainer: {
    marginBottom: 16,
  },
  option: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E0E0E0',
  },
  selectedOption: {
    borderColor: '#2E7D32',
    backgroundColor: '#E8F5E9',
  },
  correctOption: {
    borderColor: '#4CAF50',
    backgroundColor: '#E8F5E9',
  },
  wrongOption: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE',
  },
  optionText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
  },
  correctOptionText: {
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  inputContainer: {
    marginBottom: 16,
  },
  instruction: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 16,
  },
  textInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 2,
    borderColor: '#E0E0E0',
    textAlign: 'center',
  },
  correctInput: {
    borderColor: '#4CAF50',
    backgroundColor: '#E8F5E9',
  },
  wrongInput: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE',
  },
  correctAnswerText: {
    fontSize: 14,
    color: '#F44336',
    textAlign: 'center',
    marginTop: 8,
    fontWeight: '600',
  },
  voiceRecognitionContainer: {
    alignItems: 'center',
  },
  recordButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 50,
    width: 120,
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
  },
  recordingButton: {
    backgroundColor: '#F44336',
  },
  recordButtonText: {
    fontSize: 12,
    color: '#FFF',
    fontWeight: 'bold',
    marginTop: 8,
    textAlign: 'center',
  },
  resultCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  correctResult: {
    backgroundColor: '#E8F5E9',
  },
  wrongResult: {
    backgroundColor: '#FFEBEE',
  },
  resultText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 12,
  },
  actionContainer: {
    marginTop: 'auto',
  },
  submitButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
  },
  disabledButton: {
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  audioModal: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    width: '80%',
    maxHeight: '70%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  reciterOption: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  reciterName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  reciterCountry: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  closeButton: {
    backgroundColor: '#2E7D32',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  closeButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
});
