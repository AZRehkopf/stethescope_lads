#This is the class definition for peak_detector 
import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
import time

class peakDetector:
    #Class Variables, customized to sampling frequency of ESP
    fs= 2000 #Sampling frequency
    T=1/fs #Sampling Period #arduino board 0.00025
    mult= int(fs/250)
    lowcut_filter= 0.00001 #lower cutoff for bandpass
    highcut_filter= 15.0 #higher cutoff for bandpass
    filter_order= 1 #filter order for bandpass
    integration_window= 15*mult #size of integration window, changed proportionally to sampling frequency  #arduino 240, was 60 before
    findpeaks_limit= 3000 #Change this according to amplitude of integrated ecg, 0.005 for ecg board #arduino 2800
    # findpeaks_upper_limit= 000 #adjust this according to amplitude of integrated ecg data
    findpeaks_spacing= 50*mult #changed proportionally to sampling freq #arduino 800
    refractory_period= 120*mult #Change proportionally to sampling freq 480*4 period
    threshold_value= 0.0
    noise_peak_value=0.0
    qrs_peak_filtering_factor=0.125
    noise_peak_filtering_factor=0.125
    qrs_peak_value= 0.0
    qrs_noise_diff_weight = 0.25

    def __init__(self):
        #Detection results stored here
        self.qrs_peaks_indices = np.array([], dtype=int)
        self.noise_peaks_indices = np.array([], dtype=int)
        self.last_qrs_index= 0
        self.packet_flag= 0 #This flag is set to 0, when new packet is being analyzed
        self.empty_packet_count= 1 #set it as 1 here for computation purposes

    def bandpass_filter(self, data, lowcut, highcut, signal_freq, filter_order):
        """
        Method responsible for creating and applying Butterworth filter.
        :param deque data: raw data
        :param float lowcut: filter lowcut frequency value
        :param float highcut: filter highcut frequency value
        :param int signal_freq: signal frequency in samples per second (Hz)
        :param int filter_order: filter order
        :return array: filtered data
        """
        nyquist_freq = 0.5 * signal_freq
        low = lowcut / nyquist_freq
        high = highcut / nyquist_freq
        b, a = butter(filter_order, [low, high], btype="band")
        y = lfilter(b, a, data)
        return y

    def findpeaks(self, data, spacing=1, limit=None, upper_limit=None):
        """
        Janko Slavic peak detection algorithm and implementation.
        https://github.com/jankoslavic/py-tools/tree/master/findpeaks
        Finds peaks in `data` which are of `spacing` width and >=`limit`.
        :param ndarray data: data
        :param float spacing: minimum spacing to the next peak (should be 1 or more)
        :param float limit: peaks should have value greater or equal
        :return array: detected peaks indexes array
        """
        length = data.size
        x = np.zeros(length + 2 * spacing)
        x[:spacing] = data[0] - 1.e-6
        x[-spacing:] = data[-1] - 1.e-6
        x[spacing:spacing + length] = data
        peak_candidate = np.zeros(length)
        peak_candidate[:] = True
        for s in range(spacing):
            start = spacing - s - 1
            h_b = x[start: start + length]  # before
            start = spacing
            h_c = x[start: start + length]  # central
            start = spacing + s + 1
            h_a = x[start: start + length]  # after
            peak_candidate = np.logical_and(peak_candidate, np.logical_and(h_c > h_b, h_c > h_a))

        ind = np.argwhere(peak_candidate)
        ind = ind.reshape(ind.size)

        if limit is not None:
            ind= ind[data[ind]> limit]
        return ind


    def detectPeaks(self,ecg):
        
        packet_size= len(ecg) 

        #Bandpass filter the raw ecg data
        filtered_ecg_measurements= self.bandpass_filter(ecg, self.lowcut_filter, self.highcut_filter, self.fs, self.filter_order)
        filtered_ecg_measurements[:100] = filtered_ecg_measurements[100] #this depends on sampling rate!!!!!!! #arduino 100
            
        #Taking the derivative to provide QRS Slope info
        differentiated_ecg_measurements = np.ediff1d(filtered_ecg_measurements)

        #Squaring to intensify measurements
        squared_ecg_measurements = differentiated_ecg_measurements ** 2

        #Moving window integration
        integrated_ecg_measurements = np.convolve(squared_ecg_measurements, np.ones(self.integration_window))
        
        #Fudicial mark whatever that means
        detected_peaks_indices = self.findpeaks(data=integrated_ecg_measurements,limit=self.findpeaks_limit,spacing=self.findpeaks_spacing, upper_limit=None)

        detected_peaks_values = integrated_ecg_measurements[detected_peaks_indices]
        # print("New Packet!")

        # plt.plot()
        # plt.plot(integrated_ecg_measurements)
        # plt.show()
        
        for detected_peak_index, detected_peaks_value in zip(detected_peaks_indices, detected_peaks_values):

            # try:
            #     last_qrs_index = self.qrs_peaks_indices_old[-1]
            # except IndexError:
            #     last_qrs_index = 0
            
            
            # print("Detected peak index %d" %detected_peak_index)
            if(self.packet_flag == 1):
                detected_peak_index= detected_peak_index + (packet_size*self.empty_packet_count)
                # self.last_qrs_index= self.last_qrs_index + (packet_size * (self.packet_count-1))
                # print("New detected peak %d" %detected_peak_index)
                # print("New last qrs %d"  %self.last_qrs_index)
                
            # print("last index %d" % self.last_qrs_index)
                
            

            # print("Difference Val: %d" %(detected_peak_index- self.last_qrs_index))
            # After a valid QRS complex detection, there is a 200 ms refractory period before next one can be detected.
            if ((detected_peak_index - self.last_qrs_index) > self.refractory_period): #or not self.qrs_peaks_indices.size:
                
                pk_difference= detected_peak_index - self.last_qrs_index
                
                if(self.packet_flag == 1):
                    detected_peak_index= detected_peak_index -(packet_size*self.empty_packet_count)
                    # self.last_qrs_index= self.last_qrs_index - (packet_size * (self.packet_count-1))
                    self.packet_flag= 0

                # Peak must be classified either as a noise peak or a QRS peak.
                # To be classified as a QRS peak it must exceed dynamically set threshold value.
                if detected_peaks_value > self.threshold_value:
                    self.qrs_peaks_indices= np.append(self.qrs_peaks_indices, detected_peak_index)
                    # print("ADDED %d" %detected_peak_index)

                    # hr= self.heartRate_RT(pk_difference)
                    # print("THE HEARTRATE IS %F" %hr)

                    self.last_qrs_index= detected_peak_index
                    
                    # Adjust QRS peak value used later for setting QRS-noise threshold.
                    self.qrs_peak_value = self.qrs_peak_filtering_factor * detected_peaks_value + \
                                (1 - self.qrs_peak_filtering_factor) * self.qrs_peak_value

                else:
                    self.noise_peaks_indices = np.append(self.noise_peaks_indices, detected_peak_index)

                    # Adjust noise peak value used later for setting QRS-noise threshold.
                    self.noise_peak_value = self.noise_peak_filtering_factor * detected_peaks_value + \
                                            (1 - self.noise_peak_filtering_factor) * self.noise_peak_value

                    self.packet_flag= 1

                # Adjust QRS-noise threshold value based on previously detected QRS or noise peaks value.
                self.threshold_value = self.noise_peak_value + \
                                        self.qrs_noise_diff_weight * (self.qrs_peak_value - self.noise_peak_value)
                # print(self.threshold_value)
        
        self.packet_flag= 1 #indicate that new packet of data will be analyzed
        

        # Create array containing both input ECG measurements data and QRS detection indication column.
        # We mark QRS detection with '1' flag in 'qrs_detected' log column ('0' otherwise).
        measurement_qrs_detection_flag = np.zeros([len(ecg), 1])
        
        #Keep track of empty packets
        if(len(self.qrs_peaks_indices) == 0):
            self.empty_packet_count += 1

        else:
            self.empty_packet_count= 1


        measurement_qrs_detection_flag[self.qrs_peaks_indices] = 3000 #adjust to make visible when plotting agains ecg data
        self.qrs_peaks_indices= np.array([], dtype=int)
        
        pks_indices= np.where(measurement_qrs_detection_flag == 3000)[0] #returns tuple, extract first array in tuple

        #Average HR calculation
        rate= self.heartRate(pks_indices)

        return pks_indices, rate

    def heartRate_RT(self, pk_difference):

        rate= 60/(self.T * pk_difference)

        return rate

    def heartRate(self, qrs_locations):
        rate_sum=0
        ave_rate=0
        num_peaks= qrs_locations.size

        if (qrs_locations.size > 1):

            for i in range(num_peaks-1):

                rate_sum += 60/(self.T* (qrs_locations[i+1]-qrs_locations[i]))

            ave_rate= rate_sum/(num_peaks-1)
        
        return ave_rate





def main():
    pk_detector= peakDetector() 

    csvfile= open('raw_ecg_data_6K_2.csv') #open the csv file, replace by incoming BT data

    csvreader= csv.reader(csvfile, delimiter= ',')

    # csvfile= open('lead1.csv') #open the csv file

    # csvreader= csv.reader(csvfile, delimiter= ',')

    # array=[]
    # times=[]
    ecg= []

    # for i in csvreader:
    #     array.append(i[0])

    # for i in array:
    #     temp= i.split('\t')
    #     times.append(float(temp[0]))
    #     ecg.append(float(temp[1]))
    # ecg=[]
    indices_peaks=[]


    ecg=[]
    for i in csvreader:
        for j in i:
            ecg.append(int(j))
    
   
    # for i in csvreader:
    #     ecg.append(float(i[0]))

    # start= time.time()
    # for i in range(10):
    #     ecg_data= ecg[i*5000: i*5000+ 5000]
    #     print(len(ecg_data))
    #     peaks= pk_detector.detectPeaks(ecg_data)
        
    #     for i in peaks:
    #         indices_peaks.append(i)
    
    indices_peaks, rate= pk_detector.detectPeaks(ecg)
    print(indices_peaks.size)
    # end= time.time()

    # print("Elapsed time: %f" %(end-start))

    # plt.plot(indices_peaks)
    # plt.plot(ecg)
    # plt.show()




if __name__ == "__main__":
    main()


