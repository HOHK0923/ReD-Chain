package com.redchain.agent.modules

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.util.concurrent.TimeUnit

object TrafficGenModule {

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(5, TimeUnit.SECONDS)
        .build()

    suspend fun execute(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val targetUrl = params.getString("target_url")
        val duration = params.getInt("duration")
        val requestsPerSecond = params.getInt("requests_per_second")

        var totalRequests = 0
        var successful = 0
        var failed = 0

        val startTime = System.currentTimeMillis()
        val endTime = startTime + (duration * 1000)

        while (System.currentTimeMillis() < endTime) {
            try {
                val request = Request.Builder()
                    .url(targetUrl)
                    .build()

                val response = client.newCall(request).execute()
                totalRequests++

                if (response.isSuccessful) {
                    successful++
                } else {
                    failed++
                }
                response.close()

            } catch (e: Exception) {
                failed++
                totalRequests++
            }

            delay(1000L / requestsPerSecond)
        }

        JSONObject().apply {
            put("target_url", targetUrl)
            put("total_requests", totalRequests)
            put("successful", successful)
            put("failed", failed)
            put("duration", duration)
        }
    }
}
