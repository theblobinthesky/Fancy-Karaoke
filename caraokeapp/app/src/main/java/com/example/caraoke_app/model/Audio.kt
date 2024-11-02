package com.example.caraoke_app.model

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlin.concurrent.thread

const val TAG = "Audio";
const val RECORDER_SAMPLE_RATE = 44100
const val AUDIO_SOURCE = MediaRecorder.AudioSource.MIC
const val RAW_AUDIO_SOURCE = MediaRecorder.AudioSource.UNPROCESSED
const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
val BUFFER_SIZE_RECORDING =
    AudioRecord.getMinBufferSize(RECORDER_SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)

class Audio() {
    @SuppressLint("MissingPermission")
    val audioRecord: AudioRecord = AudioRecord(AUDIO_SOURCE, RECORDER_SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT, BUFFER_SIZE_RECORDING)
    lateinit var recordingThread: Thread

    fun record() {
        //First check whether the above object actually initialized
        if (audioRecord.state != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "error initializing AudioRecord");
            return
        }

        //Now start the audio recording
        audioRecord.startRecording()

        /*
        recordingThread = thread(true) {
            writeAudioDataToFile()
        }*/
    }
}