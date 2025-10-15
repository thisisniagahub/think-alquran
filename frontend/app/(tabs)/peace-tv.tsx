import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Image,
  TextInput,
  ActivityIndicator,
  Alert,
  FlatList,
  Modal,
  Linking
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface PeaceTVVideo {
  id: string;
  title: string;
  description: string;
  scholar: string;
  language: string;
  content_type: string;
  duration_minutes: number;
  thumbnail_url: string;
  video_url: string;
  view_count: number;
  upload_date: string;
  tags: string[];
}

interface PeaceTVRecommendation {
  video: PeaceTVVideo;
  relevance_score: number;
  reason: string;
  learning_context: string;
  estimated_benefit: string;
}

interface Scholar {
  scholar: string;
  display_name: string;
  expertise: string[];
}

interface ContentType {
  type: string;
  display_name: string;
  description: string;
}

interface WatchHistory {
  video: PeaceTVVideo;
  watch_duration: number;
  completion_percentage: number;
  watched_at: string;
  learning_value: string;
}

const API_BASE = 'http://localhost:8000/api';

export default function PeaceTVScreen() {
  // State management
  const [activeTab, setActiveTab] = useState<'recommendations' | 'search' | 'scholars' | 'live' | 'history'>('recommendations');
  const [recommendations, setRecommendations] = useState<PeaceTVRecommendation[]>([]);
  const [searchResults, setSearchResults] = useState<PeaceTVVideo[]>([]);
  const [scholars, setScholars] = useState<Scholar[]>([]);
  const [contentTypes, setContentTypes] = useState<ContentType[]>([]);
  const [watchHistory, setWatchHistory] = useState<WatchHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScholar, setSelectedScholar] = useState<string>('');
  const [selectedContentType, setSelectedContentType] = useState<string>('');
  const [selectedVideo, setSelectedVideo] = useState<PeaceTVVideo | null>(null);
  const [videoModalVisible, setVideoModalVisible] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadRecommendations(),
        loadContentTypes(),
        loadWatchHistory()
      ]);
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAuthHeaders = async () => {
    const token = await AsyncStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  const loadRecommendations = async () => {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_BASE}/peace-tv/recommendations?limit=10`, {
        headers
      });
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    }
  };

  const loadContentTypes = async () => {
    try {
      const response = await fetch(`${API_BASE}/peace-tv/content-types`);
      const data = await response.json();
      setScholars(data.scholars || []);
      setContentTypes(data.content_types || []);
    } catch (error) {
      console.error('Error loading content types:', error);
    }
  };

  const loadWatchHistory = async () => {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_BASE}/peace-tv/watch-history?limit=20`, {
        headers
      });
      const data = await response.json();
      setWatchHistory(data.watch_history || []);
    } catch (error) {
      console.error('Error loading watch history:', error);
    }
  };

  const searchContent = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const params = new URLSearchParams({
        q: searchQuery,
        limit: '10'
      });
      
      if (selectedScholar) params.append('scholar', selectedScholar);
      if (selectedContentType) params.append('content_type', selectedContentType);
      
      const response = await fetch(`${API_BASE}/peace-tv/search?${params}`, {
        headers
      });
      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Error searching content:', error);
      Alert.alert('Error', 'Failed to search Peace TV content');
    } finally {
      setLoading(false);
    }
  };

  const loadScholarContent = async (scholarName: string) => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_BASE}/peace-tv/scholars/${scholarName}?limit=10`, {
        headers
      });
      const data = await response.json();
      setSearchResults(data.videos || []);
      setActiveTab('search');
    } catch (error) {
      console.error('Error loading scholar content:', error);
      Alert.alert('Error', 'Failed to load scholar content');
    } finally {
      setLoading(false);
    }
  };

  const openVideo = (video: PeaceTVVideo) => {
    setSelectedVideo(video);
    setVideoModalVisible(true);
  };

  const watchVideo = async (video: PeaceTVVideo) => {
    try {
      // Simulate watching the video (in real app, this would be actual video playback)
      const watchDuration = Math.floor(Math.random() * video.duration_minutes * 60); // Random watch time
      const completionPercentage = Math.min((watchDuration / (video.duration_minutes * 60)) * 100, 100);
      
      // Track engagement
      const headers = await getAuthHeaders();
      await fetch(`${API_BASE}/peace-tv/track-engagement`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          video_id: video.id,
          watch_duration: watchDuration,
          completion_percentage: completionPercentage
        })
      });
      
      // Open the video URL
      await Linking.openURL(video.video_url);
      
      setVideoModalVisible(false);
      Alert.alert('Success', 'Video engagement tracked! XP earned for learning.');
      
      // Refresh watch history
      loadWatchHistory();
    } catch (error) {
      console.error('Error watching video:', error);
      Alert.alert('Error', 'Failed to track video engagement');
    }
  };

  const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatScholarName = (scholar: string): string => {
    return scholar.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderVideoCard = (video: PeaceTVVideo, recommendation?: PeaceTVRecommendation) => (
    <TouchableOpacity
      key={video.id}
      style={styles.videoCard}
      onPress={() => openVideo(video)}
    >
      <Image source={{ uri: video.thumbnail_url }} style={styles.thumbnail} />
      <View style={styles.videoInfo}>
        <Text style={styles.videoTitle} numberOfLines={2}>{video.title}</Text>
        <Text style={styles.scholarName}>{formatScholarName(video.scholar)}</Text>
        <Text style={styles.videoDescription} numberOfLines={2}>{video.description}</Text>
        
        <View style={styles.videoMeta}>
          <Text style={styles.duration}>{formatDuration(video.duration_minutes)}</Text>
          <Text style={styles.viewCount}>{video.view_count.toLocaleString()} views</Text>
          <Text style={styles.language}>{video.language}</Text>
        </View>
        
        {recommendation && (
          <View style={styles.recommendationReason}>
            <Ionicons name=\"lightbulb\" size={14} color=\"#4CAF50\" />
            <Text style={styles.reasonText}>{recommendation.reason}</Text>
          </View>
        )}
        
        <View style={styles.tags}>
          {video.tags.slice(0, 3).map((tag, index) => (
            <Text key={index} style={styles.tag}>#{tag}</Text>
          ))}
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderRecommendationsTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.sectionHeader}>
        <Ionicons name=\"star\" size={24} color=\"#4CAF50\" />
        <Text style={styles.sectionTitle}>Personalized for You</Text>
      </View>
      
      {recommendations.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name=\"tv\" size={48} color=\"#ddd\" />
          <Text style={styles.emptyText}>No recommendations yet</Text>
          <Text style={styles.emptySubtext}>Complete some lessons to get personalized video recommendations</Text>
        </View>
      ) : (
        <FlatList
          data={recommendations}
          keyExtractor={(item) => item.video.id}
          renderItem={({ item }) => renderVideoCard(item.video, item)}
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );

  const renderSearchTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name=\"search\" size={20} color=\"#666\" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder=\"Search Peace TV content...\"
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={searchContent}
          />
        </View>
        
        <View style={styles.filtersContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <TouchableOpacity
              style={[styles.filterChip, !selectedScholar && styles.filterChipActive]}
              onPress={() => setSelectedScholar('')}
            >
              <Text style={[styles.filterText, !selectedScholar && styles.filterTextActive]}>All Scholars</Text>
            </TouchableOpacity>
            
            {scholars.map((scholar) => (
              <TouchableOpacity
                key={scholar.scholar}
                style={[styles.filterChip, selectedScholar === scholar.scholar && styles.filterChipActive]}
                onPress={() => setSelectedScholar(scholar.scholar)}
              >
                <Text style={[styles.filterText, selectedScholar === scholar.scholar && styles.filterTextActive]}>
                  {scholar.display_name}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
        
        <TouchableOpacity style={styles.searchButton} onPress={searchContent}>
          <Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>
      
      {searchResults.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name=\"search\" size={48} color=\"#ddd\" />
          <Text style={styles.emptyText}>No search results</Text>
          <Text style={styles.emptySubtext}>Try searching for Islamic topics, scholars, or Quranic content</Text>
        </View>
      ) : (
        <FlatList
          data={searchResults}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => renderVideoCard(item)}
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );

  const renderScholarsTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.sectionHeader}>
        <Ionicons name=\"school\" size={24} color=\"#4CAF50\" />
        <Text style={styles.sectionTitle}>Featured Scholars</Text>
      </View>
      
      <FlatList
        data={scholars}
        keyExtractor={(item) => item.scholar}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.scholarCard}
            onPress={() => loadScholarContent(item.scholar)}
          >
            <View style={styles.scholarInfo}>
              <Text style={styles.scholarName}>{item.display_name}</Text>
              <Text style={styles.scholarExpertise}>
                Expertise: {item.expertise.join(', ')}
              </Text>
            </View>
            <Ionicons name=\"chevron-forward\" size={20} color=\"#666\" />
          </TouchableOpacity>
        )}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );

  const renderWatchHistoryTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.sectionHeader}>
        <Ionicons name=\"time\" size={24} color=\"#4CAF50\" />
        <Text style={styles.sectionTitle}>Watch History</Text>
      </View>
      
      {watchHistory.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name=\"tv\" size={48} color=\"#ddd\" />
          <Text style={styles.emptyText}>No watch history</Text>
          <Text style={styles.emptySubtext}>Start watching Peace TV content to see your history here</Text>
        </View>
      ) : (
        <FlatList
          data={watchHistory}
          keyExtractor={(item, index) => `${item.video.id}-${index}`}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.historyCard}
              onPress={() => openVideo(item.video)}
            >
              <Image source={{ uri: item.video.thumbnail_url }} style={styles.historyThumbnail} />
              <View style={styles.historyInfo}>
                <Text style={styles.historyTitle} numberOfLines={2}>{item.video.title}</Text>
                <Text style={styles.historyScholar}>{formatScholarName(item.video.scholar)}</Text>
                <Text style={styles.historyDate}>Watched on {formatDate(item.watched_at)}</Text>
                
                <View style={styles.progressContainer}>
                  <View style={styles.progressBar}>
                    <View 
                      style={[styles.progressFill, { width: `${item.completion_percentage}%` }]} 
                    />
                  </View>
                  <Text style={styles.progressText}>{Math.round(item.completion_percentage)}%</Text>
                </View>
              </View>
            </TouchableOpacity>
          )}
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );

  const renderVideoModal = () => (
    <Modal
      visible={videoModalVisible}
      animationType=\"slide\"
      presentationStyle=\"pageSheet\"
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => setVideoModalVisible(false)}
          >
            <Ionicons name=\"close\" size={24} color=\"#333\" />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Video Details</Text>
        </View>
        
        {selectedVideo && (
          <ScrollView style={styles.modalContent}>
            <Image source={{ uri: selectedVideo.thumbnail_url }} style={styles.modalThumbnail} />
            
            <View style={styles.modalVideoInfo}>
              <Text style={styles.modalVideoTitle}>{selectedVideo.title}</Text>
              <Text style={styles.modalScholar}>{formatScholarName(selectedVideo.scholar)}</Text>
              <Text style={styles.modalDescription}>{selectedVideo.description}</Text>
              
              <View style={styles.modalMeta}>
                <View style={styles.metaItem}>
                  <Ionicons name=\"time\" size={16} color=\"#666\" />
                  <Text style={styles.metaText}>{formatDuration(selectedVideo.duration_minutes)}</Text>
                </View>
                <View style={styles.metaItem}>
                  <Ionicons name=\"eye\" size={16} color=\"#666\" />
                  <Text style={styles.metaText}>{selectedVideo.view_count.toLocaleString()} views</Text>
                </View>
                <View style={styles.metaItem}>
                  <Ionicons name=\"language\" size={16} color=\"#666\" />
                  <Text style={styles.metaText}>{selectedVideo.language}</Text>
                </View>
              </View>
              
              <View style={styles.modalTags}>
                {selectedVideo.tags.map((tag, index) => (
                  <Text key={index} style={styles.modalTag}>#{tag}</Text>
                ))}
              </View>
              
              <TouchableOpacity
                style={styles.watchButton}
                onPress={() => watchVideo(selectedVideo)}
              >
                <Ionicons name=\"play\" size={20} color=\"white\" />
                <Text style={styles.watchButtonText}>Watch Video</Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        )}
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Image 
            source={{ uri: 'https://www.peacetv.tv/images/logo.png' }} 
            style={styles.logo}
          />
          <View>
            <Text style={styles.headerTitle}>Peace TV</Text>
            <Text style={styles.headerSubtitle}>Islamic Education Channel</Text>
          </View>
        </View>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {[
            { key: 'recommendations', icon: 'star', label: 'For You' },
            { key: 'search', icon: 'search', label: 'Search' },
            { key: 'scholars', icon: 'school', label: 'Scholars' },
            { key: 'history', icon: 'time', label: 'History' }
          ].map((tab) => (
            <TouchableOpacity
              key={tab.key}
              style={[styles.tab, activeTab === tab.key && styles.activeTab]}
              onPress={() => setActiveTab(tab.key as any)}
            >
              <Ionicons 
                name={tab.icon as any} 
                size={18} 
                color={activeTab === tab.key ? '#4CAF50' : '#666'} 
              />
              <Text style={[styles.tabText, activeTab === tab.key && styles.activeTabText]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Content */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size=\"large\" color=\"#4CAF50\" />
          <Text style={styles.loadingText}>Loading Peace TV content...</Text>
        </View>
      ) : (
        <>
          {activeTab === 'recommendations' && renderRecommendationsTab()}
          {activeTab === 'search' && renderSearchTab()}
          {activeTab === 'scholars' && renderScholarsTab()}
          {activeTab === 'history' && renderWatchHistoryTab()}
        </>
      )}

      {/* Video Modal */}
      {renderVideoModal()}
      
      {/* Islamic Compliance Note */}
      <View style={styles.complianceNote}>
        <Ionicons name=\"shield-checkmark\" size={16} color=\"#4CAF50\" />
        <Text style={styles.complianceText}>
          All content is authentic and scholar-verified ✓
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    paddingTop: 50,
    paddingBottom: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logo: {
    width: 40,
    height: 40,
    marginRight: 12,
    borderRadius: 8,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  tabContainer: {
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 4,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#4CAF50',
  },
  tabText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#666',
  },
  activeTabText: {
    color: '#4CAF50',
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
    padding: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 8,
  },
  videoCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  thumbnail: {
    width: '100%',
    height: 200,
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
  },
  videoInfo: {
    padding: 16,
  },
  videoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  scholarName: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
    marginBottom: 6,
  },
  videoDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  videoMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  duration: {
    fontSize: 12,
    color: '#666',
  },
  viewCount: {
    fontSize: 12,
    color: '#666',
  },
  language: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
  },
  recommendationReason: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f8f0',
    padding: 8,
    borderRadius: 6,
    marginBottom: 8,
  },
  reasonText: {
    fontSize: 12,
    color: '#4CAF50',
    marginLeft: 4,
    flex: 1,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    fontSize: 12,
    color: '#4CAF50',
    marginRight: 8,
    marginBottom: 4,
  },
  searchContainer: {
    marginBottom: 20,
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 10,
    paddingHorizontal: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 44,
    fontSize: 16,
  },
  filtersContainer: {
    marginBottom: 12,
  },
  filterChip: {
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  filterChipActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  filterText: {
    fontSize: 14,
    color: '#666',
  },
  filterTextActive: {
    color: 'white',
  },
  searchButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  searchButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  scholarCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  scholarInfo: {
    flex: 1,
  },
  scholarExpertise: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  historyCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: 'row',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  historyThumbnail: {
    width: 120,
    height: 90,
    borderTopLeftRadius: 12,
    borderBottomLeftRadius: 12,
  },
  historyInfo: {
    flex: 1,
    padding: 12,
  },
  historyTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  historyScholar: {
    fontSize: 12,
    color: '#4CAF50',
    marginBottom: 4,
  },
  historyDate: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressBar: {
    flex: 1,
    height: 4,
    backgroundColor: '#eee',
    borderRadius: 2,
    marginRight: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 12,
    color: '#666',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#bbb',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  closeButton: {
    marginRight: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  modalContent: {
    flex: 1,
  },
  modalThumbnail: {
    width: '100%',
    height: 250,
  },
  modalVideoInfo: {
    padding: 20,
  },
  modalVideoTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  modalScholar: {
    fontSize: 16,
    color: '#4CAF50',
    fontWeight: '600',
    marginBottom: 12,
  },
  modalDescription: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
    marginBottom: 20,
  },
  modalMeta: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
    paddingVertical: 16,
    backgroundColor: '#f9f9f9',
    borderRadius: 12,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#666',
  },
  modalTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 24,
  },
  modalTag: {
    fontSize: 14,
    color: '#4CAF50',
    marginRight: 12,
    marginBottom: 8,
  },
  watchButton: {
    backgroundColor: '#4CAF50',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
  },
  watchButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  complianceNote: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f8f0',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#e8f5e8',
  },
  complianceText: {
    marginLeft: 6,
    fontSize: 12,
    color: '#4CAF50',
  },
});
