import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  Modal,
  FlatList,
  Dimensions
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width } = Dimensions.get('window');

interface QuranicReference {
  surah: {
    number: number;
    name_arabic: string;
    name_english: string;
  };
  ayat: {
    number: number;
    arabic_text: string;
    english_translation: string;
  };
  reference: string;
  context_relevance: string;
  scholarly_note?: string;
}

interface UstazGuidance {
  persona: string;
  main_message: string;
  practical_advice: string;
  encouragement: string;
  next_steps: string[];
  duas_recommendation?: string;
}

interface PeaceTVVideo {
  id: string;
  title: string;
  description: string;
  scholar: string;
  duration_minutes: number;
  thumbnail_url: string;
  video_url: string;
  relevance_reason?: string;
  why_recommended_now?: string;
}

interface IntegratedGuidance {
  ustaz_guidance: UstazGuidance;
  peace_tv_recommendations: PeaceTVVideo[];
  learning_path: string[];
  next_actions: string[];
  duas_for_context: string;
  estimated_study_time_minutes: number;
  islamic_benefits: string[];
}

const API_BASE = 'http://localhost:8000/api';

export default function AIAssistantScreen() {
  // State management
  const [activeTab, setActiveTab] = useState<'guidance' | 'scholar' | 'daily' | 'videos'>('guidance');
  const [integratedGuidance, setIntegratedGuidance] = useState<IntegratedGuidance | null>(null);
  const [quranicReference, setQuranicReference] = useState<QuranicReference | null>(null);
  const [selectedScholar, setSelectedScholar] = useState<string>('');
  const [scholarGuidance, setScholarGuidance] = useState<any>(null);
  const [dailyGuidance, setDailyGuidance] = useState<any>(null);
  const [contextualVideos, setContextualVideos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<PeaceTVVideo | null>(null);
  const [videoModalVisible, setVideoModalVisible] = useState(false);
  const [currentContext, setCurrentContext] = useState<string>('onboarding');
  const [availableTime, setAvailableTime] = useState<number>(30);
  const [timeOfDay, setTimeOfDay] = useState<string>('morning');

  // Available scholars
  const scholars = [
    { id: 'dr_zakir_naik', name: 'Dr. Zakir Naik', expertise: 'Comparative Religion, Medical Miracles' },
    { id: 'dr_israr_ahmad', name: 'Dr. Israr Ahmad', expertise: 'Deep Tafseer, Islamic Philosophy' },
    { id: 'dr_bilal_philips', name: 'Dr. Bilal Philips', expertise: 'Arabic Grammar, Islamic Studies' },
    { id: 'yusuf_estes', name: 'Yusuf Estes', expertise: 'New Muslim Guidance, Practical Islam' },
    { id: 'abdur_raheem_green', name: 'Abdur Raheem Green', expertise: 'Youth Guidance, Modern Issues' },
    { id: 'hussein_yee', name: 'Hussein Yee', expertise: 'Community Building, Practical Living' }
  ];

  // Available contexts
  const contexts = [
    { id: 'onboarding', name: 'Getting Started', icon: 'rocket' },
    { id: 'lesson_start', name: 'Before Learning', icon: 'book' },
    { id: 'lesson_complete', name: 'After Learning', icon: 'checkmark-circle' },
    { id: 'prayer_time', name: 'Prayer Time', icon: 'time' },
    { id: 'achievement_unlock', name: 'Achievement', icon: 'trophy' },
    { id: 'difficulty_facing', name: 'Need Help', icon: 'help-circle' },
    { id: 'motivation_needed', name: 'Motivation', icon: 'heart' }
  ];

  useEffect(() => {
    loadIntegratedGuidance();
  }, []);

  const getAuthHeaders = async () => {
    const token = await AsyncStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  const loadIntegratedGuidance = async (context: string = currentContext) => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${API_BASE}/integrated-guidance/${context}?available_time_minutes=${availableTime}`,
        { headers }
      );
      const data = await response.json();

      setIntegratedGuidance(data.integrated_guidance);
      setQuranicReference(data.quranic_reference);
    } catch (error) {
      console.error('Error loading integrated guidance:', error);
      Alert.alert('Error', 'Failed to load guidance');
    } finally {
      setLoading(false);
    }
  };

  const loadScholarGuidance = async (scholarName: string) => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${API_BASE}/scholar-guidance/${scholarName}`,
        { headers }
      );
      const data = await response.json();
      setScholarGuidance(data.scholar_guidance);
    } catch (error) {
      console.error('Error loading scholar guidance:', error);
      Alert.alert('Error', 'Failed to load scholar guidance');
    } finally {
      setLoading(false);
    }
  };

  const loadSmartDailyGuidance = async () => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${API_BASE}/smart-daily-guidance?time_of_day=${timeOfDay}&available_time_minutes=${availableTime}`,
        { headers }
      );
      const data = await response.json();
      setDailyGuidance(data.smart_daily_guidance);
    } catch (error) {
      console.error('Error loading daily guidance:', error);
      Alert.alert('Error', 'Failed to load daily guidance');
    } finally {
      setLoading(false);
    }
  };

  const loadContextualVideos = async () => {
    setLoading(true);
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${API_BASE}/contextual-video-recommendations?lesson_context=current_lesson`,
        { headers }
      );
      const data = await response.json();
      setContextualVideos(data.contextual_recommendations.enhanced_video_recommendations);
    } catch (error) {
      console.error('Error loading contextual videos:', error);
      Alert.alert('Error', 'Failed to load video recommendations');
    } finally {
      setLoading(false);
    }
  };

  const openVideoModal = (video: PeaceTVVideo) => {
    setSelectedVideo(video);
    setVideoModalVisible(true);
  };

  const trackLearningSession = async () => {
    try {
      const headers = await getAuthHeaders();
      const sessionData = {
        ustaz_guidance_used: true,
        videos_watched: ['sample_video_1'],
        guidance_context: currentContext,
        session_duration_minutes: 25,
        learning_goals_achieved: ['understood_guidance', 'watched_video']
      };

      const response = await fetch(`${API_BASE}/track-integrated-learning-session`, {
        method: 'POST',
        headers,
        body: JSON.stringify(sessionData)
      });

      const data = await response.json();
      Alert.alert(
        'Session Complete!', 
        `You earned ${data.session_tracking.total_xp_earned} XP!`
      );
    } catch (error) {
      console.error('Error tracking session:', error);
    }
  };

  const renderQuranicReference = () => {
    if (!quranicReference) return null;

    return (
      <View style={styles.quranicCard}>
        <View style={styles.quranicHeader}>
          <Ionicons name="book" size={24} color="#2E7D32" />
          <Text style={styles.quranicTitle}>Quranic Guidance</Text>
        </View>
        
        <Text style={styles.quranicReference}>
          {quranicReference.reference}
        </Text>
        
        <Text style={styles.surahName}>
          {quranicReference.surah.name_english} ({quranicReference.surah.name_arabic})
        </Text>
        
        <Text style={styles.arabicText}>
          {quranicReference.ayat.arabic_text}
        </Text>
        
        <Text style={styles.translation}>
          "{quranicReference.ayat.english_translation}"
        </Text>
        
        <Text style={styles.contextRelevance}>
          📖 {quranicReference.context_relevance}
        </Text>
        
        {quranicReference.scholarly_note && (
          <Text style={styles.scholarlyNote}>
            🎓 Scholar's Note: {quranicReference.scholarly_note}
          </Text>
        )}
      </View>
    );
  };

  const renderGuidanceTab = () => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* Context Selector */}
      <View style={styles.sectionContainer}>
        <Text style={styles.sectionTitle}>🎯 Choose Your Context</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.contextScroll}>
          {contexts.map((context) => (
            <TouchableOpacity
              key={context.id}
              style={[
                styles.contextChip,
                currentContext === context.id && styles.contextChipActive
              ]}
              onPress={() => {
                setCurrentContext(context.id);
                loadIntegratedGuidance(context.id);
              }}
            >
              <Ionicons
                name={context.icon as any}
                size={20}
                color={currentContext === context.id ? 'white' : '#2E7D32'}
              />
              <Text style={[
                styles.contextText,
                currentContext === context.id && styles.contextTextActive
              ]}>
                {context.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#2E7D32" style={styles.loader} />
      ) : (
        <>
          {/* Quranic Reference */}
          {renderQuranicReference()}

          {/* AI Ustaz Guidance */}
          {integratedGuidance && (
            <View style={styles.guidanceCard}>
              <View style={styles.guidanceHeader}>
                <Ionicons name="person" size={24} color="#2E7D32" />
                <Text style={styles.guidanceTitle}>
                  {integratedGuidance.ustaz_guidance.persona === 'ustazah' ? 'Ustazah Aisha' : 'Ustaz Ahmad'}
                </Text>
              </View>
              
              <Text style={styles.mainMessage}>
                {integratedGuidance.ustaz_guidance.main_message}
              </Text>
              
              <View style={styles.adviceSection}>
                <Text style={styles.adviceTitle}>🎯 Practical Advice:</Text>
                <Text style={styles.adviceText}>
                  {integratedGuidance.ustaz_guidance.practical_advice}
                </Text>
              </View>
              
              <View style={styles.encouragementSection}>
                <Text style={styles.encouragementTitle}>💝 Encouragement:</Text>
                <Text style={styles.encouragementText}>
                  {integratedGuidance.ustaz_guidance.encouragement}
                </Text>
              </View>

              {/* Learning Path */}
              <View style={styles.pathSection}>
                <Text style={styles.pathTitle}>🛤️ Your Learning Path:</Text>
                {integratedGuidance.learning_path.map((step, index) => (
                  <View key={index} style={styles.pathStep}>
                    <Text style={styles.stepNumber}>{index + 1}</Text>
                    <Text style={styles.stepText}>{step}</Text>
                  </View>
                ))}
              </View>

              {/* Islamic Benefits */}
              <View style={styles.benefitsSection}>
                <Text style={styles.benefitsTitle}>🌟 Islamic Benefits:</Text>
                {integratedGuidance.islamic_benefits.map((benefit, index) => (
                  <Text key={index} style={styles.benefitText}>• {benefit}</Text>
                ))}
              </View>

              {/* Duas */}
              <View style={styles.duasSection}>
                <Text style={styles.duasTitle}>🤲 Recommended Dua:</Text>
                <Text style={styles.duasText}>{integratedGuidance.duas_for_context}</Text>
              </View>

              {/* Study Time */}
              <View style={styles.timeSection}>
                <Ionicons name="time" size={20} color="#2E7D32" />
                <Text style={styles.timeText}>
                  Estimated Study Time: {integratedGuidance.estimated_study_time_minutes} minutes
                </Text>
              </View>
            </View>
          )}

          {/* Peace TV Recommendations */}
          {integratedGuidance?.peace_tv_recommendations && integratedGuidance.peace_tv_recommendations.length > 0 && (
            <View style={styles.videosSection}>
              <Text style={styles.videosSectionTitle}>📺 Recommended Peace TV Videos</Text>
              {integratedGuidance.peace_tv_recommendations.map((video, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.videoCard}
                  onPress={() => openVideoModal(video)}
                >
                  <Image source={{ uri: video.thumbnail_url }} style={styles.videoThumbnail} />
                  <View style={styles.videoInfo}>
                    <Text style={styles.videoTitle} numberOfLines={2}>{video.title}</Text>
                    <Text style={styles.videoScholar}>{video.scholar.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Text>
                    <Text style={styles.videoDuration}>{video.duration_minutes} minutes</Text>
                    {video.relevance_reason && (
                      <Text style={styles.relevanceReason}>💡 {video.relevance_reason}</Text>
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}

          {/* Track Session Button */}
          <TouchableOpacity style={styles.trackButton} onPress={trackLearningSession}>
            <Ionicons name="analytics" size={20} color="white" />
            <Text style={styles.trackButtonText}>Complete Learning Session</Text>
          </TouchableOpacity>
        </>
      )}
    </ScrollView>
  );

  const renderScholarTab = () => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.sectionTitle}>👨‍🏫 Choose Your Scholar</Text>
      
      {scholars.map((scholar) => (
        <TouchableOpacity
          key={scholar.id}
          style={[
            styles.scholarCard,
            selectedScholar === scholar.id && styles.scholarCardActive
          ]}
          onPress={() => {
            setSelectedScholar(scholar.id);
            loadScholarGuidance(scholar.id);
          }}
        >
          <View style={styles.scholarInfo}>
            <Text style={styles.scholarName}>{scholar.name}</Text>
            <Text style={styles.scholarExpertise}>Expertise: {scholar.expertise}</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#2E7D32" />
        </TouchableOpacity>
      ))}

      {loading && <ActivityIndicator size="large" color="#2E7D32" style={styles.loader} />}

      {scholarGuidance && (
        <View style={styles.scholarGuidanceCard}>
          <Text style={styles.scholarGuidanceTitle}>
            🎓 Guidance from {scholarGuidance.scholar.display_name}
          </Text>
          
          <Text style={styles.relevanceScore}>
            📊 Relevance Score: {Math.round(scholarGuidance.scholar.relevance_score * 100)}%
          </Text>
          
          <Text style={styles.whyRecommended}>
            💡 Why Recommended: {scholarGuidance.scholar.why_recommended}
          </Text>
          
          <Text style={styles.suitableLevel}>
            🎯 Suitable for: {scholarGuidance.scholar.suitable_for_level} learners
          </Text>

          {scholarGuidance.learning_outcomes && (
            <View style={styles.outcomesSection}>
              <Text style={styles.outcomesTitle}>🎯 Learning Outcomes:</Text>
              {scholarGuidance.learning_outcomes.map((outcome: string, index: number) => (
                <Text key={index} style={styles.outcomeText}>• {outcome}</Text>
              ))}
            </View>
          )}

          {scholarGuidance.recommended_videos && (
            <View style={styles.scholarVideos}>
              <Text style={styles.scholarVideosTitle}>📺 Recommended Videos:</Text>
              {scholarGuidance.recommended_videos.map((video: any, index: number) => (
                <TouchableOpacity
                  key={index}
                  style={styles.videoCard}
                  onPress={() => openVideoModal(video)}
                >
                  <Image source={{ uri: video.thumbnail_url }} style={styles.videoThumbnail} />
                  <View style={styles.videoInfo}>
                    <Text style={styles.videoTitle} numberOfLines={2}>{video.title}</Text>
                    <Text style={styles.videoDuration}>{video.duration_minutes} minutes</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );

  const renderDailyTab = () => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.sectionTitle}>🌅 Smart Daily Guidance</Text>
      
      {/* Time Preferences */}
      <View style={styles.preferencesSection}>
        <Text style={styles.preferencesTitle}>⏰ When are you studying?</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {['morning', 'afternoon', 'evening', 'night'].map((time) => (
            <TouchableOpacity
              key={time}
              style={[
                styles.timeChip,
                timeOfDay === time && styles.timeChipActive
              ]}
              onPress={() => setTimeOfDay(time)}
            >
              <Text style={[
                styles.timeText,
                timeOfDay === time && styles.timeTextActive
              ]}>
                {time.charAt(0).toUpperCase() + time.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        
        <Text style={styles.preferencesTitle}>⏱️ How much time do you have?</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {[15, 30, 45, 60].map((time) => (
            <TouchableOpacity
              key={time}
              style={[
                styles.timeChip,
                availableTime === time && styles.timeChipActive
              ]}
              onPress={() => setAvailableTime(time)}
            >
              <Text style={[
                styles.timeText,
                availableTime === time && styles.timeTextActive
              ]}>
                {time} min
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        
        <TouchableOpacity style={styles.loadDailyButton} onPress={loadSmartDailyGuidance}>
          <Text style={styles.loadDailyButtonText}>Get My Daily Guidance</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#2E7D32" style={styles.loader} />}

      {dailyGuidance && (
        <View style={styles.dailyGuidanceCard}>
          <Text style={styles.dailyTitle}>🌟 Your Optimized Daily Session</Text>
          
          <View style={styles.timeOptimization}>
            <Text style={styles.optimizationTitle}>⏰ Time Optimization:</Text>
            <Text style={styles.optimizationText}>
              Perfect for {timeOfDay} study • {availableTime} minutes available
            </Text>
          </View>

          <View style={styles.ustazMessage}>
            <Text style={styles.ustazMessageTitle}>👨‍🏫 Daily Message:</Text>
            <Text style={styles.ustazMessageText}>
              {dailyGuidance.ustaz_guidance.main_message}
            </Text>
          </View>

          <View style={styles.dailyPath}>
            <Text style={styles.dailyPathTitle}>🛤️ Optimized Learning Path:</Text>
            {dailyGuidance.optimized_learning_path.map((step: string, index: number) => (
              <View key={index} style={styles.pathStep}>
                <Text style={styles.stepNumber}>{index + 1}</Text>
                <Text style={styles.stepText}>{step}</Text>
              </View>
            ))}
          </View>

          <View style={styles.dailyDuas}>
            <Text style={styles.dailyDuasTitle}>🤲 Daily Duas:</Text>
            <Text style={styles.dailyDuasText}>{dailyGuidance.daily_duas}</Text>
          </View>

          {dailyGuidance.daily_peace_tv_recommendations && (
            <View style={styles.dailyVideos}>
              <Text style={styles.dailyVideosTitle}>📺 Today's Recommended Videos:</Text>
              {dailyGuidance.daily_peace_tv_recommendations.map((video: any, index: number) => (
                <TouchableOpacity
                  key={index}
                  style={styles.videoCard}
                  onPress={() => openVideoModal(video)}
                >
                  <Image source={{ uri: video.thumbnail_url }} style={styles.videoThumbnail} />
                  <View style={styles.videoInfo}>
                    <Text style={styles.videoTitle} numberOfLines={2}>{video.title}</Text>
                    <Text style={styles.videoScholar}>{video.scholar.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Text>
                    <Text style={styles.videoDuration}>{video.duration_minutes} minutes</Text>
                    {video.why_recommended_now && (
                      <Text style={styles.recommendationReason}>💡 {video.why_recommended_now}</Text>
                    )}
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );

  const renderVideosTab = () => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>🎬 Contextual Video Recommendations</Text>
        <TouchableOpacity style={styles.refreshButton} onPress={loadContextualVideos}>
          <Ionicons name="refresh" size={20} color="#2E7D32" />
          <Text style={styles.refreshText}>Refresh</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#2E7D32" style={styles.loader} />}

      {contextualVideos.length > 0 ? (
        <FlatList
          data={contextualVideos}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.enhancedVideoCard}
              onPress={() => openVideoModal(item.video)}
            >
              <Image source={{ uri: item.video.thumbnail_url }} style={styles.videoThumbnail} />
              <View style={styles.videoInfo}>
                <Text style={styles.videoTitle} numberOfLines={2}>{item.video.title}</Text>
                <Text style={styles.videoScholar}>
                  {item.video.scholar.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Text>
                <Text style={styles.videoDuration}>{item.video.duration_minutes} minutes</Text>
                
                {item.ai_insights && (
                  <View style={styles.aiInsights}>
                    <Text style={styles.insightsTitle}>🤖 AI Insights:</Text>
                    <Text style={styles.relevanceScore}>
                      📊 Relevance: {Math.round(item.ai_insights.relevance_score * 100)}%
                    </Text>
                    <Text style={styles.whyRecommended}>
                      💡 {item.ai_insights.why_recommended}
                    </Text>
                    <Text style={styles.estimatedBenefit}>
                      🎯 {item.ai_insights.estimated_benefit}
                    </Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          )}
          showsVerticalScrollIndicator={false}
        />
      ) : (
        <View style={styles.emptyState}>
          <Ionicons name="tv" size={48} color="#ddd" />
          <Text style={styles.emptyText}>No video recommendations yet</Text>
          <Text style={styles.emptySubtext}>Tap refresh to load contextual recommendations</Text>
        </View>
      )}
    </ScrollView>
  );

  const renderVideoModal = () => (
    <Modal
      visible={videoModalVisible}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => setVideoModalVisible(false)}
          >
            <Ionicons name="close" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Video Details</Text>
        </View>
        
        {selectedVideo && (
          <ScrollView style={styles.modalContent}>
            <Image source={{ uri: selectedVideo.thumbnail_url }} style={styles.modalThumbnail} />
            
            <View style={styles.modalVideoInfo}>
              <Text style={styles.modalVideoTitle}>{selectedVideo.title}</Text>
              <Text style={styles.modalScholar}>
                {selectedVideo.scholar.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Text>
              <Text style={styles.modalDescription}>{selectedVideo.description}</Text>
              
              <View style={styles.modalMeta}>
                <View style={styles.metaItem}>
                  <Ionicons name="time" size={16} color="#666" />
                  <Text style={styles.metaText}>{selectedVideo.duration_minutes} minutes</Text>
                </View>
              </View>
              
              <TouchableOpacity
                style={styles.watchButton}
                onPress={() => {
                  // Implement video watching logic
                  Alert.alert('Watch Video', 'Video player would open here');
                  setVideoModalVisible(false);
                }}
              >
                <Ionicons name="play" size={20} color="white" />
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
          <Ionicons name="person-circle" size={40} color="#2E7D32" />
          <View>
            <Text style={styles.headerTitle}>AI Islamic Assistant</Text>
            <Text style={styles.headerSubtitle}>Your Personal Ustaz/Ustazah</Text>
          </View>
        </View>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {[
          { key: 'guidance', icon: 'book', label: 'Guidance' },
          { key: 'scholar', icon: 'school', label: 'Scholars' },
          { key: 'daily', icon: 'sunny', label: 'Daily' },
          { key: 'videos', icon: 'tv', label: 'Videos' }
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[styles.tab, activeTab === tab.key && styles.activeTab]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Ionicons 
              name={tab.icon as any} 
              size={20} 
              color={activeTab === tab.key ? '#2E7D32' : '#666'} 
            />
            <Text style={[styles.tabText, activeTab === tab.key && styles.activeTabText]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Content */}
      {activeTab === 'guidance' && renderGuidanceTab()}
      {activeTab === 'scholar' && renderScholarTab()}
      {activeTab === 'daily' && renderDailyTab()}
      {activeTab === 'videos' && renderVideosTab()}

      {/* Video Modal */}
      {renderVideoModal()}

      {/* Islamic Compliance Note */}
      <View style={styles.complianceNote}>
        <Ionicons name="shield-checkmark" size={16} color="#2E7D32" />
        <Text style={styles.complianceText}>
          All guidance is based on authentic Islamic sources ✓
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
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 12,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginLeft: 12,
  },
  tabContainer: {
    backgroundColor: 'white',
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  tab: {
    flex: 1,
    flexDirection: 'column',
    alignItems: 'center',
    paddingVertical: 12,
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#2E7D32',
  },
  tabText: {
    marginTop: 4,
    fontSize: 12,
    color: '#666',
  },
  activeTabText: {
    color: '#2E7D32',
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
    padding: 16,
  },
  sectionContainer: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  refreshButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f8f0',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  refreshText: {
    marginLeft: 4,
    color: '#2E7D32',
    fontSize: 12,
  },
  contextScroll: {
    marginBottom: 10,
  },
  contextChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#2E7D32',
  },
  contextChipActive: {
    backgroundColor: '#2E7D32',
  },
  contextText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#2E7D32',
  },
  contextTextActive: {
    color: 'white',
  },
  loader: {
    marginVertical: 30,
  },
  quranicCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderLeftWidth: 4,
    borderLeftColor: '#2E7D32',
  },
  quranicHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  quranicTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginLeft: 8,
  },
  quranicReference: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  surahName: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  arabicText: {
    fontSize: 20,
    textAlign: 'right',
    fontFamily: 'Arial',
    color: '#2E7D32',
    marginBottom: 8,
    lineHeight: 32,
  },
  translation: {
    fontSize: 16,
    fontStyle: 'italic',
    color: '#333',
    marginBottom: 12,
    lineHeight: 24,
  },
  contextRelevance: {
    fontSize: 14,
    color: '#666',
    backgroundColor: '#f0f8f0',
    padding: 8,
    borderRadius: 6,
    marginBottom: 8,
  },
  scholarlyNote: {
    fontSize: 12,
    color: '#888',
    fontStyle: 'italic',
  },
  guidanceCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  guidanceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  guidanceTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginLeft: 8,
  },
  mainMessage: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
    marginBottom: 16,
  },
  adviceSection: {
    marginBottom: 12,
  },
  adviceTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 4,
  },
  adviceText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  encouragementSection: {
    marginBottom: 12,
  },
  encouragementTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 4,
  },
  encouragementText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  pathSection: {
    marginBottom: 12,
  },
  pathTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  pathStep: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
  },
  stepNumber: {
    backgroundColor: '#2E7D32',
    color: 'white',
    width: 20,
    height: 20,
    borderRadius: 10,
    textAlign: 'center',
    fontSize: 12,
    fontWeight: 'bold',
    marginRight: 8,
    lineHeight: 20,
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  benefitsSection: {
    marginBottom: 12,
  },
  benefitsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  benefitText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  duasSection: {
    marginBottom: 12,
    backgroundColor: '#f0f8f0',
    padding: 12,
    borderRadius: 8,
  },
  duasTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 6,
  },
  duasText: {
    fontSize: 14,
    color: '#333',
    fontStyle: 'italic',
    textAlign: 'right',
    lineHeight: 20,
  },
  timeSection: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
    padding: 8,
    borderRadius: 6,
  },
  timeText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#666',
  },
  videosSection: {
    marginBottom: 16,
  },
  videosSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  videoCard: {
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
  enhancedVideoCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  videoThumbnail: {
    width: 120,
    height: 90,
    borderTopLeftRadius: 12,
    borderBottomLeftRadius: 12,
  },
  videoInfo: {
    flex: 1,
    padding: 12,
  },
  videoTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  videoScholar: {
    fontSize: 12,
    color: '#2E7D32',
    marginBottom: 4,
  },
  videoDuration: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  relevanceReason: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
  recommendationReason: {
    fontSize: 12,
    color: '#2E7D32',
    fontStyle: 'italic',
  },
  aiInsights: {
    backgroundColor: '#f0f8f0',
    padding: 8,
    borderRadius: 6,
    marginTop: 8,
  },
  insightsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 4,
  },
  relevanceScore: {
    fontSize: 11,
    color: '#666',
    marginBottom: 2,
  },
  whyRecommended: {
    fontSize: 11,
    color: '#666',
    marginBottom: 2,
  },
  estimatedBenefit: {
    fontSize: 11,
    color: '#666',
  },
  trackButton: {
    backgroundColor: '#2E7D32',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 20,
    marginBottom: 30,
  },
  trackButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
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
  scholarCardActive: {
    borderWidth: 2,
    borderColor: '#2E7D32',
  },
  scholarInfo: {
    flex: 1,
  },
  scholarName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  scholarExpertise: {
    fontSize: 12,
    color: '#666',
  },
  scholarGuidanceCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginTop: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scholarGuidanceTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 12,
  },
  suitableLevel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  outcomesSection: {
    marginTop: 12,
  },
  outcomesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 6,
  },
  outcomeText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  scholarVideos: {
    marginTop: 16,
  },
  scholarVideosTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  preferencesSection: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  preferencesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 8,
  },
  timeChip: {
    backgroundColor: '#f0f8f0',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#2E7D32',
  },
  timeChipActive: {
    backgroundColor: '#2E7D32',
  },
  timeTextActive: {
    color: 'white',
  },
  loadDailyButton: {
    backgroundColor: '#2E7D32',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  loadDailyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  dailyGuidanceCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dailyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 16,
  },
  timeOptimization: {
    backgroundColor: '#f0f8f0',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  optimizationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 4,
  },
  optimizationText: {
    fontSize: 14,
    color: '#666',
  },
  ustazMessage: {
    marginBottom: 16,
  },
  ustazMessageTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 6,
  },
  ustazMessageText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  dailyPath: {
    marginBottom: 16,
  },
  dailyPathTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  dailyDuas: {
    backgroundColor: '#f0f8f0',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  dailyDuasTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 6,
  },
  dailyDuasText: {
    fontSize: 14,
    color: '#333',
    fontStyle: 'italic',
    lineHeight: 20,
  },
  dailyVideos: {
    marginTop: 8,
  },
  dailyVideosTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
    marginBottom: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
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
    color: '#2E7D32',
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
    marginBottom: 20,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
  },
  metaText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#666',
  },
  watchButton: {
    backgroundColor: '#2E7D32',
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
    color: '#2E7D32',
  },
});
