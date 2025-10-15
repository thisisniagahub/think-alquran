import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const { width } = Dimensions.get('window');

interface LeaderboardEntry {
  username: string;
  words_learned: number;
  current_streak: number;
  rank: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlocked: boolean;
  progress?: number;
  maxProgress?: number;
}

export default function CommunityScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'leaderboard' | 'achievements'>('leaderboard');
  const [timeframe, setTimeframe] = useState<'weekly' | 'monthly' | 'all_time'>('weekly');
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [userRank, setUserRank] = useState<number | null>(null);
  const [currentUser, setCurrentUser] = useState<string>('');

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedTab === 'leaderboard') {
      loadLeaderboard();
    } else {
      loadAchievements();
    }
  }, [selectedTab, timeframe]);

  const loadInitialData = async () => {
    try {
      const userStr = await AsyncStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        setCurrentUser(user.username);
      }
      
      await loadLeaderboard();
      setLoading(false);
    } catch (error) {
      console.error('Error loading initial data:', error);
      setLoading(false);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(
        `${API_URL}/api/community/leaderboard?timeframe=${timeframe}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setLeaderboard(response.data.leaderboard);
      
      // Find current user's rank
      const userEntry = response.data.leaderboard.find(
        (entry: LeaderboardEntry) => entry.username === currentUser
      );
      setUserRank(userEntry?.rank || null);
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    }
  };

  const loadAchievements = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(
        `${API_URL}/api/achievements`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Transform achievement data for display
      const achievementsList: Achievement[] = [
        {
          id: 'first_word',
          title: 'First Steps',
          description: 'Learn your first Quranic word',
          icon: 'leaf',
          unlocked: response.data.user_achievements.includes('first_word'),
        },
        {
          id: 'fifty_words',
          title: 'Vocabulary Builder',
          description: 'Master 50 Quranic words',
          icon: 'library',
          unlocked: response.data.user_achievements.includes('fifty_words'),
          progress: Math.min(50, response.data.next_milestone?.progress || 0),
          maxProgress: 50,
        },
        {
          id: 'hundred_words',
          title: 'Scholar',
          description: 'Master 100 Quranic words',
          icon: 'school',
          unlocked: response.data.user_achievements.includes('hundred_words'),
          progress: response.data.next_milestone?.progress || 0,
          maxProgress: 100,
        },
        {
          id: 'streak_3',
          title: 'Consistent Learner',
          description: 'Maintain a 3-day learning streak',
          icon: 'flame',
          unlocked: false, // Will be determined by API
        },
        {
          id: 'fatiha_master',
          title: 'Fatiha Master',
          description: 'Master all words from Al-Fatiha',
          icon: 'star',
          unlocked: false,
        },
      ];

      setAchievements(achievementsList);
    } catch (error) {
      console.error('Error loading achievements:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    if (selectedTab === 'leaderboard') {
      await loadLeaderboard();
    } else {
      await loadAchievements();
    }
    setRefreshing(false);
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return { icon: 'trophy', color: '#FFD700' };
      case 2:
        return { icon: 'medal', color: '#C0C0C0' };
      case 3:
        return { icon: 'medal', color: '#CD7F32' };
      default:
        return { icon: 'person', color: '#666' };
    }
  };

  const getTimeframeLabel = (tf: string) => {
    switch (tf) {
      case 'weekly':
        return 'This Week';
      case 'monthly':
        return 'This Month';
      case 'all_time':
        return 'All Time';
      default:
        return 'This Week';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2E7D32" />
        <Text style={styles.loadingText}>Loading community data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Islamic Community</Text>
        <Text style={styles.headerSubtitle}>Learning together in the path of Allah</Text>
      </View>

      {/* Tab Selector */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'leaderboard' && styles.activeTab]}
          onPress={() => setSelectedTab('leaderboard')}
        >
          <Ionicons 
            name="trophy" 
            size={20} 
            color={selectedTab === 'leaderboard' ? '#FFF' : '#666'} 
          />
          <Text style={[
            styles.tabText,
            selectedTab === 'leaderboard' && styles.activeTabText
          ]}>
            Leaderboard
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, selectedTab === 'achievements' && styles.activeTab]}
          onPress={() => setSelectedTab('achievements')}
        >
          <Ionicons 
            name="star" 
            size={20} 
            color={selectedTab === 'achievements' ? '#FFF' : '#666'} 
          />
          <Text style={[
            styles.tabText,
            selectedTab === 'achievements' && styles.activeTabText
          ]}>
            Achievements
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#2E7D32" />
        }
      >
        {selectedTab === 'leaderboard' ? (
          <>
            {/* Timeframe Selector */}
            <View style={styles.timeframeContainer}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {['weekly', 'monthly', 'all_time'].map((tf) => (
                  <TouchableOpacity
                    key={tf}
                    style={[
                      styles.timeframeButton,
                      timeframe === tf && styles.activeTimeframe
                    ]}
                    onPress={() => setTimeframe(tf as any)}
                  >
                    <Text style={[
                      styles.timeframeText,
                      timeframe === tf && styles.activeTimeframeText
                    ]}>
                      {getTimeframeLabel(tf)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>

            {/* User's Rank Card */}
            {userRank && (
              <View style={styles.userRankCard}>
                <LinearGradient
                  colors={['#2E7D32', '#4CAF50']}
                  style={styles.userRankGradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                >
                  <View style={styles.userRankContent}>
                    <Text style={styles.userRankLabel}>Your Rank</Text>
                    <View style={styles.userRankInfo}>
                      <Text style={styles.userRankNumber}>#{userRank}</Text>
                      <Text style={styles.userRankName}>{currentUser}</Text>
                    </View>
                  </View>
                </LinearGradient>
              </View>
            )}

            {/* Leaderboard List */}
            <View style={styles.leaderboardContainer}>
              {leaderboard.map((entry, index) => {
                const rankInfo = getRankIcon(entry.rank);
                const isCurrentUser = entry.username === currentUser;
                
                return (
                  <View
                    key={index}
                    style={[
                      styles.leaderboardEntry,
                      isCurrentUser && styles.currentUserEntry
                    ]}
                  >
                    <View style={styles.rankContainer}>
                      <Ionicons
                        name={rankInfo.icon as any}
                        size={24}
                        color={rankInfo.color}
                      />
                      <Text style={styles.rankNumber}>{entry.rank}</Text>
                    </View>

                    <View style={styles.userInfo}>
                      <Text style={[
                        styles.username,
                        isCurrentUser && styles.currentUsername
                      ]}>
                        {entry.username}
                        {isCurrentUser && ' (You)'}
                      </Text>
                      <View style={styles.statsRow}>
                        <View style={styles.statItem}>
                          <Ionicons name="book" size={14} color="#666" />
                          <Text style={styles.statText}>{entry.words_learned} words</Text>
                        </View>
                        <View style={styles.statItem}>
                          <Ionicons name="flame" size={14} color="#FF6B35" />
                          <Text style={styles.statText}>{entry.current_streak} day streak</Text>
                        </View>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>

            {/* Islamic Note */}
            <View style={styles.islamicNote}>
              <Ionicons name="information-circle" size={20} color="#2E7D32" />
              <Text style={styles.islamicNoteText}>
                This leaderboard promotes healthy competition in Islamic learning, following the principle of 'fastabiq al-khayrat' (race in good deeds).
              </Text>
            </View>
          </>
        ) : (
          <>
            {/* Achievements Grid */}
            <View style={styles.achievementsContainer}>
              {achievements.map((achievement) => (
                <View
                  key={achievement.id}
                  style={[
                    styles.achievementCard,
                    achievement.unlocked && styles.unlockedAchievement
                  ]}
                >
                  <View style={styles.achievementIcon}>
                    <Ionicons
                      name={achievement.icon as any}
                      size={32}
                      color={achievement.unlocked ? '#FFD700' : '#CCC'}
                    />
                  </View>
                  
                  <Text style={[
                    styles.achievementTitle,
                    achievement.unlocked && styles.unlockedTitle
                  ]}>
                    {achievement.title}
                  </Text>
                  
                  <Text style={styles.achievementDescription}>
                    {achievement.description}
                  </Text>

                  {achievement.progress !== undefined && achievement.maxProgress && (
                    <View style={styles.progressContainer}>
                      <View style={styles.progressBar}>
                        <View
                          style={[
                            styles.progressFill,
                            {
                              width: `${(achievement.progress / achievement.maxProgress) * 100}%`
                            }
                          ]}
                        />
                      </View>
                      <Text style={styles.progressText}>
                        {achievement.progress}/{achievement.maxProgress}
                      </Text>
                    </View>
                  )}

                  {achievement.unlocked && (
                    <View style={styles.unlockedBadge}>
                      <Ionicons name="checkmark-circle" size={20} color="#4CAF50" />
                      <Text style={styles.unlockedText}>Unlocked</Text>
                    </View>
                  )}
                </View>
              ))}
            </View>

            {/* Islamic Achievement Note */}
            <View style={styles.islamicNote}>
              <Ionicons name="star" size={20} color="#FFD700" />
              <Text style={styles.islamicNoteText}>
                Our achievements follow Islamic principles - celebrating knowledge, consistency, and spiritual growth without gambling elements.
              </Text>
            </View>
          </>
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
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 12,
  },
  header: {
    backgroundColor: '#6A1B9A',
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
    color: '#E1BEE7',
    marginTop: 4,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    marginTop: -20,
    borderRadius: 12,
    padding: 4,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#6A1B9A',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginLeft: 6,
  },
  activeTabText: {
    color: '#FFF',
  },
  content: {
    flex: 1,
    paddingTop: 20,
  },
  timeframeContainer: {
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  timeframeButton: {
    backgroundColor: '#FFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  activeTimeframe: {
    backgroundColor: '#6A1B9A',
    borderColor: '#6A1B9A',
  },
  timeframeText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
  },
  activeTimeframeText: {
    color: '#FFF',
  },
  userRankCard: {
    marginHorizontal: 20,
    marginBottom: 20,
    borderRadius: 16,
    overflow: 'hidden',
  },
  userRankGradient: {
    padding: 20,
  },
  userRankContent: {
    alignItems: 'center',
  },
  userRankLabel: {
    fontSize: 14,
    color: '#E8F5E9',
    marginBottom: 8,
  },
  userRankInfo: {
    alignItems: 'center',
  },
  userRankNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFF',
  },
  userRankName: {
    fontSize: 16,
    color: '#FFF',
    marginTop: 4,
  },
  leaderboardContainer: {
    paddingHorizontal: 20,
  },
  leaderboardEntry: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  currentUserEntry: {
    borderWidth: 2,
    borderColor: '#6A1B9A',
  },
  rankContainer: {
    alignItems: 'center',
    marginRight: 16,
    minWidth: 50,
  },
  rankNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 4,
  },
  userInfo: {
    flex: 1,
  },
  username: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  currentUsername: {
    color: '#6A1B9A',
  },
  statsRow: {
    flexDirection: 'row',
    marginTop: 6,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  statText: {
    fontSize: 13,
    color: '#666',
    marginLeft: 4,
  },
  achievementsContainer: {
    paddingHorizontal: 20,
  },
  achievementCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    opacity: 0.6,
  },
  unlockedAchievement: {
    opacity: 1,
    borderWidth: 2,
    borderColor: '#FFD700',
  },
  achievementIcon: {
    marginBottom: 12,
  },
  achievementTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#999',
    textAlign: 'center',
    marginBottom: 8,
  },
  unlockedTitle: {
    color: '#333',
  },
  achievementDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
  progressContainer: {
    width: '100%',
    marginTop: 16,
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
    backgroundColor: '#6A1B9A',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  unlockedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    backgroundColor: '#E8F5E9',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  unlockedText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#4CAF50',
    marginLeft: 4,
  },
  islamicNote: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    marginVertical: 20,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  islamicNoteText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 12,
    lineHeight: 20,
    fontStyle: 'italic',
  },
});
