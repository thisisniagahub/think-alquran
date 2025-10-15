import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface WordProgress {
  id: string;
  arabic: string;
  transliteration: string;
  meaning: string;
  mastery_level: number;
  total_attempts: number;
}

export default function ProgressScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [words, setWords] = useState<WordProgress[]>([]);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(`${API_URL}/api/progress/words`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWords(response.data);
    } catch (error) {
      console.error('Error loading progress:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadProgress();
  };

  const getMasteryColor = (level: number) => {
    if (level >= 70) return '#2E7D32';
    if (level >= 40) return '#FFD700';
    if (level > 0) return '#FF6B35';
    return '#E0E0E0';
  };

  const getMasteryLabel = (level: number) => {
    if (level >= 80) return 'Mastered';
    if (level >= 60) return 'Good';
    if (level >= 40) return 'Learning';
    if (level > 0) return 'Beginner';
    return 'Not Started';
  };

  const stats = {
    total: words.length,
    mastered: words.filter(w => w.mastery_level >= 70).length,
    learning: words.filter(w => w.mastery_level > 0 && w.mastery_level < 70).length,
    notStarted: words.filter(w => w.mastery_level === 0).length,
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
        <Text style={styles.headerTitle}>Your Progress</Text>
        <Text style={styles.headerSubtitle}>Track your word mastery</Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.contentContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#2E7D32" />
        }
      >
        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={[styles.statCard, styles.statCardGreen]}>
            <Ionicons name="checkmark-circle" size={32} color="#2E7D32" />
            <Text style={styles.statNumber}>{stats.mastered}</Text>
            <Text style={styles.statLabel}>Mastered</Text>
          </View>

          <View style={[styles.statCard, styles.statCardOrange]}>
            <Ionicons name="trending-up" size={32} color="#FF6B35" />
            <Text style={styles.statNumber}>{stats.learning}</Text>
            <Text style={styles.statLabel}>Learning</Text>
          </View>

          <View style={[styles.statCard, styles.statCardGray]}>
            <Ionicons name="book-outline" size={32} color="#999" />
            <Text style={styles.statNumber}>{stats.notStarted}</Text>
            <Text style={styles.statLabel}>Not Started</Text>
          </View>
        </View>

        {/* Words List */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>All Words ({words.length})</Text>
        </View>

        {words.map((word) => (
          <View key={word.id} style={styles.wordCard}>
            <View style={styles.wordHeader}>
              <View style={styles.wordInfo}>
                <Text style={styles.arabicText}>{word.arabic}</Text>
                <Text style={styles.transliterationText}>{word.transliteration}</Text>
                <Text style={styles.meaningText}>{word.meaning}</Text>
              </View>
              <View
                style={[
                  styles.masteryBadge,
                  { backgroundColor: getMasteryColor(word.mastery_level) },
                ]}
              >
                <Text style={styles.masteryBadgeText}>
                  {word.mastery_level.toFixed(0)}%
                </Text>
              </View>
            </View>

            {/* Progress Bar */}
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  {
                    width: `${word.mastery_level}%`,
                    backgroundColor: getMasteryColor(word.mastery_level),
                  },
                ]}
              />
            </View>

            <View style={styles.wordFooter}>
              <Text style={styles.masteryLabel}>
                {getMasteryLabel(word.mastery_level)}
              </Text>
              {word.total_attempts > 0 && (
                <Text style={styles.attemptsText}>
                  {word.total_attempts} attempt{word.total_attempts !== 1 ? 's' : ''}
                </Text>
              )}
            </View>
          </View>
        ))}

        {/* Empty State */}
        {words.length === 0 && (
          <View style={styles.emptyState}>
            <Ionicons name="book-outline" size={64} color="#CCC" />
            <Text style={styles.emptyText}>No words learned yet</Text>
            <Text style={styles.emptySubtext}>Start your first lesson to begin!</Text>
          </View>
        )}
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
    backgroundColor: '#1976D2',
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
    color: '#E3F2FD',
    marginTop: 4,
  },
  contentContainer: {
    padding: 16,
    paddingBottom: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statCardGreen: {
    borderTopWidth: 3,
    borderTopColor: '#2E7D32',
  },
  statCardOrange: {
    borderTopWidth: 3,
    borderTopColor: '#FF6B35',
  },
  statCardGray: {
    borderTopWidth: 3,
    borderTopColor: '#999',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  sectionHeader: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
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
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  wordInfo: {
    flex: 1,
  },
  arabicText: {
    fontSize: 24,
    color: '#2E7D32',
    marginBottom: 4,
  },
  transliterationText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 2,
  },
  meaningText: {
    fontSize: 14,
    color: '#999',
  },
  masteryBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginLeft: 8,
  },
  masteryBadgeText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFF',
  },
  progressBar: {
    height: 6,
    backgroundColor: '#E0E0E0',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  wordFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  masteryLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  attemptsText: {
    fontSize: 12,
    color: '#999',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#CCC',
    marginTop: 8,
  },
});
