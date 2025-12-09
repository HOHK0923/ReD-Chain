package com.redchain.agent

import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.redchain.agent.service.C2Service
import com.redchain.agent.network.C2Client

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var startButton: Button
    private lateinit var stopButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)

        startButton.setOnClickListener {
            startC2Service()
        }

        stopButton.setOnClickListener {
            stopC2Service()
        }

        // Auto start on launch
        if (C2Client.isRegistered(this)) {
            startC2Service()
        }
    }

    private fun startC2Service() {
        val intent = Intent(this, C2Service::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        statusText.text = "Status: Running"
    }

    private fun stopC2Service() {
        val intent = Intent(this, C2Service::class.java)
        stopService(intent)
        statusText.text = "Status: Stopped"
    }
}
