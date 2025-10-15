import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const { width } = Dimensions.get('window');

interface PrayerTime {
  name: string;
  time: string;
  icon: string;
  gradient: string[];
  isNext?: boolean;
  isPassed?: boolean;
}

interface QiblaData {
  qibla_bearing: number;
  accuracy: string;
  calculation_method: string;
}

export default function PrayerScreen() {
  const [loading, setLoading] = useState(true);
  const [locationLoading, setLocationLoading] = useState(false);
  const [prayerTimes, setPrayerTimes] = useState<PrayerTime[]>([]);
  const [qiblaData, setQiblaData] = useState<QiblaData | null>(null);
  const [currentLocation, setCurrentLocation] = useState<{
    latitude: number;
    longitude: number;
    city?: string;
  } | null>(null);
  const [nextPrayer, setNextPrayer] = useState<PrayerTime | null>(null);
  const [timeUntilNext, setTimeUntilNext] = useState<string>('');

  useEffect(() => {
    requestLocationPermission();
  }, []);

  useEffect(() => {
    // Update countdown every minute
    const interval = setInterval(updateCountdown, 60000);
    updateCountdown(); // Initial call
    return () => clearInterval(interval);
  }, [prayerTimes]);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Location permission is needed to calculate accurate prayer times and Qibla direction.');
        // Use default location (Kuala Lumpur, Malaysia)
        loadPrayerTimes(3.139, 101.6869, 'Kuala Lumpur, Malaysia');
        return;
      }

      setLocationLoading(true);
      const location = await Location.getCurrentPositionAsync({});
      const address = await Location.reverseGeocodeAsync({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });

      const city = address[0]?.city || address[0]?.district || 'Unknown Location';
      const locationData = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        city,
      };

      setCurrentLocation(locationData);
      await loadPrayerTimes(location.coords.latitude, location.coords.longitude, city);
      await loadQiblaDirection(location.coords.latitude, location.coords.longitude);
    } catch (error) {
      console.error('Error getting location:', error);
      Alert.alert('Location Error', 'Unable to get your location. Using default location (Kuala Lumpur).');
      loadPrayerTimes(3.139, 101.6869, 'Kuala Lumpur, Malaysia');
    } finally {
      setLocationLoading(false);
    }
  };

  const loadPrayerTimes = async (latitude: number, longitude: number, city: string) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const today = new Date().toISOString().split('T')[0];
      
      const response = await axios.get(
        `${API_URL}/api/prayer-times?latitude=${latitude}&longitude=${longitude}&date=${today}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const data = response.data;
      const now = new Date();
      
      const prayers: PrayerTime[] = [
        {
          name: 'Fajr',
          time: formatTime(new Date(data.fajr)),
          icon: 'moon-outline',
          gradient: ['#1A237E', '#3F51B5'],
        },
        {
          name: 'Sunrise',
          time: formatTime(new Date(data.sunrise)),
          icon: 'sunny-outline',
          gradient: ['#FF6F00', '#FF8F00'],
        },
        {
          name: 'Dhuhr',
          time: formatTime(new Date(data.dhuhr)),
          icon: 'sunny',
          gradient: ['#F57F17', '#FBC02D'],
        },
        {
          name: 'Asr',
          time: formatTime(new Date(data.asr)),
          icon: 'partly-sunny-outline',
          gradient: ['#FF8A00', '#FF6F00'],
        },
        {
          name: 'Maghrib',
          time: formatTime(new Date(data.maghrib)),
          icon: 'moon',
          gradient: ['#D32F2F', '#F44336'],
        },
        {
          name: 'Isha',
          time: formatTime(new Date(data.isha)),
          icon: 'moon',
          gradient: ['#512DA8', '#673AB7'],
        },
      ];

      // Determine next prayer and mark passed prayers
      let nextPrayerFound = false;
      const processedPrayers = prayers.map(prayer => {
        const prayerTime = parseTime(prayer.time);
        const isPassed = prayerTime < now;
        const isNext = !nextPrayerFound && !isPassed;
        
        if (isNext) {
          nextPrayerFound = true;
          setNextPrayer(prayer);
        }

        return {
          ...prayer,
          isPassed,
          isNext,
        };
      });

      // If no next prayer found (after Isha), next is Fajr tomorrow
      if (!nextPrayerFound) {
        processedPrayers[0].isNext = true;
        setNextPrayer(prayers[0]);
      }

      setPrayerTimes(processedPrayers);
    } catch (error) {
      console.error('Error loading prayer times:', error);
      Alert.alert('Error', 'Unable to load prayer times. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadQiblaDirection = async (latitude: number, longitude: number) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const response = await axios.get(
        `${API_URL}/api/qibla-direction?latitude=${latitude}&longitude=${longitude}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setQiblaData(response.data);
    } catch (error) {
      console.error('Error loading Qibla direction:', error);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const parseTime = (timeString: string) => {
    const today = new Date();
    const [time, period] = timeString.split(' ');
    const [hours, minutes] = time.split(':').map(Number);
    const hour24 = period === 'PM' && hours !== 12 ? hours + 12 : 
                   period === 'AM' && hours === 12 ? 0 : hours;
    
    return new Date(today.getFullYear(), today.getMonth(), today.getDate(), hour24, minutes);
  };

  const updateCountdown = () => {
    if (!nextPrayer) return;

    const now = new Date();
    const nextTime = parseTime(nextPrayer.time);
    
    // If next prayer is tomorrow (Fajr after Isha)
    if (nextTime < now) {
      nextTime.setDate(nextTime.getDate() + 1);
    }

    const diff = nextTime.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    setTimeUntilNext(`${hours}h ${minutes}m`);
  };

  const refreshLocation = () => {
    setLoading(true);
    requestLocationPermission();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2E7D32" />
        <Text style={styles.loadingText}>Loading prayer times...</Text>
        {locationLoading && (
          <Text style={styles.locationText}>Getting your location...</Text>
        )}
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Ionicons name="location" size={20} color="#FFF" />
          <Text style={styles.locationText}>{currentLocation?.city || 'Kuala Lumpur'}</Text>
        </View>
        <TouchableOpacity onPress={refreshLocation} style={styles.refreshButton}>
          <Ionicons name="refresh" size={20} color="#FFF" />
        </TouchableOpacity>
      </View>

      {/* Next Prayer Card */}
      {nextPrayer && (
        <LinearGradient
          colors={nextPrayer.gradient}
          style={styles.nextPrayerCard}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <View style={styles.nextPrayerContent}>
            <View style={styles.nextPrayerHeader}>
              <Text style={styles.nextPrayerLabel}>Next Prayer</Text>
              <Text style={styles.timeUntilNext}>{timeUntilNext}</Text>
            </View>
            <View style={styles.nextPrayerInfo}>
              <Ionicons name={nextPrayer.icon as any} size={40} color="#FFF" />
              <View style={styles.nextPrayerText}>
                <Text style={styles.nextPrayerName}>{nextPrayer.name}</Text>
                <Text style={styles.nextPrayerTime}>{nextPrayer.time}</Text>
              </View>
            </View>
          </View>
        </LinearGradient>
      )}

      {/* Prayer Times Grid */}
      <View style={styles.prayerTimesContainer}>
        <Text style={styles.sectionTitle}>Today's Prayer Times</Text>
        <Text style={styles.methodNote}>Calculated using JAKIM method</Text>
        
        <View style={styles.prayerGrid}>
          {prayerTimes.map((prayer, index) => (
            <View key={index} style={[
              styles.prayerCard,
              prayer.isPassed && styles.passedPrayer,
              prayer.isNext && styles.nextPrayerHighlight,
            ]}>
              <LinearGradient
                colors={prayer.isPassed ? ['#E0E0E0', '#BDBDBD'] : prayer.gradient}
                style={styles.prayerCardGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <Ionicons 
                  name={prayer.icon as any} 
                  size={24} 
                  color="#FFF" 
                />
                <Text style={styles.prayerName}>{prayer.name}</Text>
                <Text style={styles.prayerTime}>{prayer.time}</Text>
                {prayer.isNext && (
                  <View style={styles.nextIndicator}>
                    <Text style={styles.nextIndicatorText}>NEXT</Text>
                  </View>
                )}
              </LinearGradient>
            </View>
          ))}
        </View>
      </View>

      {/* Qibla Direction */}
      {qiblaData && (
        <View style={styles.qiblaContainer}>
          <Text style={styles.sectionTitle}>Qibla Direction</Text>
          <View style={styles.qiblaCard}>
            <View style={styles.qiblaContent}>
              <View style={styles.compassContainer}>
                <View style={styles.compass}>
                  <View 
                    style={[
                      styles.qiblaArrow,
                      { transform: [{ rotate: `${qiblaData.qibla_bearing}deg` }] }
                    ]}
                  >
                    <Ionicons name="arrow-up" size={32} color="#FFD700" />
                  </View>
                  <Text style={styles.compassText}>Qibla</Text>
                </View>
              </View>
              <View style={styles.qiblaInfo}>
                <Text style={styles.qiblaBearing}>{qiblaData.qibla_bearing.toFixed(1)}°</Text>
                <Text style={styles.qiblaAccuracy}>Accuracy: {qiblaData.accuracy}</Text>
                <Text style={styles.qiblaMethod}>Method: {qiblaData.calculation_method}</Text>
              </View>
            </View>
          </View>
        </View>
      )}

      {/* Islamic Reminders */}
      <View style={styles.remindersContainer}>
        <Text style={styles.sectionTitle}>Islamic Reminders</Text>
        <View style={styles.reminderCard}>
          <Ionicons name="book" size={24} color="#2E7D32" />
          <View style={styles.reminderText}>
            <Text style={styles.reminderTitle}>Daily Quran Reading</Text>
            <Text style={styles.reminderDescription}>
              "And We have made the Quran easy for remembrance" (54:17)
            </Text>
          </View>
        </View>
        
        <View style={styles.reminderCard}>
          <Ionicons name="heart" size={24} color="#D32F2F" />
          <View style={styles.reminderText}>
            <Text style={styles.reminderTitle}>Dhikr After Prayer</Text>
            <Text style={styles.reminderDescription}>
              Remember Allah 33x: SubhanAllah, Alhamdulillah, Allahu Akbar
            </Text>
          </View>
        </View>
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
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 12,
  },
  header: {
    backgroundColor: '#2E7D32',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  locationText: {
    fontSize: 16,
    color: '#FFF',
    marginLeft: 8,
    fontWeight: '500',
  },
  refreshButton: {
    padding: 8,
  },
  nextPrayerCard: {
    marginHorizontal: 20,
    marginTop: -30,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  nextPrayerContent: {
    padding: 20,
  },
  nextPrayerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  nextPrayerLabel: {
    fontSize: 14,
    color: '#FFF',
    opacity: 0.9,
  },
  timeUntilNext: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: 'bold',
  },
  nextPrayerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nextPrayerText: {
    marginLeft: 16,
  },
  nextPrayerName: {
    fontSize: 24,
    color: '#FFF',
    fontWeight: 'bold',
  },
  nextPrayerTime: {
    fontSize: 18,
    color: '#FFF',
    opacity: 0.9,
    marginTop: 4,
  },
  prayerTimesContainer: {
    marginHorizontal: 20,
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  methodNote: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    fontStyle: 'italic',
  },
  prayerGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  prayerCard: {
    width: (width - 60) / 2,
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden',
  },
  prayerCardGradient: {
    padding: 16,
    alignItems: 'center',
    minHeight: 100,
    justifyContent: 'center',
    position: 'relative',
  },
  prayerName: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: '600',
    marginTop: 8,
  },
  prayerTime: {
    fontSize: 14,
    color: '#FFF',
    opacity: 0.9,
    marginTop: 4,
  },
  passedPrayer: {
    opacity: 0.6,
  },
  nextPrayerHighlight: {
    borderWidth: 2,
    borderColor: '#FFD700',
  },
  nextIndicator: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#FFD700',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  nextIndicatorText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  qiblaContainer: {
    marginHorizontal: 20,
    marginTop: 24,
  },
  qiblaCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  qiblaContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  compassContainer: {
    flex: 1,
    alignItems: 'center',
  },
  compass: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#2E7D32',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  qiblaArrow: {
    position: 'absolute',
  },
  compassText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 24,
  },
  qiblaInfo: {
    flex: 1,
    marginLeft: 20,
  },
  qiblaBearing: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  qiblaAccuracy: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  qiblaMethod: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  remindersContainer: {
    marginHorizontal: 20,
    marginTop: 24,
  },
  reminderCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  reminderText: {
    flex: 1,
    marginLeft: 16,
  },
  reminderTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  reminderDescription: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
    lineHeight: 20,
  },
});
