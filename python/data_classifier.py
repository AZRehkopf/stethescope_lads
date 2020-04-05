# data_classifier.py
# Process and classify data

### Imports ###

# Built-ins
import logging
import threading
from time import sleep
from joblib import load

# Third party imports
import bluetooth
import numpy as np
from scipy import signal,stats
from sklearn import preprocessing
import pywt
import sklearn.svm as svm


# For testing
import matplotlib.pyplot as plt
import matplotlib
import csv
# matplotlib.use('agg') # for plotting...
import scipy.io as sio

#peak detector/heart rate calculator
import peak_detect_class_RT as pk

### Globals ###
LOGGER = logging.getLogger("classifier")

class DataClassifier():
    def __init__(self, controller):
        self.controller = controller

        # Feature parameters
        self.num_divs = 3
        self.dwt_lvls = 5
        self.wav_name = 'db2'
        
        # Filter specs
        fc_hp = 20 
        fc_lp = 600
        filt_order = 12
        FS = 2000
        self.coeffs_hp = signal.butter(filt_order,fc_hp,btype='highpass',fs=FS,output='sos')
        self.coeffs_lp = signal.butter(filt_order,fc_lp,btype='lowpass',fs=FS,output='sos')

        # Load classifier
        classifier_path = \
            '/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/physio_net/e_files_labels/_out_2020-03-31--23_59_48_clf.joblib'
        self.clf = load(classifier_path) 
        print('Classifier loaded')

        # For test (plotting 'real-time')
        self.itr = 0

        #pk detector
        self.pk_detector= pk.peakDetector()

        
    def find_packet(self):
        # While in receiving state look for new raw packet
        while self.controller.receive_data:
            if self.controller.mic_data_slow != None:
                LOGGER.info("find_packet (DataClassifier) recieved packet.")
                # Spawn thread to handle new packet
                handler = threading.Thread(target=self.data_stream, args=(self.controller.mic_data_slow,self.controller.ecg_data_slow))
                handler.start()
                self.controller.mic_data_slow = None 

            sleep(0.2)

    def data_stream(self,raw_mic,raw_ecg):
        
        # Preprocess
        pcg_processed, ecg_processed = self.preprocess(pcg,ecg)

        # Find ECG peaks (Johnny function)
        pk_locs, heart_rate = self.pk_detector.detectPeaks(ecg_processed)
        
        # Extract features
        features = self.extract_features(pcg_processed,pk_locs)

        # Classify
        self.clf.predict(features)
        print(self.clf.predict(features))

        # Update self.controller (prediction and heart rate)
        # ...



    def plotter_fn(self,data):
        # Plot
        dir_name = '/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/test_plot_slow/'
        ax = []
        fig=plt.figure()
        ax.append(fig.add_subplot(1, 1, 1))
        ax[0].plot(data)
        plt.savefig(dir_name+'test'+str(self.itr),bbox_inches='tight',dpi=50)
        plt.close(fig)
        self.itr += 1

    def extract_features(self,pcg_data,peak_locs):
        num_beats = peak_locs.size-1
        features_mat = np.zeros((self.dwt_lvls+1,self.num_divs,num_beats))
        beat_var_mat = np.zeros((num_beats,))
        # Loop through all beats
        for jj in range(num_beats):
            beat = np.copy(pcg_data[peak_locs[jj]:peak_locs[jj+1]])
            beat_var_mat[jj] = np.var(beat) # variance
            # Loop through DWT levels
            for ii in range(self.dwt_lvls):
                (beat,coeff_d) = pywt.dwt(beat,self.wav_name)
                features_mat[ii,:,jj] = self.div_signal(coeff_d)
                if ii == self.dwt_lvls-1:
                    features_mat[ii+1,:,jj] = self.div_signal(beat)

        # Remove beats with high variance
        remove_inds = self.beat_check(beat_var_mat)
        features_mat_clean = features_mat[:,:,remove_inds]

        # Normalize features and reshape
        features_mat_out = np.mean(features_mat_clean,axis=2)
        features_mat_out = preprocessing.scale(np.reshape(features_mat_out,(features_mat_out.size,1)))
        return  np.transpose(features_mat_out)

    def div_signal(self,data_in):
        div_means = np.zeros(self.num_divs)
        div_len = int(np.floor(data_in.size/self.num_divs))
        for i in range(self.num_divs):
            div_means[i] = stats.median_absolute_deviation(data_in[i*div_len:(i+1)*div_len])
        return div_means

    def beat_check(self,var_mat):
        # Find outliers
        quartiles = np.percentile(var_mat,(25,75))
        iqr = quartiles[1] - quartiles[0]
        low_cutoff = quartiles[0]-iqr*1.5 
        up_cutoff = quartiles[1]+iqr*1.5
        outlier_inds = ((low_cutoff <= var_mat) & (var_mat <= up_cutoff))
        return outlier_inds

    def preprocess(self,pcg,ecg):
        # Normalise PCG
        pcg_mean = np.mean(pcg)
        pcg_std = np.std(pcg,ddof=1)
        pcg_norm = (pcg - pcg_mean) / pcg_std
        # Downsample PCG and ECG
        raw_mic_ds = signal.decimate(pcg_norm,2)
        raw_ecg_ds = signal.decimate(ecg,2)
        # Filter PCG
        mic_filt_hp = signal.sosfiltfilt(self.coeffs_hp,raw_mic_ds)
        mic_filt = signal.sosfiltfilt(self.coeffs_lp,mic_filt_hp)
        return mic_filt,raw_ecg_ds



if __name__ == "__main__":

    classifier_ob = DataClassifier('hi')

    # dir_name = '/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/physio_net/all_files_labels/'
    # fname = 'a0076.mat'
    # # # print(dir_name+fname)
    # pcg_load = sio.loadmat(dir_name+fname)['pcg_signal_cut']
    # pcg = pcg_load.reshape((pcg_load.shape[0],))
    # inds_load = sio.loadmat(dir_name+fname)['s1_inds']
    # inds = inds_load.reshape((inds_load.shape[0],))

    # print(pcg)
    # print(inds)
    # print('Data loaded')

    # pcg_1 = np.loadtxt(\
    #     '/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/johnny_files/raw_mic_data_6K_2.csv',\
    #         delimiter=",")
    # ecg = np.loadtxt(\
    #     '/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/johnny_files/raw_ecg_data_6K_2.csv',\
    #         delimiter=",")
    
    csvfile= open('/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/johnny_files/raw_mic_data_6K_2.csv') 
    csvreader= csv.reader(csvfile, delimiter= ',')
    pcg_in= []
    for i in csvreader: #for every line in csv file
        for j in i:
            pcg_in.append(int(j))
    pcg = np.array(pcg_in)

    csvfile= open('/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/johnny_files/raw_ecg_data_6K_2.csv') 
    csvreader= csv.reader(csvfile, delimiter= ',')
    ecg_in= []
    for i in csvreader: #for every line in csv file
        for j in i:
            ecg_in.append(int(j))
    ecg = np.array(ecg_in)

    # print(pcg.shape)
    # print(ecg.shape)


    classifier_ob.data_stream(pcg,ecg)
    # pk_detector= pk.peakDetector()

    # plt.figure()
    # plt.plot(raw_mic)


    # print(pk_locs)
    # print(np.ones(ecg_processed.shape[0]))
    # a = np.ones(ecg_processed.shape[0])
    # a[pk_locs] = 2000
    
    # plt.figure()
    # plt.plot(ecg_processed)
    # plt.plot(np.arange(0,a.shape[0]),a)
    # features_plt = np.reshape(features,(6,3))
    # plt.figure()
    # plt.imshow(features_plt, interpolation= None, cmap='Greys', aspect="auto",
    # extent=[0, 1, 0, len(features_plt)])
    # plt.show()