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

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Lesson {
  id: string;
  lesson_number: number;
  title: string;
  description: string;
  word_count: number;
  estimated_minutes: number;
  is_completed: boolean;
  mastery_percentage: number;
}

export default function LessonsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lessons, setLessons] = useState<Lesson[]>([]);

  useEffect(() => {
    loadLessons();
  }, []);

  const loadLessons = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/api/lessons`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLessons(response.data);
    } catch (error) {
      console.error('Error loading lessons:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadLessons();
  };

  const getMasteryColor = (percentage: number) => {
    if (percentage >= 70) return '#2E7D32';
    if (percentage >= 40) return '#FFD700';
    return '#FF6B35';
  };

  const startLesson = (lesson: Lesson) => {
    router.push(`/lesson/${lesson.lesson_number}`);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2E7D32" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Word Quest</Text>
        <Text style={styles.headerSubtitle}>Master 1000 Quranic Words</Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.contentContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#2E7D32" />
        }
      >
        {/* Progress Overview */}
        <View style={styles.overviewCard}>
          <View style={styles.overviewHeader}>
            <Ionicons name="trophy" size={32} color="#FFD700" />
            <View style={styles.overviewText}>
              <Text style={styles.overviewTitle}>Your Progress</Text>
              <Text style={styles.overviewSubtitle}>
                {lessons.filter(l => l.is_completed).length} / {lessons.length} lessons completed
              </Text>
            </View>
          </View>
        </View>

        {/* Lessons List */}
        {lessons.map((lesson, index) => (
          <TouchableOpacity
            key={lesson.id}
            style={styles.lessonCard}
            onPress={() => startLesson(lesson)}
            activeOpacity={0.7}
          >
            <View style={styles.lessonHeader}>
              <View style={[
                styles.lessonNumber,
                lesson.is_completed && styles.lessonNumberCompleted
              ]}>
                {lesson.is_completed ? (
                  <Ionicons name="checkmark" size={24} color="#FFF" />
                ) : (
                  <Text style={styles.lessonNumberText}>{lesson.lesson_number}</Text>
                )}
              </View>
              <View style={styles.lessonInfo}>
                <Text style={styles.lessonTitle}>{lesson.title}</Text>
                <Text style={styles.lessonDescription}>{lesson.description}</Text>
                <View style={styles.lessonMeta}>
                  <View style={styles.metaItem}>
                    <Ionicons name="book-outline" size={14} color="#666" />
                    <Text style={styles.metaText}>{lesson.word_count} words</Text>
                  </View>
                  <View style={styles.metaItem}>
                    <Ionicons name="time-outline" size={14} color="#666" />
                    <Text style={styles.metaText}>{lesson.estimated_minutes} min</Text>
                  </View>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#999" />
            </View>

            {/* Mastery Bar */}
            {lesson.mastery_percentage > 0 && (
              <View style={styles.masterySection}>
                <View style={styles.masteryBar}>
                  <View
                    style={[
                      styles.masteryFill,
                      {
                        width: `${lesson.mastery_percentage}%`,
                        backgroundColor: getMasteryColor(lesson.mastery_percentage),
                      },
                    ]}
                  />
                </View>
                <Text style={styles.masteryText}>
                  {lesson.mastery_percentage.toFixed(0)}% mastered
                </Text>
              </View>
            )}
          </TouchableOpacity>
        ))}

        {/* Motivational Footer */}
        <View style={styles.motivationCard}>
          <Ionicons name="star" size={24} color="#FFD700" />
          <Text style={styles.motivationText}>
            Consistency is key! Complete one lesson daily to build your vocabulary.
          </Text>
        </View>
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
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#E0F2E9',
    marginTop: 4,
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 24,
  },
  overviewCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  overviewHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  overviewText: {
    marginLeft: 16,
    flex: 1,
  },
  overviewTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  overviewSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  lessonCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lessonHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  lessonNumber: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#2E7D32',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  lessonNumberCompleted: {
    backgroundColor: '#FFD700',
  },
  lessonNumberText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
  },
  lessonInfo: {
    flex: 1,
  },
  lessonTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  lessonDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  lessonMeta: {
    flexDirection: 'row',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  metaText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  masterySection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  masteryBar: {
    height: 6,
    backgroundColor: '#E0E0E0',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  masteryFill: {
    height: '100%',
    borderRadius: 3,
  },
  masteryText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'right',
  },
  motivationCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 8,
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
});
