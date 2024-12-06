package com.example.caraoke_app.model

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaCodec
import android.media.MediaFormat
import android.media.MediaRecorder
import android.util.Log
import java.net.Socket
import java.net.SocketException
import java.nio.ByteBuffer
import kotlin.concurrent.thread

const val TAG = "Audio";
const val RECORDER_SAMPLE_RATE = 44100
const val AUDIO_SOURCE = MediaRecorder.AudioSource.MIC
const val RAW_AUDIO_SOURCE = MediaRecorder.AudioSource.UNPROCESSED
const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
val BUFFER_SIZE_RECORDING =
    2 * AudioRecord.getMinBufferSize(RECORDER_SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)

class Audio() {
    @SuppressLint("MissingPermission")
    var audioRecord: AudioRecord = AudioRecord(AUDIO_SOURCE, RECORDER_SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT, BUFFER_SIZE_RECORDING)
    lateinit var recordingThread: Thread

    val format: MediaFormat = MediaFormat.createAudioFormat(
        MediaFormat.MIMETYPE_AUDIO_FLAC,
        RECORDER_SAMPLE_RATE,
        1
    )

    var runOnSocketClose: Runnable? = null

    @Volatile private var recoring: Boolean = false

    init {
        format.setInteger(MediaFormat.KEY_FLAC_COMPRESSION_LEVEL, 0)
        format.setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, BUFFER_SIZE_RECORDING)
    }

    fun setOnCancel(run: Runnable) {
        runOnSocketClose = run
    }

    @SuppressLint("MissingPermission")
    fun initAudio() {
        audioRecord = AudioRecord(AUDIO_SOURCE, RECORDER_SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT, BUFFER_SIZE_RECORDING)
    }

    fun record(socket: Socket) {
        //First check whether the above object actually initialized
        if (audioRecord.state != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "error initializing AudioRecord");
            return
        }

        //Now start the audio recording
        audioRecord.startRecording()
        recoring = true

        recordingThread = thread(true) {
            val encoder = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_AUDIO_FLAC)
            encoder.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            encoder.start()

            var totalSamplesProcessed = 0
            val bufferInfo = MediaCodec.BufferInfo()

            while (recoring) {
                val inputBufferIndex = encoder.dequeueInputBuffer(10000)
                if (inputBufferIndex >= 0) {
                    val inputBuffer = encoder.getInputBuffer(inputBufferIndex)
                    inputBuffer!!.clear()

                    val readSize = audioRecord.read(inputBuffer, BUFFER_SIZE_RECORDING, AudioRecord.READ_BLOCKING);

                    if (readSize > 0) {
                        val presentationTime = (totalSamplesProcessed * 1000000L) / RECORDER_SAMPLE_RATE;
                        totalSamplesProcessed += readSize / 2
                        encoder.queueInputBuffer(inputBufferIndex, 0, readSize, presentationTime, 0)
                    }

                }

                var outputBufferIndex = encoder.dequeueOutputBuffer(bufferInfo, 10000)
                var socketAlive = true
                while (socketAlive && outputBufferIndex >= 0) {
                    val outputBuffer = encoder.getOutputBuffer(outputBufferIndex)
                    val encodedData = ByteArray(bufferInfo.size)
                    outputBuffer!!.get(encodedData)

                    try {
                        socket.getOutputStream().write(encodedData);
                        socket.getOutputStream().flush();
                    } catch (e: SocketException) {
                        recoring = false
                        socketAlive = false

                        runOnSocketClose?.run()
                    }

                    encoder.releaseOutputBuffer(outputBufferIndex, false)
                    outputBufferIndex = encoder.dequeueOutputBuffer(bufferInfo, 10000)
                }
            }

            encoder.stop()
            encoder.release()
            socket.close()

        }
    }

    fun stopRecord() {
        recoring = false
    }
}