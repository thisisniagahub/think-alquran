import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface DashboardData {
  total_words_learned: number;
  current_streak: number;
  total_lessons_completed: number;
  mastery_percentage: number;
  words_practiced_today: number;
  next_lesson: { lesson_number: number; word_count: number } | null;
}

export default function HomeScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [username, setUsername] = useState('');
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    total_words_learned: 0,
    current_streak: 0,
    total_lessons_completed: 0,
    mastery_percentage: 0,
    words_practiced_today: 0,
    next_lesson: null,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const userStr = await AsyncStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        setUsername(user.username);
      }

      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/api/dashboard`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setDashboardData(response.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#2E7D32" />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>{getGreeting()}</Text>
          <Text style={styles.username}>{username}</Text>
        </View>
        <Ionicons name="book" size={40} color="#2E7D32" />
      </View>

      {/* Islamic Quote */}
      <View style={styles.quoteCard}>
        <Text style={styles.quoteArabic}>إِنَّا أَنزَلْنَاهُ قُرْآنًا عَرَبِيًّا لَعَلَّكُمْ تَعْقِلُونَ</Text>
        <Text style={styles.quoteTranslation}>
          "Indeed, We have sent it down as an Arabic Quran that you might understand."
        </Text>
        <Text style={styles.quoteSurah}>~ Surah Yusuf 12:2</Text>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <View style={[styles.statCard, styles.statCardGreen]}>
          <Ionicons name="flame" size={32} color="#FF6B35" />
          <Text style={styles.statNumber}>{dashboardData.current_streak}</Text>
          <Text style={styles.statLabel}>Day Streak</Text>
        </View>

        <View style={[styles.statCard, styles.statCardBlue]}>
          <Ionicons name="book-outline" size={32} color="#1976D2" />
          <Text style={styles.statNumber}>{dashboardData.total_words_learned}</Text>
          <Text style={styles.statLabel}>Words Learned</Text>
        </View>

        <View style={[styles.statCard, styles.statCardGold]}>
          <Ionicons name="checkmark-circle" size={32} color="#FFD700" />
          <Text style={styles.statNumber}>{dashboardData.total_lessons_completed}</Text>
          <Text style={styles.statLabel}>Lessons Done</Text>
        </View>

        <View style={[styles.statCard, styles.statCardPurple]}>
          <Ionicons name="trending-up" size={32} color="#9C27B0" />
          <Text style={styles.statNumber}>{dashboardData.mastery_percentage}%</Text>
          <Text style={styles.statLabel}>Mastery</Text>
        </View>
      </View>

      {/* Daily Lesson Card */}
      {dashboardData.next_lesson && (
        <View style={styles.lessonCard}>
          <View style={styles.lessonHeader}>
            <Text style={styles.lessonTitle}>Today's Lesson</Text>
            <Ionicons name="arrow-forward" size={24} color="#2E7D32" />
          </View>
          <Text style={styles.lessonDescription}>
            Lesson {dashboardData.next_lesson.lesson_number} • {dashboardData.next_lesson.word_count} words
          </Text>
          <Text style={styles.lessonTime}>~ 15 minutes</Text>
          <TouchableOpacity
            style={styles.startButton}
            onPress={() => router.push('/lessons')}
          >
            <Text style={styles.startButtonText}>Start Learning</Text>
            <Ionicons name="play" size={20} color="#FFF" />
          </TouchableOpacity>
        </View>
      )}

      {/* Motivation Section */}
      <View style={styles.motivationCard}>
        <Ionicons name="bulb" size={24} color="#FFD700" />
        <Text style={styles.motivationText}>
          "The best among you are those who learn the Quran and teach it." - Prophet Muhammad ﷺ
        </Text>
      </View>

      {/* Progress Indicator */}
      <View style={styles.progressSection}>
        <Text style={styles.progressTitle}>Today's Progress</Text>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${Math.min(100, (dashboardData.words_practiced_today / 10) * 100)}%` },
            ]}
          />
        </View>
        <Text style={styles.progressText}>
          {dashboardData.words_practiced_today} / 10 words practiced
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  contentContainer: {
    paddingBottom: 24,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 24,
    backgroundColor: '#FFF',
  },
  greeting: {
    fontSize: 16,
    color: '#666',
  },
  username: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginTop: 4,
  },
  quoteCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 24,
    marginTop: 16,
    padding: 20,
    borderRadius: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#FFD700',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quoteArabic: {
    fontSize: 20,
    color: '#2E7D32',
    textAlign: 'center',
    marginBottom: 12,
    lineHeight: 32,
  },
  quoteTranslation: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  quoteSurah: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    marginTop: 16,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 16,
    marginHorizontal: '1%',
    marginVertical: 8,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statCardGreen: {
    borderTopWidth: 3,
    borderTopColor: '#FF6B35',
  },
  statCardBlue: {
    borderTopWidth: 3,
    borderTopColor: '#1976D2',
  },
  statCardGold: {
    borderTopWidth: 3,
    borderTopColor: '#FFD700',
  },
  statCardPurple: {
    borderTopWidth: 3,
    borderTopColor: '#9C27B0',
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  lessonCard: {
    backgroundColor: '#2E7D32',
    marginHorizontal: 24,
    marginTop: 16,
    padding: 20,
    borderRadius: 16,
    shadowColor: '#2E7D32',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 5,
  },
  lessonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  lessonTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
  },
  lessonDescription: {
    fontSize: 16,
    color: '#E0F2E9',
    marginBottom: 4,
  },
  lessonTime: {
    fontSize: 14,
    color: '#B8E6C9',
    marginBottom: 16,
  },
  startButton: {
    backgroundColor: '#FFD700',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  startButtonText: {
    color: '#2E7D32',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  motivationCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    marginHorizontal: 24,
    marginTop: 16,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  motivationText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 12,
    fontStyle: 'italic',
  },
  progressSection: {
    marginHorizontal: 24,
    marginTop: 16,
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2E7D32',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
});
