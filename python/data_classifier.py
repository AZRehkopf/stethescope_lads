# data_classifier.py
# Process and classify data

### Imports ###

# Built-ins
import logging
import os
import threading
from time import sleep

# Third party imports
import bluetooth
from joblib import load
import numpy as np
import pywt
from scipy import signal,stats
from sklearn import preprocessing
import sklearn.svm as svm

### Globals ###

LOGGER = logging.getLogger("classifier")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CLASSIFIER_FILE = "_classifier_data.joblib"

### Classes ###

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
        classifier_path = os.path.join(DATA_DIR, CLASSIFIER_FILE)
        self.clf = load(classifier_path) 
        LOGGER.info('Classifier data loaded from file')

        # For test (plotting 'real-time')
        self.itr = 0

        LOGGER.info("Data classifier class initialized")
        
    def data_stream(self, raw_ecg_data, raw_pcg_data):
        # Preprocess
        pcg_processed, ecg_processed = self.preprocess(raw_pcg_data, raw_ecg_data)
        
        # Find ECG peaks (Johnny function)
        self.controller.peak_detector_module.run_peak_detection(raw_ecg_data)
        pk_locs, heart_rate = self.controller.analysis_peak_detector.detectPeaks(ecg_processed)
        
        # Extract features
        features = self.extract_features(pcg_processed,pk_locs)

        # Classify
        classification = self.clf.predict(features)[0]

        if classification == 1.0:
            self.controller.interface.send_heart_sounds_classification(False)
        elif classification == -1.0:
            self.controller.interface.send_heart_sounds_classification(True)
        else:
            LOGGER.error("Classification error, unknown result")

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

    def run_heart_sound_analysis(self, raw_ecg_data, raw_pcg_data):
        LOGGER.info("Starting heart sound analysis")
        self.data_stream(raw_ecg_data, raw_pcg_data)
        LOGGER.info("Heart sound analysis complete")